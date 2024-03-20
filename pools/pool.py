"""
Pool Module
=============

This module defines a framework for managing fantasy sports pools within a league. 
It includes abstract base classes for different types of pools and concrete 
implementations for specific pool types such as weekly, seasonal, and special week pools.
"""

from abc import ABC, abstractmethod
import sys
from utils import DynamoDBUtils
from decimal import Decimal
from stats import *


class Pool(ABC):
    """
    Abstract base class representing a generic pool.
    """

    def __init__(self, pool_id: str, league, payout_pct: Decimal, week: int):
        """
        Initialize a Pool object.

        Args:
            pool_id (str): The unique identifier for the pool.
            league (League): The league object.
            payout_pct (Decimal): The payout percentage.
            week (int): The week of the pool.
        """
        self.pool_id = pool_id
        self.league = league
        self.payout_pct = payout_pct
        self.winners = []
        self.payout_amount = self.set_payout_amount()
        self.week = week
        self.paid = False
        self.label = pool_id.replace("_", " ").title()
        # self.save_to_dynamodb()

    def __str__(self):
        """
        Return a string representation of the Pool object.
        """
        attributes = {
            "pool": self.label,
            "week": self.week,
            "payout": self.payout_amount,
            "winners": self.winners,
            "paid": self.paid,
        }

        attr_string = "\n".join(
            [f"{key}: {value}" for key, value in attributes.items()]
        )
        return attr_string

    def save_to_dynamodb(self):
        """
        Saves the pool data to DynamoDB.
        """
        table = DynamoDBUtils.get_table("pools")

        # Get all instance variables and their values
        pool_attributes = vars(self)

        # Filter out any attributes you don't want to include
        pool_item = {key: value for key, value in pool_attributes.items()}

    def set_winner(self):
        self.winners = self.set_pool_winner()

    @abstractmethod
    def set_pool_winner(self):
        """
        Abstract method to set the winners(s) of the pool.
        """
        pass

    @abstractmethod
    def set_payout_amount(self):
        """
        Abstract method to set the payout amount for the pool.
        """
        pass

    def process_payout(self):
        """
        Processes a payout, sends payment, and loads payout data to a database.

        Returns:
            Payout: The Payout object representing the payout transaction.
        """
        try:
            payout = Payout(self)
            self.paid = True
        except:
            self.paid = False
        return payout

    @classmethod
    def create_pools(cls, league, **kwargs):
        """
        Create pools based on the configuration file.

        Args:
            league (League): The league object.
            **kwargs: Additional keyword arguments to pass to pool constructors.

        Returns:
            List: List of created Pool instances.
        """
        config = league.config

        pools = []
        for pool_type in ["side_pools", "main_pools"]:
            for pool_config in config.get(pool_type, []):
                pool_name = pool_config["pool"]
                payout_pct = pool_config["payout"]
                if "pool_id" in pool_config:
                    kwargs["pool_id"] = pool_config["pool_id"]
                pool_instance = cls.create_pool_instance(
                    league, pool_name, payout_pct, **kwargs
                )
                try:
                    for p in pool_instance:
                        pools.append(p)
                except TypeError:
                    pools.append(pool_instance)

        return pools

    @classmethod
    def create_pool_instance(
        cls, league, pool_name: str, payout_pct: Decimal, **kwargs
    ):
        """
        Create an instance of a specific pool type with the given parameters.

        Args:
            league (League): The league object.
            pool_name (str): The name of the pool type.
            payout_pct (Decimal): The payout percentage.
            **kwargs: Additional parameters specific to the pool type.

        Returns:
            Pool: An instance of the specified pool type.
        """
        pool_class = getattr(sys.modules[__name__], pool_name)
        if pool_class.pool_subtype == "weekly":
            return pool_class.create_pools_for_weeks(league, payout_pct, **kwargs)
        elif pool_class.pool_type == "main":
            return pool_class(league=league, payout_pct=payout_pct)
        else:
            return pool_class(league=league, payout_pct=payout_pct, **kwargs)


class SidePool(Pool, ABC):
    """
    Subclass representing a Side Pool object.
    """

    pool_type = "side"
    pool_subtype = None

    def __init__(self, league, pool_id: str, payout_pct: Decimal, week: int):
        """
        Initialize a SidePool object.

        Args:
            league (League): The league object.
            pool_id (str): The unique identifier for the pool.
            payout_pct (Decimal): The payout percentage.
            week (int): The week of the pool.
        """
        from league import League

        super().__init__(pool_id, league, payout_pct, week)
        self.set_payout_amount()

    def set_payout_amount(self):
        """
        Set the payout amount for the side pool.
        """
        self.payout_amount = round(self.payout_pct * self.league.side_pot, 2)


class MainPool(Pool, ABC):
    """
    Subclass representing a Main Pool object.
    """

    pool_type = "main"  # Static attribute
    pool_subtype = None

    def __init__(self, league, pool_id: str, payout_pct: Decimal, week: int):
        """
        Initialize a MainPool object.

        Args:
            league (League): The league object.
            pool_id (str): The unique identifier for the pool.
            payout_pct (Decimal): The payout percentage.
            week (int): The week of the pool.
        """
        from league import League

        super().__init__(pool_id, league, payout_pct, week)
        self.set_payout_amount()

    def set_payout_amount(self):
        """
        Set the payout amount for the main pool.
        """
        self.payout_amount = round(self.payout_pct * self.league.main_pot, 2)


class SeasonPool(SidePool, ABC):
    """
    Subclass representing a Season Pool object.
    """

    def __init__(self, league, pool_id: str, payout_pct: Decimal, pool_subtype: str):
        """
        Initialize a SeasonPool object.

        Args:
            league (League): The league object.
            pool_id (str): The unique identifier for the pool.
            payout_pct (Decimal): The payout percentage.
            pool_subtype (str): The subtype of the season pool.
        """
        super().__init__(league, pool_id, payout_pct, league.LAST_WEEK)
        self.pool_subtype = pool_subtype

    @abstractmethod
    def get_leaderboard(self):
        """
        Abstract method to get the leaderboard for the season pool.
        """
        pass


class SpecialWeekPool(SidePool, ABC):
    """
    Subclass representing a Special Week Pool object.
    """

    pool_subtype = "special_week"

    def __init__(self, league, pool_id: str, payout_pct: Decimal, week):
        """
        Initialize a SpecialWeekPool object.

        Args:
            league (League): The league object.
            pool_id (str): The unique identifier for the pool.
            payout_pct (Decimal): The payout percentage.
            week (int): The week of the pool.
        """
        super().__init__(league, pool_id, payout_pct, week)

    def set_payout_amount(self):
        """
        Set the payout amount for the side pool.
        """
        self.payout_amount = round(
            (self.payout_pct * self.league.side_pot)
            / (1 if not self.winners else self.winners),
            2,
        )


class WeeklyPool(SidePool, ABC):
    """
    Subclass representing a Weekly Pool object.
    """

    pool_subtype = "weekly"

    def __init__(self, league, pool_id: str, payout_pct: Decimal, week: int):
        """
        Initialize a WeeklyPool object.

        Args:
            league (League): The league object.
            pool_id (str): The unique identifier for the pool.
            payout_pct (Decimal): The payout percentage.
            week (int): The week of the pool.
        """
        super().__init__(league, pool_id, payout_pct, week)

    @classmethod
    def create_pools_for_weeks(cls, league, payout_pct: Decimal):
        """
        Create Pool instances for each week in the list of weeks.

        Args:
            league (League): The league object.
            payout_pct (Decimal): The payout percentage.
            **kwargs: Additional keyword arguments.

        Returns:
            List: List of created Pool instances.
        """
        weeks = league.REGULAR_SEASON
        pools = []
        for week in weeks:
            pool_instance = cls(league, payout_pct, week)
            pools.append(pool_instance)
        return pools


class PropPool(SidePool):
    """
    Subclass representing a Prop Pool object.
    """

    pool_subtype = "prop"

    def __init__(self, pool_id: str, league, payout_pct: Decimal):
        """
        Initialize a PropPool object.

        Args:
            pool_id (str): The unique identifier for the pool.
            league (League): The league object.
            payout_pct (Decimal): The payout percentage.
        """
        super().__init__(
            league,
            pool_id,
            payout_pct,
            league.CHAMPIONSHIP_WEEK,
        )

    def set_pool_winner(self):
        """
        Set the winners of the prop pool.
        """
        winners_roster_id = input("Enter roster_id of winners: ")
        return [{"roster_id": winners_roster_id}]


class HighestScoreOfWeekPool(WeeklyPool):
    """
    Subclass representing a pool for the highest score of the week.

    Args:
        league (League): The league object.
        payout_pct (Decimal): The payout percentage.
        week (int): The week of the pool.
    """

    def __init__(self, league, payout_pct: Decimal, week: int):
        """
        Initialize a HighestScoreOfWeekPool object.

        Args:
            league (League): The league object.
            payout_pct (Decimal): The payout percentage.
            week (int): The week of the pool.
        """
        super().__init__(
            league,
            f"highest_score_of_week_{week}",
            payout_pct,
            week,
        )

    def set_pool_winner(self):
        """
        Set the winners(s) of the pool based on the highest team score of the week.
        """
        return MatchupStats.get_high_team_score(self.league, week=self.week)


class HighestScoringMarginOfWeekPool(WeeklyPool):
    """
    Subclass representing a pool for the highest scoring margin of the week.

    Args:
        league (League): The league object.
        payout_pct (Decimal): The payout percentage.
        week (int): The week of the pool.
    """

    def __init__(self, league, payout_pct: Decimal, week: int):
        """
        Initialize a HighestScoringMarginOfWeekPool object.

        Args:
            league (League): The league object.
            payout_pct (Decimal): The payout percentage.
            week (int): The week of the pool.
        """
        super().__init__(
            league,
            f"highest_scoring_margin_of_the_week_{week}",
            payout_pct,
            week,
        )

    def set_pool_winner(self):
        """
        Set the winners(s) of the pool based on the highest scoring margin of the week.
        """
        return MatchupStats.get_high_scoring_margin(self.league, week=self.week)


class HighestScoringPlayerOfWeekPool(WeeklyPool):
    """
    Subclass representing a pool for the highest scoring player of the week.

    Args:
        league (League): The league object.
        payout_pct (Decimal): The payout percentage.
        week (int): The week of the pool.
    """

    def __init__(self, league, payout_pct: Decimal, week: int):
        """
        Initialize a HighestScoringPlayerOfWeekPool object.

        Args:
            league (League): The league object.
            payout_pct (Decimal): The payout percentage.
            week (int): The week of the pool.
        """
        super().__init__(
            league,
            f"highest_scoring_player_of_week_{week}",
            payout_pct,
            week,
        )

    def set_pool_winner(self):
        """
        Set the winners(s) of the pool based on the highest scoring player of the week.
        """
        return PlayerStats.get_high_player_score(self.league, week=self.week)


class RegularSeasonFirstPlacePool(SeasonPool):
    def __init__(self, league, payout_pct: Decimal):
        super().__init__(
            league,
            "regular_season_first_place",
            payout_pct,
            pool_subtype="season_cumulative",
        )

    def set_pool_winner(self):
        return LeagueStats.get_regular_season_first_place(self.league)

    def get_leaderboard(self):
        return LeagueStats.get_regular_season_first_place(self.league, top_n=12)


class RegularSeasonMostPointsPool(SeasonPool):
    def __init__(self, league, payout_pct: Decimal):
        super().__init__(
            league,
            "regular_season_most_points",
            payout_pct,
            pool_subtype="season_cumulative",
        )

    def set_pool_winner(self):
        return LeagueStats.get_regular_season_most_points(self.league)

    def get_leaderboard(self):
        return LeagueStats.get_regular_season_most_points(self.league, top_n=12)


class RegularSeasonMostPointsAgainstPool(SeasonPool):
    def __init__(self, league, payout_pct: Decimal):
        super().__init__(
            league,
            "regular_season_most_points_against",
            payout_pct,
            pool_subtype="season_cumulative",
        )

    def set_pool_winner(self):
        return LeagueStats.get_regular_season_most_points_against(self.league)

    def get_leaderboard(self):
        return LeagueStats.get_regular_season_most_points_against(self.league, top_n=12)


class RegularSeasonHighestScoringPlayerPool(SeasonPool):
    def __init__(self, league, payout_pct: Decimal):
        super().__init__(
            league,
            "regular_season_highest_scoring_player",
            payout_pct,
            pool_subtype="season_cumulative",
        )

    def set_pool_winner(self):
        return PlayerStats.get_regular_season_high_scoring_player(self.league)

    def get_leaderboard(self):
        return PlayerStats.get_regular_season_high_scoring_player(self.league, top_n=12)


class OneWeekHighestScorePool(SeasonPool):
    def __init__(self, league, payout_pct: Decimal):
        super().__init__(
            league,
            "one_week_highest_score",
            payout_pct,
            pool_subtype="season_high",
        )

    def set_pool_winner(self):
        return MatchupStats.get_high_team_score(self.league, week=None)

    def get_leaderboard(self):
        return MatchupStats.get_high_team_score(self.league, week=None, top_n=12)


class OneWeekHighestScoreAgainstPool(SeasonPool):
    def __init__(self, league, payout_pct: Decimal):
        super().__init__(
            league,
            "one_week_highest_score_against",
            payout_pct,
            pool_subtype="season_high",
        )

    def set_pool_winner(self):
        return MatchupStats.get_high_score_against(self.league, week=None)

    def get_leaderboard(self):
        return MatchupStats.get_high_score_against(self.league, week=None, top_n=12)


class OneWeekHighestScoringPlayerPool(SeasonPool):
    def __init__(self, league, payout_pct: Decimal):
        super().__init__(
            league,
            "one_week_highest_scoring_player",
            payout_pct,
            pool_subtype="season_high",
        )

    def set_pool_winner(self):
        return PlayerStats.get_high_player_score(self.league, week=None)

    def get_leaderboard(self):
        return PlayerStats.get_high_player_score(self.league, week=None, top_n=12)


class OneWeekSmallestMarginPool(SeasonPool):
    def __init__(self, league, payout_pct: Decimal):
        super().__init__(
            league,
            "one_week_smallest_margin_of_loss",
            payout_pct,
            pool_subtype="season_high",
        )

    def set_pool_winner(self):
        return MatchupStats.get_small_scoring_margin(self.league, week=None)

    def get_leaderboard(self):
        return MatchupStats.get_small_scoring_margin(self.league, week=None, top_n=12)


class OpeningWeekWinnersPool(SpecialWeekPool):
    def __init__(self, league, payout_pct: Decimal):
        super().__init__(
            league,
            "each_winners_of_opening_week",
            payout_pct,
            league.OPENING_WEEK,
        )

    def set_pool_winner(self):
        return MatchupStats.get_head_to_head_winners(self.league, week=self.week)


class RivalryWeekWinnersPool(SpecialWeekPool):
    def __init__(self, league, payout_pct: Decimal):
        super().__init__(
            league,
            "each_winners_of_rivalry_week",
            payout_pct,
            league.RIVALRY_WEEK,
        )

    def set_pool_winner(self):
        return MatchupStats.get_head_to_head_winners(self.league, week=self.week)


class LastWeekWinnersPool(SpecialWeekPool):
    def __init__(self, league, payout_pct: Decimal):
        super().__init__(
            league,
            "each_winners_of_last_week",
            payout_pct,
            league.LAST_WEEK,
        )

    def set_pool_winner(self):
        return MatchupStats.get_head_to_head_winners(self.league, week=self.week)


class LeagueWinner(MainPool):
    def __init__(self, league, payout_pct: Decimal):
        super().__init__(
            league,
            "league_winner",
            payout_pct,
            league.CHAMPIONSHIP_WEEK,
        )

    def set_pool_winner(self):
        """
        Set the winners of the prop pool.
        """
        match = next(
            (
                match
                for match in self.league.playoffs
                if match["r"] == 3 and match["m"] == 6
            ),
            None,
        )
        return match.get("w")


class LeagueRunnerUp(MainPool):
    def __init__(self, league, payout_pct: Decimal):
        super().__init__(
            league,
            "league_runnerup",
            payout_pct,
            league.CHAMPIONSHIP_WEEK,
        )

    def set_pool_winner(self):
        """
        Set the winners of the prop pool.
        """
        match = next(
            (
                match
                for match in self.league.playoffs
                if match["r"] == 3 and match["m"] == 6
            ),
            None,
        )
        return match.get("l")


class LeagueThirdPlace(MainPool):
    def __init__(self, league, payout_pct: Decimal):
        super().__init__(
            league,
            "league_thirdplace",
            payout_pct,
            league.CHAMPIONSHIP_WEEK,
        )

    def set_pool_winner(self):
        """
        Set the winners of the prop pool.
        """
        match = next(
            (
                match
                for match in self.league.playoffs
                if match["r"] == 3 and match["m"] == 7
            ),
            None,
        )
        return match.get("w")
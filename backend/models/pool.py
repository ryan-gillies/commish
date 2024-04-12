"""
Pool Module
=============

This module defines a framework for managing fantasy sports pools within a league. 
It includes abstract base classes for different types of pools and concrete 
implementations for specific pool types such as weekly, seasonal, and special week pools.
"""

from abc import ABC, ABCMeta, abstractmethod
from decimal import Decimal
from sqlalchemy import update, Column, String, Integer, Boolean, Numeric, JSON, ForeignKey
from sqlalchemy.orm import relationship, join
import sys
import logging

from extensions import db
from onepassword import OnePassword
from venmo_api import Client

from .league import League
from .stats import *
from .user import User, Roster


class PoolMeta(type(db.Model), ABCMeta):
    pass


class Pool(ABC, db.Model, metaclass=PoolMeta):
    __tablename__ = "pools"

    pool_id = Column(String, primary_key=True)
    league_id = Column(
        String, ForeignKey("leagues.league_id"), primary_key=True
    )
    winner = Column(String, ForeignKey("users.username"))
    winner_payload = Column(JSON)
    payout_amount = Column(Numeric)
    week = Column(Integer)
    paid = Column(Boolean)
    label = Column(String)
    pool_type = Column(String)
    pool_subtype = Column(String)
    pool_class = Column(String)

    __mapper_args__ = {
        "polymorphic_on": pool_class,
        "polymorphic_identity": "pool",
    }

    league = relationship("League", backref="pools")
    user = relationship("User", backref="pools")

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
        self.league_id = league.league_id
        self.payout_pct = payout_pct
        self.payout_amount = self.set_payout_amount()
        self.week = week
        self.paid = False
        self.label = pool_id.replace("_", " ").title()

    def __str__(self):
        """
        Return a string representation of the Pool object.
        """
        attributes = {
            "pool": self.label,
            "week": self.week,
            "payout": self.payout_amount,
            "winner": self.winner,
            "paid": self.paid,
        }

        attr_string = "\n".join(
            [f"{key}: {value}" for key, value in attributes.items()]
        )
        return attr_string

    def set_winner(self):
        """
        Set the winner of the pool.
        """
        winner = self.set_pool_winner()[0]["roster_id"]

        if self.pool_type == 'side':
            self.winner_payload = self.set_pool_winner()

        user = User.get_user_by_roster_id(winner, self.league_id)

        if user:
            stmt = (
                update(Pool)
                .where(Pool.pool_id == self.pool_id)
                .where(Pool.league_id == self.league_id)
                .values(winner=user.username)
            )
            db.session.execute(stmt)
            db.session.commit()
        else:
            print(f"User with roster_id {self.winner} not found in league {self.league_id}")


    @abstractmethod
    def set_pool_winner(self):
        """
        Abstract method to set the winner of the pool.
        """
        # get the user from the returned value

    @abstractmethod
    def set_payout_amount(self):
        """
        Abstract method to set the payout amount for the pool.
        """
        pass

    def process_payout(self):
        """
        Process the payout for a winner in the pool.

        Args:
            winner (User): The user who won the pool.
            amount (float): The amount to be paid to the winner.
            week (int): The week of the pool.
            season (int): The season of the pool.

        Returns:
            bool: True if the payout was successful, False otherwise.
        """
        from .payout import Payout

        # Initialize Venmo client
        op = OnePassword()
        config = League.query.filter_by(league_id=self.league_id).first().config
        venmo_client = Client(
            access_token=op.get_item(
                config["credentials"]["venmo_uuid"], fields="access_token"
            )
        )

        # Send payment via Venmo
        try:
            if not self.paid:
                payment_info = venmo_client.payment.send_money(
                    amount=self.payout_amount,
                    note=f"Payout for pool {self.label}, week {self.week}",
                    target_user_id=self.winner_user.get_venmo_id(),
                )
                logging.info(f"Payment sent to {self.winner} via Venmo: {payment_info}")
            # Create payout item in the database
            payout = Payout(
                pool_id=self.pool_id,
                amount=self.payout_amount,
                week=self.week,
                venmo_id=self.winner_user.get_venmo_id(),
                paid=True,  # Mark as paid since payment was successful
                season=League.query.filter_by(league_id=self.league_id).first().season
,
            )
            try:
                payout.save_to_database()
                logging.info("Payout item created in the database.")
                return True
            except Exception as e:
                logging.error(f"Failed to create payout item in the database: {e}")
                return False
        except Exception as e:
            logging.error(f"Failed to send payment to {self.winner} via Venmo: {e}")
            return False

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
        
        if getattr(pool_class, 'weekly', False):
            return pool_class.create_pools_for_weeks(league, payout_pct, **kwargs)
        elif getattr(pool_class, 'main_pool', False):
            return pool_class(league=league, payout_pct=payout_pct, **{})
        else:
            return pool_class(league=league, payout_pct=payout_pct, **kwargs)


class SidePool(Pool, ABC):
    """
    Subclass representing a Side Pool object.
    """

    __abstract__ = True
    main_pool = False

    def __init__(self, league, pool_id: str, payout_pct: Decimal, week: int):
        """
        Initialize a SidePool object.

        Args:
            league (League): The league object.
            pool_id (str): The unique identifier for the pool.
            payout_pct (Decimal): The payout percentage.
            week (int): The week of the pool.
        """
        super().__init__(pool_id, league, payout_pct, week)
        self.pool_type = "side"

    def set_payout_amount(self):
        """
        Set the payout amount for the side pool.
        """
        side_pot = League.query.filter_by(league_id=self.league_id).first().side_pot
        return round(self.payout_pct * side_pot, 2)


class MainPool(Pool, ABC):
    """
    Subclass representing a Main Pool object.
    """

    __abstract__ = True
    main_pool = True

    def __init__(self, league, pool_id: str, payout_pct: Decimal, week: int):
        """
        Initialize a MainPool object.

        Args:
            league (League): The league object.
            pool_id (str): The unique identifier for the pool.
            payout_pct (Decimal): The payout percentage.
            week (int): The week of the pool.
        """
        super().__init__(pool_id, league, payout_pct, week)
        self.pool_type = "main"

    def set_payout_amount(self):
        """
        Set the payout amount for the main pool.
        """
        main_pot = League.query.filter_by(league_id=self.league_id).first().main_pot
        return round(self.payout_pct * main_pot, 2)


class SeasonPool(SidePool, ABC):
    """
    Subclass representing a Season Pool object.
    """

    __abstract__ = True

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

    __abstract__ = True

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
        self.pool_subtype = "special_week"

    def split_pool(self):
        winners = MatchupStats.get_head_to_head_winners(self.league, week=self.week)
        payout_amount = self.payout_amount / len(winners)
        pools = []
        for winner in winners:
            pool_instance = getattr(sys.modules[__name__], self.pool_class)(self.league, 0)
            pool_instance.payout_amount = payout_amount
            pool_instance.matchup_id = winner['matchup_id']
            pool_instance.pool_id = self.pool_id+'_'+str(pool_instance.matchup_id)
            pools.append(pool_instance)
            db.session.add(pool_instance)
        db.session.delete(self)
        db.session.commit()
        return pools

class WeeklyPool(SidePool, ABC):
    """
    Subclass representing a Weekly Pool object.
    """

    __abstract__ = True
    weekly = True

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
        self.subtype = 'weekly'

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

    __mapper_args__ = {
        "polymorphic_identity": "PropPool",
    }

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
        self.pool_class = self.__mapper_args__["polymorphic_identity"]
        self.pool_subtype = 'prop'

    def set_pool_winner(self):
        """
        Set the winners of the prop pool.
        """
        winner_roster_id = input("Enter roster_id of winner: ")
        return [{"roster_id": winner_roster_id}]


class HighestScoreOfWeekPool(WeeklyPool):
    """
    Subclass representing a pool for the highest score of the week.

    Args:
        league (League): The league object.
        payout_pct (Decimal): The payout percentage.
        week (int): The week of the pool.
    """

    __mapper_args__ = {
        "polymorphic_identity": "HighestScoreOfWeekPool",
    }

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
        self.pool_class = self.__mapper_args__["polymorphic_identity"]

    def set_pool_winner(self):
        """
        Set the winner of the pool based on the highest team score of the week.
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

    __mapper_args__ = {
        "polymorphic_identity": "HighestScoringMarginOfWeekPool",
    }

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
            f"highest_scoring_margin_of_week_{week}",
            payout_pct,
            week,
        )
        self.pool_class = self.__mapper_args__["polymorphic_identity"]

    def set_pool_winner(self):
        """
        Set the winner of the pool based on the highest scoring margin of the week.
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

    __mapper_args__ = {
        "polymorphic_identity": "HighestScoringPlayerOfWeekPool",
    }

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
        self.pool_class = self.__mapper_args__["polymorphic_identity"]

    def set_pool_winner(self):
        """
        Set the winner of the pool based on the highest scoring player of the week.
        """
        return PlayerStats.get_high_player_score(self.league, week=self.week)


class RegularSeasonFirstPlacePool(SeasonPool):
    __mapper_args__ = {
        "polymorphic_identity": "RegularSeasonFirstPlacePool",
    }

    def __init__(self, league, payout_pct: Decimal):
        super().__init__(
            league,
            "regular_season_first_place",
            payout_pct,
            pool_subtype="season_cumulative",
        )
        self.pool_class = self.__mapper_args__["polymorphic_identity"]

    def set_pool_winner(self):
        return LeagueStats.get_regular_season_first_place(self.league)

    def get_leaderboard(self):
        return LeagueStats.get_regular_season_first_place(self.league, top_n=12)


class RegularSeasonMostPointsPool(SeasonPool):
    __mapper_args__ = {
        "polymorphic_identity": "RegularSeasonMostPointsPool",
    }

    def __init__(self, league, payout_pct: Decimal):
        super().__init__(
            league,
            "regular_season_most_points",
            payout_pct,
            pool_subtype="season_cumulative",
        )
        self.pool_class = self.__mapper_args__["polymorphic_identity"]

    def set_pool_winner(self):
        return LeagueStats.get_regular_season_most_points(self.league)

    def get_leaderboard(self):
        return LeagueStats.get_regular_season_most_points(self.league, top_n=12)


class RegularSeasonMostPointsAgainstPool(SeasonPool):
    __mapper_args__ = {
        "polymorphic_identity": "RegularSeasonMostPointsAgainstPool",
    }

    def __init__(self, league, payout_pct: Decimal):
        super().__init__(
            league,
            "regular_season_most_points_against",
            payout_pct,
            pool_subtype="season_cumulative",
        )
        self.pool_class = self.__mapper_args__["polymorphic_identity"]

    def set_pool_winner(self):
        return LeagueStats.get_regular_season_most_points_against(self.league)

    def get_leaderboard(self):
        return LeagueStats.get_regular_season_most_points_against(self.league, top_n=12)


class RegularSeasonHighestScoringPlayerPool(SeasonPool):
    __mapper_args__ = {
        "polymorphic_identity": "RegularSeasonHighestScoringPlayerPool",
    }

    def __init__(self, league, payout_pct: Decimal):
        super().__init__(
            league,
            "regular_season_highest_scoring_player",
            payout_pct,
            pool_subtype="season_cumulative",
        )
        self.pool_class = self.__mapper_args__["polymorphic_identity"]

    def set_pool_winner(self):
        return PlayerStats.get_regular_season_high_scoring_player(self.league)

    def get_leaderboard(self):
        return PlayerStats.get_regular_season_high_scoring_player(self.league, top_n=12)


class OneWeekHighestScorePool(SeasonPool):
    __mapper_args__ = {
        "polymorphic_identity": "OneWeekHighestScorePool",
    }

    def __init__(self, league, payout_pct: Decimal):
        super().__init__(
            league,
            "one_week_highest_score",
            payout_pct,
            pool_subtype="season_high",
        )
        self.pool_class = self.__mapper_args__["polymorphic_identity"]

    def set_pool_winner(self):
        return MatchupStats.get_high_team_score(self.league, week=None)

    def get_leaderboard(self):
        return MatchupStats.get_high_team_score(self.league, week=None, top_n=12)


class OneWeekHighestScoreAgainstPool(SeasonPool):
    __mapper_args__ = {
        "polymorphic_identity": "OneWeekHighestScoreAgainstPool",
    }

    def __init__(self, league, payout_pct: Decimal):
        super().__init__(
            league,
            "one_week_highest_score_against",
            payout_pct,
            pool_subtype="season_high",
        )
        self.pool_class = self.__mapper_args__["polymorphic_identity"]

    def set_pool_winner(self):
        return MatchupStats.get_high_score_against(self.league, week=None)

    def get_leaderboard(self):
        return MatchupStats.get_high_score_against(self.league, week=None, top_n=12)


class OneWeekHighestScoringPlayerPool(SeasonPool):
    __mapper_args__ = {
        "polymorphic_identity": "OneWeekHighestScoringPlayerPool",
    }

    def __init__(self, league, payout_pct: Decimal):
        super().__init__(
            league,
            "one_week_highest_scoring_player",
            payout_pct,
            pool_subtype="season_high",
        )
        self.pool_class = self.__mapper_args__["polymorphic_identity"]

    def set_pool_winner(self):
        return PlayerStats.get_high_player_score(self.league, week=None)

    def get_leaderboard(self):
        return PlayerStats.get_high_player_score(self.league, week=None, top_n=12)


class OneWeekSmallestMarginPool(SeasonPool):
    __mapper_args__ = {
        "polymorphic_identity": "OneWeekSmallestMarginPool",
    }

    def __init__(self, league, payout_pct: Decimal):
        super().__init__(
            league,
            "one_week_smallest_margin_of_loss",
            payout_pct,
            pool_subtype="season_high",
        )
        self.pool_class = self.__mapper_args__["polymorphic_identity"]

    def set_pool_winner(self):
        return MatchupStats.get_small_scoring_margin(self.league, week=None)

    def get_leaderboard(self):
        return MatchupStats.get_small_scoring_margin(self.league, week=None, top_n=12)


class OpeningWeekWinnersPool(SpecialWeekPool):
    __mapper_args__ = {
        "polymorphic_identity": "OpeningWeekWinnersPool",
    }

    def __init__(self, league, payout_pct: Decimal):
        super().__init__(
            league,
            "each_winner_of_opening_week",
            payout_pct,
            league.OPENING_WEEK,
        )
        self.pool_class = self.__mapper_args__["polymorphic_identity"]

    def set_pool_winner(self):
        """
        Set the winner of the pool.

        Returns:
            List[int]: List of Matchup IDs.
        """
        return MatchupStats.get_head_to_head_winners(self.league, week=self.week, matchup_id=self.matchup_id if hasattr(self, 'matchup_id') else None)
class RivalryWeekWinnersPool(SpecialWeekPool):
    __mapper_args__ = {
        "polymorphic_identity": "RivalryWeekWinnersPool",
    }

    def __init__(self, league, payout_pct: Decimal):
        super().__init__(
            league,
            "each_winner_of_rivalry_week",
            payout_pct,
            league.RIVALRY_WEEK,
        )
        self.pool_class = self.__mapper_args__["polymorphic_identity"]

    def set_pool_winner(self):
        return MatchupStats.get_head_to_head_winners(self.league, week=self.week, matchup_id=self.matchup_id if hasattr(self, 'matchup_id') else None)



class LastWeekWinnersPool(SpecialWeekPool):
    __mapper_args__ = {
        "polymorphic_identity": "LastWeekWinnersPool",
    }

    def __init__(self, league, payout_pct: Decimal):
        super().__init__(
            league,
            "each_winner_of_last_week",
            payout_pct,
            league.LAST_WEEK,
        )

    def set_pool_winner(self):
        return MatchupStats.get_head_to_head_winners(self.league, week=self.week, matchup_id=self.matchup_id if hasattr(self, 'matchup_id') else None)


class LeagueWinner(MainPool):
    __mapper_args__ = {
        "polymorphic_identity": "LeagueWinner",
    }

    def __init__(self, league, payout_pct: Decimal):
        super().__init__(
            league,
            "league_winner",
            payout_pct,
            league.CHAMPIONSHIP_WEEK,
        )
        self.pool_class = self.__mapper_args__["polymorphic_identity"]

    def set_pool_winner(self):
        """
        Set the winner of the prop pool.
        """
        league = self.league
        league.fetch_playoffs()
        match = next(
            (
                match
                for match in league.playoffs
                if match["r"] == 3 and match["m"] == 6
            ),
            None,
        )
        self.winner_payload = match
        return [{"roster_id": match.get("w")}]


class LeagueRunnerUp(MainPool):
    __mapper_args__ = {
        "polymorphic_identity": "LeagueRunnerUp",
    }

    def __init__(self, league, payout_pct: Decimal):
        super().__init__(
            league,
            "league_runner_up",
            payout_pct,
            league.CHAMPIONSHIP_WEEK,
        )

    def set_pool_winner(self):
        """
        Set the winner of the prop pool.
        """
        league = self.league
        league.fetch_playoffs()
        match = next(
            (
                match
                for match in league.playoffs
                if match["r"] == 3 and match["m"] == 6
            ),
            None,
        )
        self.winner_payload = match
        return [{"roster_id": match.get("l")}]


class LeagueThirdPlace(MainPool):
    __mapper_args__ = {
        "polymorphic_identity": "LeagueThirdPlace",
    }

    def __init__(self, league, payout_pct: Decimal):
        super().__init__(
            league,
            "league_third_place",
            payout_pct,
            league.CHAMPIONSHIP_WEEK,
        )

    def set_pool_winner(self):
        """
        Set the winner of the prop pool.
        """
        league = self.league
        league.fetch_playoffs()
        match = next(
            (
                match
                for match in league.playoffs
                if match["r"] == 3 and match["m"] == 7
            ),
            None,
        )
        self.winner_payload = match
        return [{"roster_id": match.get("w")}]

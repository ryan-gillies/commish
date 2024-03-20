"""
League Module
=============

The League module provides a class for managing league information and calculations for Sleeper fantasy football leagues.

It includes functionality to load configuration, retrieve league state, get team information, calculate pot amounts, and more.

Classes:
    League: A class for managing league information and calculations.
"""

from sleeperpy import Leagues, Players
import yaml
from decimal import Decimal
from pool import Pool
from utils import PostgreSQLUtils, DynamoDBUtils
import pandas as pd
import sqlalchemy


class League:
    """
    A class for managing league information and calculations.

    This class provides functionality to manage league information and calculations for Sleeper fantasy football leagues.

    Attributes:
        REGULAR_SEASON (list): A list representing regular season weeks.
        OPENING_WEEK (int): The opening week of the regular season.
        RIVALRY_WEEK (int): The week designated as the rivalry week.
        LAST_WEEK (int): The last week of the regular season.
        PLAYOFFS (list): A list representing playoff weeks.
        CHAMPIONSHIP_WEEK (int): The week designated as the championship week.
        state (dict): The state of the league.
        season (int): The active season on Sleeper.
        config (dict): The loaded configuration.
        sleeper_user_id (str): The user ID for the Sleeper account.
        main_buy_in (Decimal): The buy-in amount for the main pool.
        side_buy_in (Decimal): The buy-in amount for the side pool.
        league_id (str): The ID of the league for the current user.
        week (int): The current week for the active season.
        team_count (int): The number of teams in the league.
        main_pot (Decimal): The total pot for the season's main pool.
        side_pool_count (int): The number of teams opted in for the season's side pools.
        side_pot (Decimal): The total pot for the season's side pool.
    """

    REGULAR_SEASON = list(range(1, 15))
    OPENING_WEEK = REGULAR_SEASON[0]
    RIVALRY_WEEK = 8
    LAST_WEEK = REGULAR_SEASON[-1]
    PLAYOFFS = list(range(15, 18))
    CHAMPIONSHIP_WEEK = PLAYOFFS[-1]
    DB_TABLE = "leagues"

    def __init__(self, season=None):
        if season is None:
            self.season = self._set_season()
            self.week = self._set_week()
        else:
            self.season = season
            self.week = 17
        self.config = self._load_config()
        self.sleeper_user_id = self.config["credentials"]["sleeper_user_id"]
        self.league_id = self._set_league_id()
        league_data = DynamoDBUtils.load_from_dynamodb(League.DB_TABLE, self.league_id)
        self.state = Leagues.get_state("nfl")
        if league_data:
            self._load_from_dynamodb(league_data)
        else:
            self.create_new_league()
            DynamoDBUtils.store_to_dynamodb(self.__dict__, League.DB_TABLE, self.league_id )
            self.matchups = self.fetch_matchups()
            self.head_to_head = self.get_head_to_head()
            self.player_stats = self.fetch_player_stats()
            self.team_stats = self.fetch_team_stats()

    def create_new_league(self, season=None):
        self.main_buy_in = self.config["buy_ins"]["main_buy_in"]
        self.side_buy_in = self.config["buy_ins"]["side_buy_in"]
        self.optouts = self._get_optouts()
        self.team_count = self._set_team_count()
        self.side_pool_count = self.team_count - len(self.optouts)
        self.main_pot = self.main_buy_in * self.team_count
        self.side_pot = self.side_buy_in * self.side_pool_count
        self.setup_pools()

    def _load_from_dynamodb(self, league_data):
        for key, value in league_data.items():
            setattr(self, key, value)

    def _load_config(self):
        """
        Loads configuration from a YAML file for the given season.

        Returns:
            dict: The loaded configuration.
        """
        with open(f"pools/config/{self.season}.yaml", "r") as file:
            return yaml.safe_load(file)

    def _set_season(self):
        """
        Gets the current active season.

        Returns:
            int: The active season on Sleeper.
        """
        return int(self.state["season"])

    def _set_week(self):
        """
        Gets the current week for the season.

        Returns:
            int: The current week for the active season.
        """
        return int(
            self.state["week"] - 1 if self.state["season_type"] == "regular" else 1
        )

    def _set_league_id(self):
        """
        Gets the ID of the league for the current user.

        Returns:
            str: The ID of the league.
        """
        leagues = Leagues.get_all_leagues(self.sleeper_user_id, "nfl", self.season)
        if not leagues:
            raise ValueError("No leagues found for the given user and season.")
        return leagues[0]["league_id"]

    def _set_team_count(self):
        """
        Gets the number of teams in the league.

        Returns:
            int: The number of teams in the league.
        """
        return Leagues.get_league(self.league_id)["total_rosters"]

    def _get_optouts(self):
        """
        Gets the list of opted-out users for the current season.

        Returns:
            list: A list of user IDs who have opted out.
        """
        current_season_optouts = self.config["optouts"]
        rosters = Leagues.get_rosters(self.league_id)
        return [
            roster["roster_id"]
            for roster in rosters
            if roster["owner_id"] in current_season_optouts
        ]

    def fetch_matchups(self):
        """
        Fetches matchups for the weeks leading up to the current week.

        Returns:
            dict: A dictionary where keys are week numbers and values are lists of matchups.
        """
        matchups = {}
        for week in range(self.OPENING_WEEK, self.week + 1):
            matchups[week] = Leagues.get_matchups(self.league_id, week)
            matchups_db = pd.DataFrame(matchups[week])
            matchups_db["league_id"] = self.league_id
            matchups_db["week"] = week
            PostgreSQLUtils.store_to_postgresql(
                "sleeper_matchups",
                matchups_db,
                dtype={"players_points": sqlalchemy.types.JSON},
            )
        return matchups

    def get_head_to_head(self):
        """
        Extracts matchup information from the provided matchups.

        Args:
            week (int): The week number to filter matchups. If None, all weeks are considered.

        Returns:
            list: A list of dictionaries containing matchup information.
        """

        matchup_info = []
        for week_num, week_matchups in self.matchups.items():
            matchups_by_id = {}  # Group matchups by matchup_id
            for matchup in week_matchups:
                matchup_id = matchup["matchup_id"]
                if matchup_id not in matchups_by_id:
                    matchups_by_id[matchup_id] = []
                matchups_by_id[matchup_id].append(matchup)

            # Iterate over matchups grouped by matchup_id
            for matchup_id, matchups in matchups_by_id.items():
                winner = max(matchups, key=lambda x: x["points"])
                loser = min(matchups, key=lambda x: x["points"])
                matchup_dict = {
                    "week": week_num,
                    "matchup_id": matchup_id,
                    "matchup_winner": winner["roster_id"],
                    "matchup_loser": loser["roster_id"],
                    "winner_points": winner["points"],
                    "loser_points": loser["points"],
                    "matchup_margin": winner["points"] - loser["points"],
                }
                matchup_info.append(matchup_dict)
        return matchup_info

    def fetch_player_stats(self):
        """
        Extracts player scores from the provided matchups for the weeks leading up to the current week.

        Returns:
            list: A list of dictionaries containing player scores.
        """
        player_stats = []
        if player_list is None:
            player_list = Players.get_all_players()
        for week_num, week_matchups in self.matchups.items():
            if (self.OPENING_WEEK is not None and week_num < self.OPENING_WEEK) or (
                self.week is not None and week_num > self.week
            ):
                continue
            for matchup in week_matchups:
                for key, value in matchup["players_points"].items():
                    if key in matchup["starters"]:
                        player = {
                            "player_id": key,
                            "week": week_num,
                            "score": value,
                            "roster_id": matchup["roster_id"],
                            "position": player_list.get(key, {}).get("position"),
                            "player_name": player_list.get(key, {}).get(
                                "full_name"
                            ),
                        }
                        player_stats.append(player)
        return player_stats

    def fetch_team_stats(self):
        """
        Gets statistics about teams in the league.

        Returns:
            list: A list of dictionaries containing team statistics.
        """
        rosters = Leagues.get_rosters(self.league_id)

        teams_stats = []
        for roster in rosters:
            teams_stats.append(
                {
                    "roster_id": roster["roster_id"],
                    "total_wins": roster["settings"]["wins"],
                    "total_losses": roster["settings"]["losses"],
                    "total_ties": roster["settings"]["ties"],
                    "total_points_for": roster["settings"]["fpts"]
                    + (roster["settings"]["fpts_decimal"] / 100),
                    "total_points_against": roster["settings"]["fpts_against"]
                    + (roster["settings"]["fpts_against_decimal"] / 100),
                }
            )
        return teams_stats

    def setup_pools(self):
        """
        Initializes pools and fetches matchups for the league.
        Validates that the total payout amounts of side and main pools are equal to the respective pots.

        Args:
            directory (str): The directory path for saving/loading pools.

        Returns:
            dict: A dictionary containing pool information.
        """
        pools_list = Pool.create_pools(self)
        pools = {pool.pool_id: pool for pool in pools_list}

        # Validate the total payout amounts of side and main pools
        side_payout_total = sum(
            pool.payout_amount for pool in pools.values() if pool.pool_type == "side"
        )
        main_payout_total = sum(
            pool.payout_amount for pool in pools.values() if pool.pool_type == "main"
        )

        if round(side_payout_total, 2) != round(self.side_pot, 2):
            raise ValueError(
                "Total payout amount for side pools does not match side pot."
            )
        if round(main_payout_total, 2) != round(self.main_pot, 2):
            raise ValueError(
                "Total payout amount for main pools does not match main pot."
            )
        return pools

    def __str__(self):
        """
        Return a string representation of the League object.
        """
        attributes = {
            "season": self.season,
            "league_id": self.league_id,
            "week": self.week,
            "team_count": self.team_count,
            "main_pot": self.main_pot,
            "side_pool_count": self.side_pool_count,
            "side_pot": self.side_pot,
            "state": self.state,
        }

        attr_string = "\n".join(
            [f"{key}: {value}" for key, value in attributes.items()]
        )
        return attr_string

    def fetch_playoffs(self):
        return Leagues.get_winners_playoff_bracket(self.league_id)

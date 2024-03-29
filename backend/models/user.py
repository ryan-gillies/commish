from typing import Dict
import yaml
from sleeperpy import Leagues
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, MapAttribute


class User(Model):
    """
    Represents a user in the Sleeper fantasy football application.

    Attributes:
        user_id (str): The user's unique identifier in Sleeper.
        username (str): The user's display name in Sleeper.
        avatar (str): The URL of the user's avatar image.
        venmo_id (str, optional): The user's Venmo user ID for payouts.
        roster_id (Dict[str, str]): A dictionary mapping league IDs to the user's roster ID for that league.
    """

    class Meta:
        table_name = "users"

    username = UnicodeAttribute(hash_key=True)
    name = UnicodeAttribute()
    user_id = UnicodeAttribute()
    avatar = UnicodeAttribute()
    venmo_id = UnicodeAttribute()   
    roster_id = MapAttribute()

    with open("backend/models/config/venmo_ids.yaml", "r", encoding="utf-8") as f:
        venmo_ids = yaml.load(f, Loader=yaml.SafeLoader)

    def __init__(self, user_data: Dict[str, str], league):
        """
        Initializes a User object.

        Args:
            user_data (dict): A dictionary containing user data retrieved from the Sleeper API.
        """
        self.user_id = user_data["user_id"]
        self.username = user_data.get("username", user_data.get("display_name"))
        self.avatar = user_data["avatar"]
        self.venmo_id = User.venmo_ids.get(self.username, "")
        self.league_id = league.league_id
        self.roster_id = str(self.set_roster_id(league.league_id))
        self.save()

    def __str__(self):
        """
        Returns a string representation of the User object.

        Returns:
            str: A string representation of the user.
        """
        return f"User(user_id={self.user_id}, username={self.username}, current_roster_id = {self.roster_id}, avatar={self.avatar}, venmo_id={self.venmo_id})"

    def set_roster_id(self, league_id):
        """
        Adds roster ID by league ID for the user.
        """
        rosters = Leagues.get_rosters(league_id)
        for league in rosters:
            if league["owner_id"] == self.user_id:
                return league["roster_id"]

    @classmethod
    def get_user_by_roster_id(cls, roster_id, league):
        """
        Get a user object by roster ID from the DynamoDB table.

        Args:
            roster_id (str): The roster ID to search for.
            league (League): The league object.

        Returns:
            User: The user object with the specified roster ID, or None if not found.
        """
        try:
            user_item = cls.get(
                cls.username
                == cls.db_table.query(
                    cls.roster_id[league.league_id] == str(roster_id)
                ).first()
            )
            return user_item
        except cls.DoesNotExist:
            return None
            

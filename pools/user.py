"""
User Module
===========

This module provides a representation of a user in the Sleeper fantasy football application.
It includes a `User` class that encapsulates user data such as user ID, username, avatar URL,
Venmo user ID for payouts, and roster IDs by league.

Classes:
    - User: Represents a user in the Sleeper fantasy football application.

Attributes:
    - venmo_ids (dict): A dictionary mapping usernames to Venmo user IDs for payouts.
                        Loaded from the 'pools/venmo_ids.yaml' file.

Usage:
    from User import User

    # Create a User object with user data retrieved from the Sleeper API
    user_data = {
        "user_id": "123456",
        "display_name": "example_user",
        "avatar": "https://example.com/avatar.jpg"
    }
    user = User(user_data)

    # Retrieve user information
    user_id = user.get_user_id()
    username = user.get_username()
    avatar_url = user.get_avatar()
    roster_id = user.get_roster_id("league_id")

    # Print user information
    print(user)
"""

from typing import Dict
import yaml
from utils import DynamoDBUtils
from sleeperpy import Leagues
from boto3.dynamodb.conditions import Attr


class User:
    """
    Represents a user in the Sleeper fantasy football application.

    Attributes:
        user_id (str): The user's unique identifier in Sleeper.
        username (str): The user's display name in Sleeper.
        avatar (str): The URL of the user's avatar image.
        venmo_id (str, optional): The user's Venmo user ID for payouts.
        roster_ids_by_league (Dict[str, str]): A dictionary mapping league IDs to the user's roster ID for that league.
    """

    # Load Venmo IDs from YAML file
    with open("pools/config/venmo_ids.yaml", "r", encoding="utf-8") as f:
        venmo_ids = yaml.load(f, Loader=yaml.SafeLoader)

    db_table = DynamoDBUtils.get_table("users")

    def __init__(self, user_data: Dict[str, str], league):
        """
        Initializes a User object.

        Args:
            user_data (dict): A dictionary containing user data retrieved from the Sleeper API.
        """
        self.user_id = user_data["user_id"]
        try:
            self.user_name = user_data["user_name"]
        except KeyError:
            # Sleeper names this field differently
            self.user_name = user_data["display_name"]        
        self.avatar = user_data["avatar"]
        self.venmo_id = self.set_venmo_id()
        self.league_id = league.league_id
        self.roster_id = str(self.get_roster_id(league.league_id))
        self.save_to_dynamodb()

    def save_to_dynamodb(self):
        """
        Saves the user data to DynamoDB.
        """
        user_item = {
            "user_name": self.user_name,
            "user_id": self.user_id,
            "avatar": self.avatar,
            "venmo_id": self.venmo_id,
            "roster_id": {self.league_id: self.roster_id},
        }

        response = User.db_table.get_item(Key={"user_name": self.user_name})

        if "Item" in response:
            User.db_table.update_item(
                Key={"user_name": self.user_name},
                UpdateExpression="SET roster_id.#league_id = :roster_id",
                ExpressionAttributeNames={
                    "#league_id": self.league_id
                },
                ExpressionAttributeValues={":roster_id": self.roster_id},
            )
        else:
            User.db_table.put_item(Item=user_item)

    def set_venmo_id(self) -> str:
        """
        Retrieves the Venmo user ID for the user's username.

        Returns:
            str: The Venmo user ID.
        """
        return User.venmo_ids.get(self.user_name, "")

    def get_roster_id(self, league_id):
        """
        Adds roster ID by league ID for the user.
        """
        rosters = Leagues.get_rosters(league_id)
        for league in rosters:
            if league["owner_id"] == self.user_id:
                return league["roster_id"]

    def get_venmo_id(self) -> str:
        """
        Retrieves the Venmo user ID for the user.

        Returns:
            str: The Venmo user ID.
        """
        return self.venmo_id

    def get_user_id(self) -> str:
        """
        Retrieves the user ID.

        Returns:
            str: The user ID.
        """
        return self.user_id

    def get_username(self) -> str:
        """
        Retrieves the username.

        Returns:
            str: The username.
        """
        return self.user_name

    def get_avatar(self) -> str:
        """
        Retrieves the avatar URL.

        Returns:
            str: The avatar URL.
        """
        return self.avatar

    def __str__(self):
        """
        Returns a string representation of the User object.

        Returns:
            str: A string representation of the user.
        """
        return f"User(user_id={self.user_id}, username={self.user_name}, current_roster_id = {self.roster_id}, avatar={self.avatar}, venmo_id={self.venmo_id})"

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
        response = cls.db_table.scan()
        
        if "Items" in response:
            items = response["Items"]
            for item in items:
                if league.league_id in item.get("roster_id", {}) and item["roster_id"][league.league_id] == str(roster_id):
                    user = cls(item, league)
                    return user     
        return None

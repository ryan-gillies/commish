from typing import Dict
import yaml
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import insert
from sleeperpy import Leagues
from extensions import db
import logging

class Roster(db.Model):
    __tablename__ = 'rosters'

    username = db.Column(db.String, db.ForeignKey('users.username'), primary_key=True)
    league_id = db.Column(db.String, primary_key=True)
    roster_id = db.Column(db.String)

class User(db.Model):
    """
    Represents a user in the Sleeper fantasy football application.

    Attributes:
        user_id (str): The user's unique identifier in Sleeper.
        username (str): The user's display name in Sleeper.
        avatar (str): The URL of the user's avatar image.
        venmo_id (str, optional): The user's Venmo user ID for payouts.
        roster_id (Dict[str, str]): A dictionary mapping league IDs to the user's roster ID for that league.
    """

    __tablename__ = "users"

    username = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    user_id = db.Column(db.String)
    avatar = db.Column(db.String)
    venmo_id = db.Column(db.String)   

    rosters = relationship("Roster", backref="user")

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
        self.roster_id = self.set_roster_id(league.league_id)
        self.save_to_database()

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

    def save_to_database(self):
        try:
            stmt = insert(User).values(
                user_id = self.user_id,
                username = self.username,
                name = self.name,
                avatar = self.avatar,
                venmo_id = self.venmo_id,
            )
            stmt = stmt.on_conflict_do_update(
                index_elements=['username'],
                set_={
                    'avatar': self.avatar,
                    'venmo_id': self.venmo_id,
                    'username': self.username,
                }
            )
            db.session.execute(stmt)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logging.error(f"Failed to add user to database: {e}")
            raise

    # @classmethod
    # def get_user_by_roster_id(cls, roster_id, league):
    #     """
    #     Get a user object by roster ID from the database.

    #     Args:
    #         roster_id (str): The roster ID to search for.
    #         league (League): The league object.

    #     Returns:
    #         User: The user object with the specified roster ID, or None if not found.
    #     """
    #     return cls.query.filter_by(roster_id={league.league_id: str(roster_id)}).first()

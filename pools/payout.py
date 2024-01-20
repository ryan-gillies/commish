# """
# Payout Module
# =============

# This module provides a class, Payout, to handle Venmo payouts for individual pools.

# Classes:
#     - Payout: Represents a Venmo payout for an individual user in a pool.

# Usage:
#     from Payout import Payout

#     # Create a Payout object
#     user = User(user_data)
#     amount = 10.0
#     memo = "Payment for the pool"
#     payout = Payout(user, amount, memo)

#     # Initiate the payout
#     payout.send_payment()
# """

# import yaml
# from onepassword import OnePassword
# from venmo_api import Client
# import pandas as pd
# from league import League
# from pool import Pool
# from user import User
# import utils
# import logging


# class Payout:
#     """
#     Handles Venmo payouts for individual pools.
#     """

#     def __init__(self, pool: Pool):
#         """
#         Initializes the Payout object.

#         Args:
#             user (User): The user to whom the payout will be sent.
#             amount (float): The amount of the payout.
#             memo (str): A note to include with the payment.
#         """
#         self.username = user.get_username()
#         self.venmo_id = user.get_venmo_id()
#         self.amount = pool.payout_amount
#         self.memo = memo
#         self.season = pool.season
#         self.week = pool.week

#         with open(f"pools/config/{League.season}.yaml", "r") as file:
#             config = yaml.safe_load(file)
#             self.VENMO_ID = config["credentials"]["venmo_uuid"]

#         self.op = OnePassword()
#         self.venmo_client = Client(
#             access_token=self.op.get_item(self.VENMO_ID, fields="access_token")
#         )
#         self.payout_data = self.get_payout_data()

#         try:
#             self.send_payment()
#             try:
#                 utils.load_data_to_database(self.payout_data, "payouts")
#             except Exception as e:
#                 logging.error(f"Failed to load payout data to database: {e}")
#                 raise
#         except Exception as e:
#             logging.error(f"Error occurred during payment: {e}")
#             raise

#     def get_user(self):
#         """
#         Retrieves the corresponding User object based on the winner's roster ID.

#         Returns:
#             User: The User object corresponding to the winner's roster ID.
#         """
#         for winner in self.pool.winner:
#             roster_id = winner['roster_id']
#             # Assuming users is a list or dictionary containing all User objects
#             for user in users:
#                 if user.roster_id == roster_id:
#                     return user
#         return None  # Return None if no corresponding User object is found

#     def send_payment(self):
#         """
#         Sends an individual payment via Venmo.

#         Returns:
#             dict: Information about the sent payment.
#         """
#         try:
#             return self.venmo_client.payment.send_money(
#                 amount=self.amount, note=self.memo, target_user_id=self.venmo_id
#             )
#         except Exception as e:
#             logging.error(f"Error occurred during payment: {e}")
#             raise

#     def get_payout_data(self):
#         """
#         Retrieves payout data for database insertion.

#         Returns:
#             pd.DataFrame: DataFrame containing payout information.
#         """
#         return pd.DataFrame(
#             {
#                 "season": [self.season],
#                 "week": [self.week],
#                 "pool_id": [self.memo],
#                 "username": [self.username],
#                 "amount": [self.amount],
#                 "paid": [True],
#             }
#         )

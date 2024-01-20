"""This module processes payouts via Venmo"""

import yaml
from onepassword import OnePassword
from venmo_api import Client
import league_info

# Load configuration from YAML file
with open(f"pools/config/{league_info.season}.yaml", "r") as file:
    config = yaml.safe_load(file)
VENMO_ID = config["credentials"]["venmo_uuid"]

with open("pools/config/venmo_ids.yaml", "r") as f:
    venmo_ids = yaml.load(f, Loader=yaml.SafeLoader)

op = OnePassword()


def payout(username: str, amount: float, memo: str):
    """
    Sends an individual payment via Venmo.
    """
    venmo = Client(access_token=op.get_item(VENMO_ID, fields="access_token"))
    recipient = venmo.user.get_user_by_username(username).id
    return venmo.payment.send_money(amount=amount, note=memo, target_user_id=recipient)

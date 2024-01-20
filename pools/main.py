from league import League
from user import User
from pool import *
import sleeperpy
import utils

league = League("2023")
# for pool_id, pool_obj in league.pools.items():
#     pool_obj.paid = True
#     pool_obj.set_winner()
#     print(pool_obj)

users = sleeperpy.Leagues.get_users(league.league_id)
for user in users:
    User(user, league)   

from league import League
from user import User
from pool import *
import sleeperpy

league = League("2023")
pools = league.setup_pools()
matchups = league.fetch_matchups()
league.get_head_to_head()
league.fetch_player_stats()
league.fetch_team_stats()
print(pools)


for pool in pools.values():
    pool.set_winner()

users = sleeperpy.Leagues.get_users(league.league_id)
for user in users:
    User(user, league)   

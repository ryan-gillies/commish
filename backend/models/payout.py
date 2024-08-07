from sqlalchemy import func
from ..models.league import League
from ..models.pool import Pool
from ..models.user import User

from ..database import get_db
from sqlalchemy.orm import scoped_session

def get_user_payouts(season=None):
    db = next(get_db())
    query = db.query(Pool).join(League, Pool.league_id == League.league_id).filter(Pool.paid == True)
    
    if season is not None:
        query = query.filter(League.season == season)
    
    payouts = query.group_by(Pool.winner, Pool.pool_type).with_entities(
        Pool.winner,
        Pool.pool_type,
        func.sum(Pool.payout_amount).label('amount')
    ).all()

    user_payouts = []
    for winner, pool_type, amount in payouts:
        user = db.query(User).get(winner)
        user_payout = {
            'username': winner,
            'name': user.name,
            'amount': float(amount),
            'pool_type': pool_type
        }
        user_payouts.append(user_payout)

    return user_payouts

def get_payout_details(season=None, username=None):
    db = next(get_db())
    query = db.query(Pool, League).join(League, Pool.league_id == League.league_id).filter(Pool.paid == True)
    if season is not None:
        query = query.filter(League.season == season)
    if username is not None:
        query = query.filter(Pool.winner == username)

    payout_details = []
    for pool, league in query.all():
        user = db.query(User).get(pool.winner)
        payout_detail = {
            'season': str(league.season),
            'pool': pool.label,
            'amount': float(pool.payout_amount),
            'week': int(pool.week),
            'name': user.name,
            'paid': pool.paid
        }
        payout_details.append(payout_detail)
    payout_details.sort(key=lambda x: (x['season'], x['week']), reverse=True)
    return payout_details


from sqlalchemy import func
from ..models.pool import Pool
from ..models.league import League
from ..models.user import User

from ..database import get_db
from sqlalchemy.orm import scoped_session


def get_payouts(season=None):
    db = next(get_db())
    query = db.query(Pool.__tablename__).join(League.__tablename__, Pool.league_id == League.league_id)
    
    if season is not None:
        query = query.filter(League.season == season)
    
    payouts = query.filter(Pool.paid == True).group_by(Pool.winner, Pool.pool_type).with_entities(
        Pool.winner,
        Pool.pool_type,
        func.sum(Pool.payout_amount).label('amount')
    ).all()

    formatted_payouts = []
    for winner, pool_type, amount in payouts:
        user = db.query(User).get(winner)
        formatted_payout = {
            'username': winner,
            'name': user.name,
            'amount': float(amount),
            'pool_type': pool_type
        }
        formatted_payouts.append(formatted_payout)

    return formatted_payouts

db = next(get_db())
print(db.query(Pool).all())
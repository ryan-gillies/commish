from flask import Blueprint, jsonify, request
from sqlalchemy import func
from models.pool import Pool
from models.league import League
from models.user import User

payouts_bp = Blueprint('payouts', __name__)

@payouts_bp.route("/api/v1/payouts/", defaults={'season': None})
@payouts_bp.route("/api/v1/payouts/<int:season>")
def get_payouts(season=None):
    if season is not None:
        query = Pool.query.join(League, Pool.league_id == League.league_id).filter(League.season == season and Pool.paid == True)
    else:
        query = Pool.query.filter(Pool.paid == True)

    payouts = query.group_by(Pool.winner, Pool.pool_type).with_entities(
        Pool.winner,
        Pool.pool_type,
        func.sum(Pool.payout_amount).label('amount')
    ).all()

    formatted_payouts = []
    for winner, pool_type, amount in payouts:
        user = User.query.get(winner)
        formatted_payout = {
            'username': winner,
            'name': user.name,
            'amount': float(amount),
            'pool_type': pool_type
        }
        formatted_payouts.append(formatted_payout)

    return jsonify(formatted_payouts)


@payouts_bp.route("/api/v1/payoutdetails")
def get_payout_details(season=None):
    season = request.args.get('season')
    username = request.args.get('username')

    query = Pool.query.join(League, Pool.league_id == League.league_id).filter(Pool.paid == True)
    if season is not None:
        query = query.filter(League.season == season)
    if username is not None:
        query = query.filter(Pool.winner == username)

    detailed_payouts = query.all()
    formatted_detailed_payouts = []
    for payout in detailed_payouts:
        user = User.query.get(payout.winner)
        formatted_payout = {
            'pool': payout.label,
            'amount': float(payout.payout_amount),
            'week': int(payout.week),
            'username': payout.winner,
            'name': user.name,
            'paid': payout.paid,
            'season': payout.league.season
        }
        formatted_detailed_payouts.append(formatted_payout)
    formatted_detailed_payouts.sort(key=lambda x: (x['season'], x['week']), reverse=True)
    return jsonify(formatted_detailed_payouts)


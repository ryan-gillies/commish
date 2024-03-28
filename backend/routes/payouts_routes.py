from flask import Blueprint, jsonify
from sqlalchemy import func
from pools.payout import Payout

payouts_bp = Blueprint('payouts', __name__)

@payouts_bp.route("/api/v1/payouts/", defaults={'season': None})
@payouts_bp.route("/api/v1/payouts/<int:season>")
def retrieve_payouts_by_season(season=None):
    query = Payout.query
    if season is not None:
        query = query.filter(Payout.season == season)

    payouts = query.group_by(Payout.venmo_id).with_entities(
        Payout.venmo_id,
        func.sum(Payout.amount).label('amount')
    ).all()

    formatted_payouts = []
    for venmo_id, amount in payouts:
        formatted_payout = {
            'venmo_id': venmo_id,
            'amount': amount
        }
        formatted_payouts.append(formatted_payout)

    return jsonify(formatted_payouts)

@payouts_bp.route("/api/v1/payouts/<int:season>/<string:venmo_id>")
def retrieve_detailed_payouts(season, venmo_id):
    detailed_payouts = Payout.query.filter_by(season=season, venmo_id=venmo_id).all()
    formatted_detailed_payouts = []
    for payout in detailed_payouts:
        formatted_payout = {
            'pool': payout.pool_id,
            'amount': payout.amount,
            'week': payout.week,
            'venmo_id': payout.venmo_id,
            'paid': payout.paid,
            'season': payout.season
        }
        formatted_detailed_payouts.append(formatted_payout)
    return jsonify(formatted_detailed_payouts)

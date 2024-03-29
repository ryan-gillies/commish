from flask import Blueprint, jsonify
from sqlalchemy import func
from models.payout import Payout

payouts_bp = Blueprint('payouts', __name__)

@payouts_bp.route("/api/v1/payouts/seasons")
def get_payout_seasons():
    payout_seasons = Payout.query.with_entities(Payout.season).distinct().all()
    formatted_payout_seasons = [season[0] for season in payout_seasons]
    return jsonify(formatted_payout_seasons)

@payouts_bp.route("/api/v1/payouts/", defaults={'season': None})
@payouts_bp.route("/api/v1/payouts/<int:season>")
def retrieve_payouts_by_season(season=None):
    query = Payout.query
    if season is not None:
        query = query.filter(Payout.season == season)

    payouts = query.group_by(Payout.username).with_entities(
        Payout.username,
        func.sum(Payout.amount).label('amount')
    ).all()

    formatted_payouts = []
    for username, amount in payouts:
        formatted_payout = {
            'username': username,
            'amount': amount
        }
        formatted_payouts.append(formatted_payout)

    return jsonify(formatted_payouts)

@payouts_bp.route("/api/v1/payouts/<int:season>/<string:username>")
def retrieve_detailed_payouts(season, username):
    detailed_payouts = Payout.query.filter_by(season=season, username=username).all()
    formatted_detailed_payouts = []
    for payout in detailed_payouts:
        formatted_payout = {
            'pool': payout.pool_id,
            'amount': payout.amount,
            'week': payout.week,
            'username': payout.username,
            'paid': payout.paid,
            'season': payout.season
        }
        formatted_detailed_payouts.append(formatted_payout)
    return jsonify(formatted_detailed_payouts)

from flask import Blueprint, jsonify, request
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
def get_payouts(season=None):
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

@payouts_bp.route("/api/v1/payoutdetails")
def get_payout_details():
    season = request.args.get('season')
    username = request.args.get('username')
    query = Payout.query

    if season is not None:
        query = query.filter_by(season=season)
    if username is not None:
        query = query.filter_by(username=username)

    detailed_payouts = query.all()
    formatted_detailed_payouts = []
    for payout in detailed_payouts:
        formatted_payout = {
            'pool': payout.pool_id,
            'amount': payout.amount,
            'week': int(payout.week),
            'username': payout.username,
            'paid': payout.paid,
            'season': int(payout.season)
        }
        formatted_detailed_payouts.append(formatted_payout)
    return jsonify(formatted_detailed_payouts)

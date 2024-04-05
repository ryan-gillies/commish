from flask import Blueprint, jsonify, request
from sqlalchemy import func
from models.pool import Pool

pools_bp = Blueprint('pools', __name__)

@pools_bp.route("/api/v1/pools/seasons")
def get_Pool_seasons():
    Pool_seasons = Pool.query.with_entities(Pool.season).distinct().all()
    formatted_Pool_seasons = [season[0] for season in Pool_seasons]
    return jsonify(formatted_Pool_seasons)

@pools_bp.route("/api/v1/pools/", defaults={'season': None})
@pools_bp.route("/api/v1/pools/<int:season>")
def get_pools(season=None):
    query = Pool.query
    if season is not None:
        query = query.filter(Pool.season == season)

    pools = query.group_by(Pool.username).with_entities(
        Pool.username,
        func.sum(Pool.amount).label('amount')
    ).all()

    formatted_pools = []
    for username, amount in pools:
        formatted_Pool = {
            'username': username,
            'amount': amount
        }
        formatted_pools.append(formatted_Pool)

    return jsonify(formatted_pools)

@pools_bp.route("/api/v1/Pooldetails")
def get_Pool_details():
    season = request.args.get('season')
    username = request.args.get('username')
    query = Pool.query

    if season is not None:
        query = query.filter_by(season=season)
    if username is not None:
        query = query.filter_by(username=username)

    detailed_pools = query.all()
    formatted_detailed_pools = []
    for Pool in detailed_pools:
        formatted_Pool = {
            'pool': Pool.pool_id,
            'amount': Pool.amount,
            'week': int(Pool.week),
            'username': Pool.username,
            'paid': Pool.paid,
            'season': int(Pool.season)
        }
        formatted_detailed_pools.append(formatted_Pool)
    return jsonify(formatted_detailed_pools)

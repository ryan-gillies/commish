from flask import Blueprint, jsonify, request
from sqlalchemy import func
from ..models.pool import Pool

pools_bp = Blueprint('pools', __name__)

@pools_bp.route("/api/v1/pools/seasons")
def get_Pool_seasons():
    Pool_seasons = Pool.query.with_entities(Pool.league.season).distinct().all()
    formatted_Pool_seasons = [season[0] for season in Pool_seasons]
    return jsonify(formatted_Pool_seasons)

@pools_bp.route("/api/v1/pools")
def get_pools():
    season = request.args.get('season')
    username = request.args.get('username')
    
    from models.league import League
    if season is not None:
        pools = Pool.query.join(League, Pool.league_id == League.league_id).filter(League.season == season).all()
    else:
        pools = Pool.query.all()
    if username is not None:
        pools = [pool for pool in pools if pool.winner == username]
    
    pools = [pool.to_dict() for pool in pools]
    return jsonify(pools)

@pools_bp.route("/api/v1/pools/<league_id>/<pool_id>")
def get_pool(league_id, pool_id):
    pool = Pool.query.filter(Pool.league_id == league_id, Pool.pool_id == pool_id).first()
    return jsonify(pool.to_dict())

@pools_bp.route("/api/v1/pools/leaderboard", methods=["GET"])
def get_pool_leaderboard():
    league_id = request.args.get('league_id')
    pool_id = request.args.get('pool_id')
    pool = Pool.query.filter(Pool.league_id == league_id, Pool.pool_id == pool_id).first()
    try:
        leaderboard = pool.get_leaderboard()
        return jsonify(leaderboard)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

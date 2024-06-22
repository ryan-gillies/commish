from flask import Blueprint, jsonify, request
from sqlalchemy import func
from ..models.pool import Pool
from ..models.league import League

leagues_bp = Blueprint('leagues', __name__)

@leagues_bp.route("/api/v1/leagues", methods=['GET'])
def get_leagues():
    leagues = League.query.all()
    return jsonify([league.to_dict() for league in leagues])

@leagues_bp.route("/api/v1/leagues/<league_id>", methods=['GET'])
def get_league(league_id=None):
    league = League.query.get_or_404(league_id)
    return jsonify(league.to_dict())
        
@leagues_bp.route("/api/v1/leagues/seasons", methods=['GET'])
def get_seasons():
    seasons = League.query.with_entities(League.season).distinct().all()
    formatted_seasons = [season[0] for season in seasons]
    formatted_seasons.sort(reverse=True)
    return jsonify(formatted_seasons)

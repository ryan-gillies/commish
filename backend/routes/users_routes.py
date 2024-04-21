from flask import Blueprint, jsonify, request
from models.user import User
from extensions import db

users_bp = Blueprint('users', __name__)

@users_bp.route("/api/v1/users", methods=['GET'])
def get_users():
    users = User.query.all()
    formatted_users = [user.to_dict() for user in users]
    return jsonify(formatted_users)

@users_bp.route("/api/v1/users/<username>", methods=['GET'])
def get_user(username):
    user = User.query.get(username)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict())

@users_bp.route("/api/v1/users/<username>/rosters", methods=['GET'])
def get_user_rosters(username):
    user = User.query.get(username)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify([roster.to_dict() for roster in user.rosters])

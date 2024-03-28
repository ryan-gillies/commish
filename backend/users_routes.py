# from flask import Blueprint, jsonify
# from payouts import User

# users_bp = Blueprint('users', __name__)

# @users_bp.route("/api/v1/users")
# def retrieve_users():
#     users = User.query.all()
#     formatted_users = []
#     for user in users:
#         formatted_user = {
#             'username': user.username,
#             'venmo_id': user.venmo_id,
#             'name': user.name,
#             'active': user.active,
#             'user_id': user.user_id,
#         }
#         formatted_users.append(formatted_user)
#     return jsonify(formatted_users)

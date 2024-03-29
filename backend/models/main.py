# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from league import League
# from user import User
# import sleeperpy

# # Create a Flask application
# app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = (
#     "postgresql://retool:ZHVhmOA2Tb4i@ep-icy-salad-54868721.us-west-2.retooldb.com/retool?sslmode=require"
# )

# # Initialize Flask-SQLAlchemy
# db = SQLAlchemy(app)

# # Define SQLAlchemy models (e.g., User) in the user.py file

# # Create an application context
# app_context = app.app_context()
# app_context.push()

# # Now you can use Flask-SQLAlchemy models and other Flask extensions
# league = League("2023")
# users = sleeperpy.Leagues.get_users(league.league_id)
# for user_data in users:
#     user = User(user_data, league)

# # Don't forget to pop the application context when done
# app_context.pop()

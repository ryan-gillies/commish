from flask import Flask
from flask.helpers import send_from_directory
from dotenv import load_dotenv
import os
from .extensions import db
from .routes.payouts_routes import payouts_bp
from .routes.pools_routes import pools_bp
from .routes.leagues_routes import leagues_bp
from .routes.users_routes import users_bp
from .models.league import League

load_dotenv()
postgresql = os.environ.get("postgresql")

app = Flask(__name__, static_folder='./build', static_url_path='/')
app.config["SQLALCHEMY_DATABASE_URI"] = (postgresql)

db.init_app(app)

# Create Tables
with app.app_context():
    db.create_all()
    league = League(2023)

# Register Blueprints
app.register_blueprint(payouts_bp)
app.register_blueprint(pools_bp)
app.register_blueprint(leagues_bp)
app.register_blueprint(users_bp)

@app.route('/')
def serve():
    return send_from_directory(app.static_folder, 'index.html')


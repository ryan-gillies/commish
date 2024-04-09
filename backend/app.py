from flask import Flask
from extensions import db
from routes.payouts_routes import payouts_bp
from routes.pools_routes import pools_bp
from models.league import League
from models.user import User
import sleeperpy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql://retool:ZHVhmOA2Tb4i@ep-icy-salad-54868721.us-west-2.retooldb.com/retool?sslmode=require"
)
db.init_app(app)
with app.app_context():
    db.create_all()
    league = League("2020")
    # users = sleeperpy.Leagues.get_users(league.league_id)
    # for user_data in users:
    #     user = User(user_data, league.league_id)
    for pool in league.pools:
        pool.set_winner()


# Register Blueprints
app.register_blueprint(payouts_bp)
app.register_blueprint(pools_bp)

if __name__ == "__main__":
    app.run(debug=True)

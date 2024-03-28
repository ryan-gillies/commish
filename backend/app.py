from flask import Flask
from pools.payout import db
from routes.payouts_routes import payouts_bp
# from users_routes import users_bp

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql://retool:ZHVhmOA2Tb4i@ep-icy-salad-54868721.us-west-2.retooldb.com/retool?sslmode=require"
)
db.init_app(app)

# Register Blueprints
app.register_blueprint(payouts_bp)
# app.register_blueprint(users_bp)

if __name__ == "__main__":
    app.run(debug=True)

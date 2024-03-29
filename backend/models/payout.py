import logging
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class Payout(db.Model):
    __tablename__ = 'payouts'

    pool_id = db.Column(db.String, db.ForeignKey('pools.pool_id'), primary_key=True)
    amount = db.Column(db.Float)
    week = db.Column(db.Integer)
    venmo_id = db.Column(db.String, db.ForeignKey('users.venmo_id'))
    paid = db.Column(db.Boolean)
    league_id = db.Column(db.String, db.ForeignKey('pools.league_id'), primary_key=True)
    season = db.Column(db.Integer)
    
    pool = relationship("Pool", backref="payouts")

    def save_to_database(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logging.error(f"Failed to add payout to database: {e}")
            raise
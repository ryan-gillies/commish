import logging
from sqlalchemy.orm import relationship
from extensions import db
from .pool import Pool

class Payout(db.Model):
    __tablename__ = 'payouts'

    pool_id = db.Column(db.String, db.ForeignKey('pools.pool_id'), primary_key=True)
    amount = db.Column(db.Float)
    week = db.Column(db.Integer)
    username = db.Column(db.String)
    paid = db.Column(db.Boolean)
    league_id = db.Column(db.String, primary_key=True)
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
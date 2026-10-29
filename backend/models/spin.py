from database.db import db


class Spin(db.Model):
    """Een van de laatste spins, zodat de geschiedenis na het herstarten terug is."""

    __tablename__ = "spins"

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey("players.id"), nullable=False)
    number = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String(10), nullable=False)
    net = db.Column(db.Float, nullable=False)
    source = db.Column(db.String(10), nullable=False)

    player = db.relationship("Player", back_populates="spins")

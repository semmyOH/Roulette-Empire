from database.db import db


class PlayerUpgrade(db.Model):
    """Niveau van één upgrade voor een speler. Het aantal bots is het niveau van `junior_bot`."""

    __tablename__ = "player_upgrades"
    __table_args__ = (db.UniqueConstraint("player_id", "upgrade_id"),)

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey("players.id"), nullable=False)
    upgrade_id = db.Column(db.String(50), nullable=False)
    level = db.Column(db.Integer, nullable=False, default=0)

    player = db.relationship("Player", back_populates="upgrades")

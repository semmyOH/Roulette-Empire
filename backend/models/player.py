from datetime import datetime, timezone

from database.db import db
from game.config.balance import REPUTATION_START, STARTING_BALANCE


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Player(db.Model):
    __tablename__ = "players"

    id = db.Column(db.Integer, primary_key=True)
    balance = db.Column(db.Float, nullable=False, default=STARTING_BALANCE)
    total_won = db.Column(db.Float, nullable=False, default=0.0)
    total_lost = db.Column(db.Float, nullable=False, default=0.0)
    total_upkeep = db.Column(db.Float, nullable=False, default=0.0)
    bot_timer = db.Column(db.Float, nullable=False, default=0.0)

    # Voor het toekomstige reputatie- en schuldensysteem.
    reputation = db.Column(db.Integer, nullable=False, default=REPUTATION_START)
    debt = db.Column(db.Float, nullable=False, default=0.0)

    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)

    upgrades = db.relationship("PlayerUpgrade", back_populates="player", cascade="all, delete-orphan")
    spins = db.relationship("Spin", back_populates="player", cascade="all, delete-orphan", order_by="Spin.id")

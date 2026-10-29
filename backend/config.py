"""Serverinstellingen. Balanswaarden van het spel staan in game/config/balance.py."""

import os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent


class Config:
    FRONTEND_DIR = Path(os.environ.get("ROULETTE_FRONTEND_DIR", BACKEND_DIR.parent / "Frontend"))
    DATABASE_PATH = Path(os.environ.get("ROULETTE_DATABASE", BACKEND_DIR / "database" / "roulette_empire.db"))

    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATABASE_PATH.as_posix()}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_AS_ASCII = False

    DEBUG = os.environ.get("FLASK_DEBUG", "1") == "1"
    PORT = int(os.environ.get("PORT", "5000"))

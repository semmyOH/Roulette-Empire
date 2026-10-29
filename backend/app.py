"""Startpunt van de Roulette Empire-server. Starten: python app.py (vanuit de map backend)."""

import atexit
import sys
from pathlib import Path

# De map met spellogica (/game) staat naast /backend; maak hem importeerbaar.
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from flask import Flask, render_template  # noqa: E402

from config import Config  # noqa: E402
from database.db import init_db  # noqa: E402
from routes import register_routes  # noqa: E402
from services import build_game_service  # noqa: E402


def create_app(config: type[Config] = Config) -> Flask:
    app = Flask(
        __name__,
        template_folder=str(config.FRONTEND_DIR / "templates"),
        static_folder=str(config.FRONTEND_DIR),
        static_url_path="/static",
    )
    app.config.from_object(config)

    init_db(app)
    service = build_game_service()
    app.extensions["game_service"] = service
    register_routes(app)

    @app.get("/")
    def index():
        return render_template("index.html")

    def save_on_exit():
        with app.app_context():
            service.save_if_loaded()

    atexit.register(save_on_exit)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=Config.DEBUG, port=Config.PORT)

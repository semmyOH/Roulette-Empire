"""Zet fouten om in JSON ({"error": "..."}), zodat de frontend ze kan tonen."""

from flask import request
from werkzeug.exceptions import HTTPException

from game.errors import GameError, UnknownUpgradeError


def register_error_handlers(app) -> None:
    @app.errorhandler(GameError)
    def handle_game_error(error: GameError):
        status = 404 if isinstance(error, UnknownUpgradeError) else 400
        return {"error": str(error)}, status

    @app.errorhandler(HTTPException)
    def handle_http_error(error: HTTPException):
        if not request.path.startswith("/api/"):
            return error
        return {"error": error.description}, error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        app.logger.exception("Onverwachte fout")
        return {"error": "Er ging iets mis op de server."}, 500

from flask import Blueprint, current_app, request

from services.game_service import GameService

game_bp = Blueprint("game", __name__, url_prefix="/api")


def game_service() -> GameService:
    return current_app.extensions["game_service"]


@game_bp.get("/state")
def get_state():
    return game_service().get_state()


@game_bp.post("/spin")
def spin():
    payload = request.get_json(silent=True) or {}
    record, bet_results, state = game_service().spin(payload)
    result = record.to_dict() | {
        "total_bet": sum(bet["amount"] for bet in bet_results),
        "bets": bet_results,
    }
    return {"result": result, "state": state}


@game_bp.post("/save")
def save():
    saved_at = game_service().save()
    return {"saved_at": saved_at.isoformat()}


@game_bp.post("/reset")
def reset():
    return {"state": game_service().reset()}

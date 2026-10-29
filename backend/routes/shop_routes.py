from flask import Blueprint

from routes.game_routes import game_service

shop_bp = Blueprint("shop", __name__, url_prefix="/api")


@shop_bp.post("/upgrades/<upgrade_id>/buy")
def buy_upgrade(upgrade_id: str):
    return {"state": game_service().buy_upgrade(upgrade_id)}

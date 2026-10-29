from flask import Blueprint, jsonify
from models.player import Player
from services.roulette_service import spin_roulette

game_bp = Blueprint("game", __name__)

player = Player()


@game_bp.route("/spin", methods=["POST"])
def spin():

    result = spin_roulette()

    player.money += result

    return jsonify({
        "money": player.money,
        "result": result
    })


@game_bp.route("/state", methods=["GET"])
def get_state():

    return jsonify({
        "money": player.money,
        "reputation": player.reputation,
        "debt": player.debt
    })
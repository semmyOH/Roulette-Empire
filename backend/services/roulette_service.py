from __future__ import annotations

from game.errors import GameError
from game.modifiers import Modifiers
from game.roulette import Bet, RouletteWheel, color_of
from game.state import GameState, SpinRecord


class RouletteService:
    """Speelt één spin voor de speler of een bot en verwerkt winst of verlies."""

    def __init__(self, wheel: RouletteWheel | None = None):
        self.wheel = wheel or RouletteWheel()

    def play(self, state: GameState, bet: Bet, modifiers: Modifiers, source: str) -> SpinRecord:
        if bet.amount > state.balance:
            raise GameError("Onvoldoende saldo voor deze inzet.")

        number = self.wheel.spin(bet, modifiers.win_chance_multiplier)
        if bet.wins(number):
            net = round(bet.amount * bet.payout_ratio * modifiers.payout_multiplier, 2)
        else:
            net = -float(bet.amount)

        record = SpinRecord(number, color_of(number), net, source)
        state.record_spin(record)
        return record

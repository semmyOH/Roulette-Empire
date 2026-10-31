from __future__ import annotations

from collections.abc import Sequence

from game.errors import GameError
from game.modifiers import Modifiers
from game.roulette import Bet, RouletteWheel, color_of
from game.state import GameState, SpinRecord


class RouletteService:
    """Speelt één spin met één of meer inzetten, voor de speler of een bot, en verwerkt het resultaat."""

    def __init__(self, wheel: RouletteWheel | None = None):
        self.wheel = wheel or RouletteWheel()

    def play(
        self, state: GameState, bets: Sequence[Bet], modifiers: Modifiers, source: str
    ) -> tuple[SpinRecord, list[dict]]:
        if sum(bet.amount for bet in bets) > state.balance:
            raise GameError("Onvoldoende saldo voor deze inzet.")

        number = self.wheel.spin(bets, modifiers.win_chance_multiplier)
        bet_results = [bet.to_dict() | {"net": bet.net(number, modifiers.payout_multiplier)} for bet in bets]
        net = round(sum(result["net"] for result in bet_results), 2)

        record = SpinRecord(number, color_of(number), net, source)
        state.record_spin(record)
        return record, bet_results

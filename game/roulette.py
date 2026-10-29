"""Regels van Europese roulette: vakken, kleuren, inzetten en het draaien van het wiel."""

from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum

from game.config.balance import MAX_WIN_CHANCE, MIN_BET
from game.errors import InvalidBetError

NUMBERS = range(37)
RED_NUMBERS = frozenset({1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36})


def color_of(number: int) -> str:
    if number == 0:
        return "green"
    return "red" if number in RED_NUMBERS else "black"


class BetType(str, Enum):
    RED = "red"
    BLACK = "black"
    EVEN = "even"
    ODD = "odd"
    NUMBER = "number"


# Winst per ingezette euro (1:1 of 35:1).
PAYOUT_RATIOS = {
    BetType.RED: 1,
    BetType.BLACK: 1,
    BetType.EVEN: 1,
    BetType.ODD: 1,
    BetType.NUMBER: 35,
}


def _is_whole_number(value) -> bool:
    if isinstance(value, bool):
        return False
    return isinstance(value, int) or (isinstance(value, float) and value.is_integer())


@dataclass(frozen=True)
class Bet:
    bet_type: BetType
    amount: int
    number: int | None = None

    @classmethod
    def from_dict(cls, data: dict) -> Bet:
        try:
            bet_type = BetType(data.get("bet_type"))
        except ValueError:
            raise InvalidBetError("Kies rood, zwart, even, oneven of een getal.") from None

        amount = data.get("amount")
        if not _is_whole_number(amount) or amount < MIN_BET:
            raise InvalidBetError(f"De inzet moet een heel bedrag van minimaal €{MIN_BET} zijn.")

        number = data.get("number")
        if bet_type is BetType.NUMBER:
            if not _is_whole_number(number) or not 0 <= number <= 36:
                raise InvalidBetError("Kies een getal van 0 tot en met 36.")
            number = int(number)
        else:
            number = None

        return cls(bet_type, int(amount), number)

    def wins(self, number: int) -> bool:
        if self.bet_type is BetType.NUMBER:
            return number == self.number
        if number == 0:
            return False
        if self.bet_type is BetType.RED:
            return color_of(number) == "red"
        if self.bet_type is BetType.BLACK:
            return color_of(number) == "black"
        if self.bet_type is BetType.EVEN:
            return number % 2 == 0
        return number % 2 == 1

    def winning_numbers(self) -> list[int]:
        return [n for n in NUMBERS if self.wins(n)]

    @property
    def payout_ratio(self) -> int:
        return PAYOUT_RATIOS[self.bet_type]


class RouletteWheel:
    def __init__(self, rng: random.Random | None = None, max_win_chance: float = MAX_WIN_CHANCE):
        self.rng = rng or random.Random()
        self.max_win_chance = max_win_chance

    def spin(self, bet: Bet, win_chance_multiplier: float = 1.0) -> int:
        """Draait het wiel. Met een multiplier boven 1 wordt een verlies soms omgezet in winst,
        zodat de winstkans precies `basiskans × multiplier` wordt (tot `max_win_chance`)."""
        number = self.rng.choice(NUMBERS)
        if bet.wins(number) or win_chance_multiplier <= 1:
            return number

        winners = bet.winning_numbers()
        base_chance = len(winners) / len(NUMBERS)
        target_chance = min(base_chance * win_chance_multiplier, self.max_win_chance)
        if target_chance <= base_chance:
            return number

        rescue_chance = (target_chance - base_chance) / (1 - base_chance)
        if self.rng.random() < rescue_chance:
            return self.rng.choice(winners)
        return number

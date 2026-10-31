"""Regels van Europese roulette: vakken, kleuren, inzetten en het draaien van het wiel."""

from __future__ import annotations

import random
from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache

from game.config.balance import MAX_BETS_PER_SPIN, MAX_WIN_CHANCE, MIN_BET
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
    DOZEN = "dozen"  # 1e, 2e of 3e 12
    COLUMN = "column"  # "2 to 1": kolom 1 (1, 4, 7, ...), 2 (2, 5, 8, ...) of 3 (3, 6, 9, ...)
    STREET = "street"  # Straat: 3 getallen op een rij, straat 1 = 1-2-3 t/m straat 12 = 34-35-36
    NUMBER = "number"


# Winst per ingezette euro.
PAYOUT_RATIOS = {
    BetType.RED: 1,
    BetType.BLACK: 1,
    BetType.EVEN: 1,
    BetType.ODD: 1,
    BetType.DOZEN: 2,
    BetType.COLUMN: 2,
    BetType.STREET: 11,
    BetType.NUMBER: 35,
}

# Inzetten die een `value` nodig hebben: (laagste, hoogste, foutmelding).
VALUE_RULES = {
    BetType.NUMBER: (0, 36, "Kies een getal van 0 tot en met 36."),
    BetType.STREET: (1, 12, "Kies een straat van 1 tot en met 12."),
    BetType.DOZEN: (1, 3, "Kies het 1e, 2e of 3e dozijn."),
    BetType.COLUMN: (1, 3, "Kies kolom 1, 2 of 3."),
}


@lru_cache(maxsize=None)
def covered_numbers(bet_type: BetType, value: int | None) -> frozenset[int]:
    """Alle getallen waarmee deze inzet wint."""
    if bet_type is BetType.NUMBER:
        return frozenset({value})
    if bet_type is BetType.STREET:
        return frozenset(range(3 * value - 2, 3 * value + 1))
    if bet_type is BetType.DOZEN:
        return frozenset(range(12 * value - 11, 12 * value + 1))

    numbers = range(1, 37)
    if bet_type is BetType.COLUMN:
        return frozenset(n for n in numbers if n % 3 == value % 3)
    if bet_type is BetType.RED:
        return RED_NUMBERS
    if bet_type is BetType.BLACK:
        return frozenset(numbers) - RED_NUMBERS
    if bet_type is BetType.EVEN:
        return frozenset(n for n in numbers if n % 2 == 0)
    return frozenset(n for n in numbers if n % 2 == 1)


def _is_whole_number(value) -> bool:
    if isinstance(value, bool):
        return False
    return isinstance(value, int) or (isinstance(value, float) and value.is_integer())


@dataclass(frozen=True)
class Bet:
    bet_type: BetType
    amount: int
    value: int | None = None  # Getal, straat, dozijn of kolom; leeg bij rood/zwart/even/oneven.

    @classmethod
    def from_dict(cls, data) -> Bet:
        if not isinstance(data, dict):
            raise InvalidBetError("Ongeldige inzet.")
        try:
            bet_type = BetType(data.get("bet_type"))
        except ValueError:
            raise InvalidBetError("Onbekend soort inzet.") from None

        amount = data.get("amount")
        if not _is_whole_number(amount) or amount < MIN_BET:
            raise InvalidBetError(f"Elke inzet moet een heel bedrag van minimaal €{MIN_BET} zijn.")

        value = None
        if bet_type in VALUE_RULES:
            low, high, message = VALUE_RULES[bet_type]
            value = data.get("value")
            if not _is_whole_number(value) or not low <= value <= high:
                raise InvalidBetError(message)
            value = int(value)

        return cls(bet_type, int(amount), value)

    def to_dict(self) -> dict:
        return {"bet_type": self.bet_type.value, "value": self.value, "amount": self.amount}

    def numbers(self) -> frozenset[int]:
        return covered_numbers(self.bet_type, self.value)

    def wins(self, number: int) -> bool:
        return number in self.numbers()

    @property
    def payout_ratio(self) -> int:
        return PAYOUT_RATIOS[self.bet_type]

    def net(self, number: int, payout_multiplier: float = 1.0) -> float:
        if self.wins(number):
            return round(self.amount * self.payout_ratio * payout_multiplier, 2)
        return -float(self.amount)


def parse_bets(payload: dict) -> list[Bet]:
    """Leest de inzetten van één spin: `{"bets": [...]}` of één losse inzet."""
    raw = payload.get("bets", [payload]) if isinstance(payload, dict) else None
    if not isinstance(raw, list) or not raw:
        raise InvalidBetError("Plaats minstens één inzet.")
    if len(raw) > MAX_BETS_PER_SPIN:
        raise InvalidBetError(f"Je kunt maximaal {MAX_BETS_PER_SPIN} inzetten per spin plaatsen.")
    return [Bet.from_dict(item) for item in raw]


def total_net(bets: Sequence[Bet], number: int, payout_multiplier: float = 1.0) -> float:
    return sum(bet.net(number, payout_multiplier) for bet in bets)


class RouletteWheel:
    def __init__(self, rng: random.Random | None = None, max_win_chance: float = MAX_WIN_CHANCE):
        self.rng = rng or random.Random()
        self.max_win_chance = max_win_chance

    def spin(self, bets: Sequence[Bet], win_chance_multiplier: float = 1.0) -> int:
        """Draait het wiel. Een spin is "gewonnen" als alle inzetten samen winst opleveren.
        Met een multiplier boven 1 wordt een verlies soms omgezet in winst, zodat de winstkans precies
        `basiskans × multiplier` wordt (tot `max_win_chance`)."""
        number = self.rng.choice(NUMBERS)
        if win_chance_multiplier <= 1 or total_net(bets, number) > 0:
            return number

        winners = [n for n in NUMBERS if total_net(bets, n) > 0]
        if not winners:
            return number
        base_chance = len(winners) / len(NUMBERS)
        target_chance = min(base_chance * win_chance_multiplier, self.max_win_chance)
        if target_chance <= base_chance:
            return number

        rescue_chance = (target_chance - base_chance) / (1 - base_chance)
        if self.rng.random() < rescue_chance:
            return self.rng.choice(winners)
        return number

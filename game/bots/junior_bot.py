from __future__ import annotations

import random

from game.bots.base import Bot
from game.config.balance import JUNIOR_BOT_BET, JUNIOR_BOT_INTERVAL_SECONDS
from game.roulette import Bet, BetType


class JuniorRouletteBot(Bot):
    """Zet elke ronde een vast bedrag in op rood of zwart."""

    bot_type = "junior"

    def __init__(self, rng: random.Random | None = None):
        self.rng = rng or random.Random()
        self.interval_seconds = JUNIOR_BOT_INTERVAL_SECONDS
        self.bet_amount = JUNIOR_BOT_BET

    def choose_bet(self, balance: float) -> Bet | None:
        if balance < self.bet_amount:
            return None
        return Bet(self.rng.choice([BetType.RED, BetType.BLACK]), self.bet_amount)

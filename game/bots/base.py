from __future__ import annotations

from abc import ABC, abstractmethod

from game.roulette import Bet


class Bot(ABC):
    """Een bot speelt automatisch roulette. Hij gebruikt hetzelfde wiel en dezelfde upgrades als de speler."""

    bot_type: str
    interval_seconds: float

    @abstractmethod
    def choose_bet(self, balance: float) -> Bet | None:
        """Kiest de volgende inzet, of None als de bot deze ronde overslaat."""

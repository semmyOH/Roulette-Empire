from __future__ import annotations

from abc import ABC, abstractmethod

from game.config.balance import UPGRADE_PRICE_GROWTH
from game.modifiers import Modifiers


class Upgrade(ABC):
    """Een koopbare upgrade. Subklassen bepalen alleen wat het effect is op de Modifiers."""

    def __init__(
        self,
        upgrade_id: str,
        name: str,
        description: str,
        base_price: float,
        value: float,
        max_level: int | None = None,
        price_growth: float = UPGRADE_PRICE_GROWTH,
    ):
        self.id = upgrade_id
        self.name = name
        self.description = description
        self.base_price = base_price
        self.value = value
        self.max_level = max_level
        self.price_growth = price_growth

    def price(self, level: int) -> float:
        return round(self.base_price * self.price_growth**level, 2)

    def can_buy(self, level: int) -> bool:
        return self.max_level is None or level < self.max_level

    @abstractmethod
    def apply(self, modifiers: Modifiers, level: int) -> None:
        """Past het effect van `level` niveaus van deze upgrade toe."""

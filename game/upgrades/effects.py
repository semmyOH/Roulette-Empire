"""De soorten upgrade-effecten. Een nieuw soort effect = een nieuwe subklasse hier."""

from game.modifiers import Modifiers
from game.upgrades.base import Upgrade


class WinChanceUpgrade(Upgrade):
    def apply(self, modifiers: Modifiers, level: int) -> None:
        modifiers.win_chance_multiplier *= 1 + self.value * level


class PayoutUpgrade(Upgrade):
    def apply(self, modifiers: Modifiers, level: int) -> None:
        modifiers.payout_multiplier *= 1 + self.value * level


class UpkeepUpgrade(Upgrade):
    def apply(self, modifiers: Modifiers, level: int) -> None:
        modifiers.upkeep_multiplier *= (1 - self.value) ** level


class BotUpgrade(Upgrade):
    def apply(self, modifiers: Modifiers, level: int) -> None:
        modifiers.bot_count += int(self.value * level)

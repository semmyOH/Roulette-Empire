from dataclasses import dataclass

from game.modifiers import Modifiers


@dataclass(frozen=True)
class GameEvent:
    """Een tijdelijk event dat winsten, kosten en reputatie kan beïnvloeden."""

    event_id: str
    name: str
    description: str
    duration_seconds: float
    win_chance_multiplier: float = 1.0
    payout_multiplier: float = 1.0
    upkeep_multiplier: float = 1.0
    reputation_change: int = 0
    min_reputation: int = 0  # Pas mogelijk vanaf deze reputatie (bijvoorbeeld voor sponsordeals).

    def apply(self, modifiers: Modifiers) -> None:
        modifiers.win_chance_multiplier *= self.win_chance_multiplier
        modifiers.payout_multiplier *= self.payout_multiplier
        modifiers.upkeep_multiplier *= self.upkeep_multiplier

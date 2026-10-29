from dataclasses import dataclass


@dataclass
class Modifiers:
    """Alle effecten op het spel samen. Upgrades vullen dit nu in, later ook events en risicoprofielen."""

    win_chance_multiplier: float = 1.0
    payout_multiplier: float = 1.0
    upkeep_multiplier: float = 1.0
    bot_count: int = 0

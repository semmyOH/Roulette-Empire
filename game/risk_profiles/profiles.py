from __future__ import annotations

import random
from dataclasses import dataclass

from game.roulette import Bet, BetType


@dataclass(frozen=True)
class RiskProfile:
    """Bepaalt hoe riskant bots spelen: welk deel van het saldo ze inzetten en op welke vakken.

    Koppelen: laat de speler een profiel kiezen (opslaan bij Player) en geef het aan een bot, die dan
    `make_bet()` gebruikt in plaats van een vaste inzet.
    """

    profile_id: str
    name: str
    description: str
    bet_fraction: float  # Deel van het saldo per inzet.
    bet_types: tuple[BetType, ...]

    def make_bet(self, balance: float, rng: random.Random) -> Bet | None:
        amount = int(balance * self.bet_fraction)
        if amount < 1:
            return None
        bet_type = rng.choice(self.bet_types)
        number = rng.randint(0, 36) if bet_type is BetType.NUMBER else None
        return Bet(bet_type, amount, number)


_EVEN_MONEY = (BetType.RED, BetType.BLACK, BetType.EVEN, BetType.ODD)

RISK_PROFILES = {
    profile.profile_id: profile
    for profile in [
        RiskProfile("safe", "Veilig", "Lage risico's, lage opbrengsten.", 0.01, (BetType.RED, BetType.BLACK)),
        RiskProfile("balanced", "Gebalanceerd", "Gemiddeld risico, gemiddelde opbrengsten.", 0.03, _EVEN_MONEY),
        RiskProfile("aggressive", "Agressief", "Hoge volatiliteit.", 0.08, _EVEN_MONEY + (BetType.NUMBER,)),
        RiskProfile("maniac", "Maniak", "Extreem risico, zeer hoge potentiële winsten.", 0.2, (BetType.NUMBER,)),
    ]
}

from game.config.balance import REPUTATION_START


class Reputation:
    """Reputatie van het casino, altijd tussen 0 en 100.

    Bedoeld om events, sponsordeals en toernooien te beïnvloeden: gebruik `influence()` als factor
    (-1 bij reputatie 0, 0 bij 50, +1 bij 100). De waarde staat al in de database (Player.reputation).
    """

    MIN = 0
    MAX = 100

    def __init__(self, value: int = REPUTATION_START):
        self._value = self._clamp(value)

    @classmethod
    def _clamp(cls, value: float) -> int:
        return int(max(cls.MIN, min(cls.MAX, round(value))))

    @property
    def value(self) -> int:
        return self._value

    def change(self, delta: float) -> int:
        self._value = self._clamp(self._value + delta)
        return self._value

    def influence(self) -> float:
        middle = (self.MAX + self.MIN) / 2
        return (self._value - middle) / (self.MAX - middle)

    def allows(self, minimum: int) -> bool:
        return self._value >= minimum

"""De spelstatus van één speler, zoals die tijdens het spelen in het geheugen staat."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from game.config.balance import HISTORY_SIZE, MIN_BET, STARTING_BALANCE


@dataclass(frozen=True)
class SpinRecord:
    number: int
    color: str
    net: float
    source: str  # "player" of "bot"

    def to_dict(self) -> dict:
        return {"number": self.number, "color": self.color, "net": round(self.net, 2), "source": self.source}


@dataclass
class GameState:
    balance: float = STARTING_BALANCE
    total_won: float = 0.0
    total_lost: float = 0.0
    total_upkeep: float = 0.0
    bot_timer: float = 0.0
    upgrade_levels: dict[str, int] = field(default_factory=dict)
    history: deque[SpinRecord] = field(default_factory=lambda: deque(maxlen=HISTORY_SIZE))

    @property
    def net_profit(self) -> float:
        return self.total_won - self.total_lost

    @property
    def bankrupt(self) -> bool:
        """Blut: niet genoeg geld meer voor de kleinste inzet."""
        return self.balance < MIN_BET

    def level(self, upgrade_id: str) -> int:
        return self.upgrade_levels.get(upgrade_id, 0)

    def record_spin(self, record: SpinRecord) -> None:
        self.balance += record.net
        if record.net > 0:
            self.total_won += record.net
        else:
            self.total_lost -= record.net
        self.history.appendleft(record)

from __future__ import annotations

import random

from game.events.base import GameEvent
from game.events.catalog import EVENT_CATALOG
from game.reputation import Reputation


class EventScheduler:
    """Kiest willekeurige events. Koppelen: roep `maybe_start()` aan in de tick van GameService en
    pas actieve events toe op de Modifiers met `GameEvent.apply()`."""

    def __init__(self, chance_per_minute: float = 0.2, rng: random.Random | None = None,
                 catalog: dict[str, GameEvent] = EVENT_CATALOG):
        self.chance_per_minute = chance_per_minute
        self.rng = rng or random.Random()
        self.catalog = catalog

    def available_events(self, reputation: Reputation) -> list[GameEvent]:
        return [e for e in self.catalog.values() if reputation.allows(e.min_reputation)]

    def maybe_start(self, reputation: Reputation, elapsed_seconds: float) -> GameEvent | None:
        chance = self.chance_per_minute * elapsed_seconds / 60
        options = self.available_events(reputation)
        if not options or self.rng.random() >= chance:
            return None
        return self.rng.choice(options)

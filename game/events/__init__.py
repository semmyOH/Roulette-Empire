"""Willekeurige events (voorbereid, nog niet gekoppeld aan het spel)."""

from game.events.base import GameEvent
from game.events.catalog import EVENT_CATALOG
from game.events.scheduler import EventScheduler

__all__ = ["GameEvent", "EVENT_CATALOG", "EventScheduler"]

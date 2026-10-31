from __future__ import annotations

import threading
import time
from datetime import datetime

from game.config.balance import AUTOSAVE_INTERVAL_SECONDS, MAX_TICK_SECONDS
from game.errors import GameError
from game.modifiers import Modifiers
from game.roulette import parse_bets
from game.state import GameState, SpinRecord
from services.bot_service import BotService
from services.roulette_service import RouletteService
from services.save_service import SaveService
from services.upgrade_service import UpgradeService


class GameService:
    """Centrale plek voor alle spelacties. De routes praten alleen met deze klasse.

    De spelstatus staat in het geheugen en wordt opgeslagen in SQLite: handmatig, elke
    AUTOSAVE_INTERVAL_SECONDS en bij het afsluiten van de server. Voor elke actie wordt eerst de
    verstreken tijd verwerkt (botspins en hun onderhoudskosten).
    """

    def __init__(
        self,
        save_service: SaveService,
        roulette: RouletteService,
        bots: BotService,
        upgrades: UpgradeService,
        clock=time.monotonic,
    ):
        self.save_service = save_service
        self.roulette = roulette
        self.bots = bots
        self.upgrades = upgrades
        self.clock = clock
        self._lock = threading.RLock()
        self._state: GameState | None = None
        self._last_tick = 0.0
        self._last_save = 0.0

    # Acties

    def get_state(self) -> dict:
        with self._lock:
            self._tick()
            return self._serialize()

    def spin(self, payload: dict) -> tuple[SpinRecord, list[dict], dict]:
        """Speelt één spin met alle inzetten uit `payload`. Geeft de spin, de uitkomst per inzet en
        de nieuwe status terug."""
        with self._lock:
            self._tick()
            if self._state.bankrupt:
                raise GameError("Je bent blut. Begin opnieuw om verder te spelen.")
            bets = parse_bets(payload)
            record, bet_results = self.roulette.play(self._state, bets, self._modifiers(), source="player")
            return record, bet_results, self._serialize()

    def buy_upgrade(self, upgrade_id: str) -> dict:
        with self._lock:
            self._tick()
            self.upgrades.buy(self._state, upgrade_id)
            return self._serialize()

    def save(self) -> datetime:
        with self._lock:
            self._tick()
            return self._save()

    def reset(self) -> dict:
        with self._lock:
            self._ensure_loaded()
            self._state = GameState()
            self._save()
            return self._serialize()

    def save_if_loaded(self) -> None:
        """Voor het afsluiten van de server: alleen opslaan als er gespeeld is."""
        with self._lock:
            if self._state is not None:
                self._save()

    # Intern

    def _ensure_loaded(self) -> None:
        if self._state is None:
            self._state = self.save_service.load()
            self._last_tick = self._last_save = self.clock()

    def _tick(self) -> None:
        self._ensure_loaded()
        now = self.clock()
        elapsed = min(now - self._last_tick, MAX_TICK_SECONDS)
        self._last_tick = now

        if not self._state.bankrupt:
            self.bots.run(self._state, self._modifiers(), elapsed)

        if now - self._last_save >= AUTOSAVE_INTERVAL_SECONDS:
            self._save()

    def _save(self) -> datetime:
        self._last_save = self.clock()
        return self.save_service.save(self._state)

    def _modifiers(self) -> Modifiers:
        return self.upgrades.modifiers(self._state)

    def _serialize(self) -> dict:
        state = self._state
        modifiers = self._modifiers()
        upkeep_per_spin = self.bots.upkeep_per_spin(modifiers)
        return {
            "balance": round(state.balance, 2),
            "total_won": round(state.total_won, 2),
            "total_lost": round(state.total_lost, 2),
            "net_profit": round(state.net_profit, 2),
            "total_upkeep": round(state.total_upkeep, 2),
            "upkeep_per_spin": round(upkeep_per_spin, 2),
            "upkeep_per_round": round(upkeep_per_spin * modifiers.bot_count, 2),
            "bankrupt": state.bankrupt,
            "bots": {"active": modifiers.bot_count, "interval_seconds": self.bots.bot.interval_seconds},
            "upgrades": self.upgrades.describe(state),
            "history": [record.to_dict() for record in state.history],
        }

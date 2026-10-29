from __future__ import annotations

from datetime import datetime, timezone

from database.db import db
from game.state import GameState, SpinRecord
from models import Player, PlayerUpgrade, Spin


class SaveService:
    """Laadt en bewaart de spelstatus in SQLite. Er is één savegame (speler 1)."""

    PLAYER_ID = 1

    def load(self) -> GameState:
        player = db.session.get(Player, self.PLAYER_ID)
        if player is None:
            return GameState()

        state = GameState(
            balance=player.balance,
            total_won=player.total_won,
            total_lost=player.total_lost,
            total_upkeep=player.total_upkeep,
            bot_timer=player.bot_timer,
            upgrade_levels={u.upgrade_id: u.level for u in player.upgrades if u.level > 0},
        )
        # player.spins staat van oud naar nieuw; de geschiedenis van nieuw naar oud.
        for spin in player.spins:
            state.history.appendleft(SpinRecord(spin.number, spin.color, spin.net, spin.source))
        return state

    def save(self, state: GameState) -> datetime:
        player = db.session.get(Player, self.PLAYER_ID)
        if player is None:
            player = Player(id=self.PLAYER_ID)
            db.session.add(player)

        player.balance = state.balance
        player.total_won = state.total_won
        player.total_lost = state.total_lost
        player.total_upkeep = state.total_upkeep
        player.bot_timer = state.bot_timer

        # Bestaande rijen bijwerken in plaats van vervangen, vanwege de unieke (speler, upgrade)-combinatie.
        existing = {u.upgrade_id: u for u in player.upgrades}
        for upgrade_id in existing.keys() | state.upgrade_levels.keys():
            row = existing.get(upgrade_id)
            if row is None:
                row = PlayerUpgrade(upgrade_id=upgrade_id)
                player.upgrades.append(row)
            row.level = state.level(upgrade_id)

        player.spins = [
            Spin(number=r.number, color=r.color, net=r.net, source=r.source) for r in reversed(state.history)
        ]

        db.session.commit()
        return datetime.now(timezone.utc)

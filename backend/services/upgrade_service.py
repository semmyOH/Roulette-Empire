from __future__ import annotations

from game.errors import GameError, UnknownUpgradeError
from game.modifiers import Modifiers
from game.state import GameState
from game.upgrades import UPGRADE_CATALOG, Upgrade, compute_modifiers


class UpgradeService:
    def __init__(self, catalog: dict[str, Upgrade] = UPGRADE_CATALOG):
        self.catalog = catalog

    def modifiers(self, state: GameState) -> Modifiers:
        return compute_modifiers(state.upgrade_levels, self.catalog)

    def buy(self, state: GameState, upgrade_id: str) -> Upgrade:
        upgrade = self.catalog.get(upgrade_id)
        if upgrade is None:
            raise UnknownUpgradeError("Deze upgrade bestaat niet.")

        level = state.level(upgrade_id)
        if not upgrade.can_buy(level):
            raise GameError(f"{upgrade.name} is al op het maximale niveau.")

        price = upgrade.price(level)
        if state.balance < price:
            raise GameError(f"Onvoldoende saldo voor {upgrade.name}.")

        state.balance -= price
        state.upgrade_levels[upgrade_id] = level + 1
        return upgrade

    def describe(self, state: GameState) -> list[dict]:
        return [
            {
                "id": upgrade.id,
                "name": upgrade.name,
                "description": upgrade.description,
                "level": state.level(upgrade.id),
                "price": upgrade.price(state.level(upgrade.id)),
                "max_level": upgrade.max_level,
            }
            for upgrade in self.catalog.values()
        ]

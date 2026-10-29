"""Bouwt de upgradewinkel op uit de balanswaarden in game/config/balance.py."""

from __future__ import annotations

from game.config.balance import UPGRADES
from game.modifiers import Modifiers
from game.upgrades.base import Upgrade
from game.upgrades.effects import BotUpgrade, PayoutUpgrade, UpkeepUpgrade, WinChanceUpgrade

EFFECT_TYPES: dict[str, type[Upgrade]] = {
    "win_chance": WinChanceUpgrade,
    "payout": PayoutUpgrade,
    "upkeep": UpkeepUpgrade,
    "bots": BotUpgrade,
}


def build_catalog(definitions: dict = UPGRADES) -> dict[str, Upgrade]:
    catalog = {}
    for upgrade_id, d in definitions.items():
        upgrade_class = EFFECT_TYPES[d["effect"]]
        catalog[upgrade_id] = upgrade_class(
            upgrade_id=upgrade_id,
            name=d["name"],
            description=d["description"],
            base_price=d["base_price"],
            value=d["value"],
            max_level=d.get("max_level"),
        )
    return catalog


UPGRADE_CATALOG = build_catalog()


def compute_modifiers(levels: dict[str, int], catalog: dict[str, Upgrade] = UPGRADE_CATALOG) -> Modifiers:
    modifiers = Modifiers()
    for upgrade_id, level in levels.items():
        if level > 0 and upgrade_id in catalog:
            catalog[upgrade_id].apply(modifiers, level)
    return modifiers

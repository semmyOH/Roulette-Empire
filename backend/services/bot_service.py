from __future__ import annotations

from game.bots import Bot, JuniorRouletteBot
from game.config.balance import UPKEEP_PER_BOT_SPIN
from game.modifiers import Modifiers
from game.state import GameState
from services.roulette_service import RouletteService


class BotService:
    """Laat de gekochte bots spelen naarmate de speltijd verstrijkt. Elke botspin kost onderhoud."""

    def __init__(self, roulette: RouletteService, bot: Bot | None = None):
        self.roulette = roulette
        self.bot = bot or JuniorRouletteBot()

    @staticmethod
    def upkeep_per_spin(modifiers: Modifiers) -> float:
        return UPKEEP_PER_BOT_SPIN * modifiers.upkeep_multiplier

    def run(self, state: GameState, modifiers: Modifiers, elapsed: float) -> None:
        if modifiers.bot_count == 0:
            state.bot_timer = 0.0
            return

        upkeep = self.upkeep_per_spin(modifiers)
        state.bot_timer += elapsed
        while state.bot_timer >= self.bot.interval_seconds:
            state.bot_timer -= self.bot.interval_seconds
            for _ in range(modifiers.bot_count):
                # Een bot speelt alleen als hij zowel de inzet als het onderhoud kan betalen.
                bet = self.bot.choose_bet(state.balance - upkeep)
                if bet is None:
                    break
                self.roulette.play(state, bet, modifiers, source="bot")
                state.balance -= upkeep
                state.total_upkeep += upkeep

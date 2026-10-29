from services.bot_service import BotService
from services.game_service import GameService
from services.roulette_service import RouletteService
from services.save_service import SaveService
from services.upgrade_service import UpgradeService


def build_game_service() -> GameService:
    roulette = RouletteService()
    return GameService(
        save_service=SaveService(),
        roulette=roulette,
        bots=BotService(roulette),
        upgrades=UpgradeService(),
    )

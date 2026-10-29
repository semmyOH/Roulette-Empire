import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT))

# Tests gebruiken een eigen database, nooit de echte savegame.
_tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)  # Windows houdt SQLite-bestanden open.
os.environ["ROULETTE_DATABASE"] = str(Path(_tmp.name) / "test.db")

from app import create_app  # noqa: E402
from config import Config  # noqa: E402
from database.db import db  # noqa: E402


class FakeClock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now

    def advance(self, seconds: float):
        self.now += seconds


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.app = self.make_app()
        with self.app.app_context():
            db.drop_all()
            db.create_all()

    def make_app(self):
        app = create_app(Config)
        self.clock = FakeClock()
        app.extensions["game_service"].clock = self.clock
        self.client = app.test_client()
        return app

    def state(self):
        return self.client.get("/api/state").get_json()

    def set_balance(self, amount: float):
        self.state()  # Zorgt dat de savegame geladen is.
        self.app.extensions["game_service"]._state.balance = amount

    def buy_bots(self, count: int):
        for _ in range(count):
            self.assertEqual(self.client.post("/api/upgrades/junior_bot/buy").status_code, 200)

    def test_new_game_starts_with_100(self):
        state = self.state()
        self.assertEqual(state["balance"], 100)
        self.assertEqual(state["upkeep_per_round"], 0)
        self.assertEqual([u["id"] for u in state["upgrades"]],
                         ["lucky_wheel", "better_tables", "efficient_staff", "junior_bot"])

    def test_spin_changes_balance(self):
        response = self.client.post("/api/spin", json={"bet_type": "red", "amount": 10})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn(data["result"]["net"], (10, -10))
        self.assertEqual(data["state"]["balance"], 100 + data["result"]["net"])
        self.assertEqual(data["state"]["history"][0]["source"], "player")

    def test_invalid_spin_returns_dutch_error(self):
        response = self.client.post("/api/spin", json={"bet_type": "red", "amount": 500})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "Onvoldoende saldo voor deze inzet.")

    def test_no_upkeep_without_bots(self):
        self.state()
        self.clock.advance(4)
        self.assertEqual(self.state()["balance"], 100)

    def test_upkeep_is_one_euro_per_bot_spin(self):
        self.set_balance(2000)
        self.buy_bots(2)  # €300 + €450
        state = self.state()
        self.assertEqual((state["upkeep_per_spin"], state["upkeep_per_round"]), (1, 2))

        self.clock.advance(3)  # Nog geen botspin (die komt na 5 s).
        self.assertEqual(self.state()["balance"], 1250)

        self.clock.advance(2)
        state = self.state()
        bot_spins = state["history"][:2]
        self.assertEqual([s["source"] for s in bot_spins], ["bot", "bot"])
        self.assertTrue(all(abs(s["net"]) == 5 for s in bot_spins), "bots zetten €5 in: +5 of -5")
        self.assertEqual(state["total_upkeep"], 2)
        self.assertAlmostEqual(state["balance"], 1250 - 2 + sum(s["net"] for s in bot_spins), places=2)

    def test_efficient_staff_lowers_upkeep(self):
        self.set_balance(2000)
        self.buy_bots(1)
        self.client.post("/api/upgrades/efficient_staff/buy")
        self.assertEqual(self.state()["upkeep_per_spin"], 0.9)

    def test_long_pause_is_capped(self):
        self.set_balance(1000)
        self.buy_bots(1)
        self.clock.advance(3600)
        self.assertEqual(self.state()["total_upkeep"], 1, "maximaal 5 s telt mee: één botspin")

    def test_buy_upgrade(self):
        response = self.client.post("/api/upgrades/lucky_wheel/buy")
        self.assertEqual(response.status_code, 200)
        lucky = response.get_json()["state"]["upgrades"][0]
        self.assertEqual((lucky["level"], lucky["price"]), (1, 150))

        self.assertEqual(self.client.post("/api/upgrades/better_tables/buy").status_code, 400)
        self.assertEqual(self.client.post("/api/upgrades/unknown/buy").status_code, 404)

    def test_bankrupt_blocks_spins_until_reset(self):
        self.client.post("/api/upgrades/lucky_wheel/buy")  # Saldo €0: geen enkele inzet meer mogelijk.
        self.assertTrue(self.state()["bankrupt"])
        self.assertEqual(self.client.post("/api/spin", json={"bet_type": "red", "amount": 1}).status_code, 400)

        reset = self.client.post("/api/reset").get_json()["state"]
        self.assertEqual(reset["balance"], 100)
        self.assertFalse(reset["bankrupt"])
        self.assertEqual(reset["upgrades"][0]["level"], 0)

    def test_bot_only_spins_if_it_can_pay_bet_and_upkeep(self):
        self.set_balance(305)
        self.buy_bots(1)  # Saldo €5: genoeg voor de inzet, niet voor inzet + onderhoud.
        self.clock.advance(5)
        state = self.state()
        self.assertEqual((state["balance"], state["history"]), (5, []))

        self.set_balance(6)
        self.clock.advance(5)
        state = self.state()
        self.assertEqual(state["history"][0]["source"], "bot")
        self.assertGreaterEqual(state["balance"], 0)

    def test_save_and_load(self):
        self.client.post("/api/spin", json={"bet_type": "black", "amount": 5})
        saved = self.state()
        self.assertEqual(self.client.post("/api/save").status_code, 200)

        self.make_app()  # Nieuwe server, zelfde database.
        loaded = self.state()
        self.assertEqual(loaded["balance"], saved["balance"])
        self.assertEqual(loaded["history"], saved["history"])

    def test_bots_play_every_five_seconds(self):
        self.set_balance(1000)
        self.buy_bots(1)
        self.clock.advance(5)
        state = self.state()
        self.assertEqual(state["bots"]["active"], 1)
        self.assertEqual(state["history"][0]["source"], "bot")


if __name__ == "__main__":
    unittest.main()

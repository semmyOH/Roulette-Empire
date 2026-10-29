import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from game.errors import InvalidBetError  # noqa: E402
from game.roulette import Bet, BetType, RouletteWheel  # noqa: E402
from game.upgrades import UPGRADE_CATALOG, compute_modifiers  # noqa: E402


class BetTests(unittest.TestCase):
    def test_from_dict_accepts_valid_bets(self):
        self.assertEqual(Bet.from_dict({"bet_type": "red", "amount": 10}), Bet(BetType.RED, 10))
        self.assertEqual(Bet.from_dict({"bet_type": "number", "number": 17, "amount": 5}).number, 17)

    def test_from_dict_rejects_invalid_bets(self):
        for payload in [
            {"bet_type": "blue", "amount": 10},
            {"bet_type": "red", "amount": 0},
            {"bet_type": "red", "amount": 2.5},
            {"bet_type": "red", "amount": True},
            {"bet_type": "number", "number": 37, "amount": 10},
            {"bet_type": "number", "amount": 10},
        ]:
            with self.subTest(payload=payload), self.assertRaises(InvalidBetError):
                Bet.from_dict(payload)

    def test_zero_loses_on_outside_bets(self):
        for bet_type in [BetType.RED, BetType.BLACK, BetType.EVEN, BetType.ODD]:
            self.assertFalse(Bet(bet_type, 1).wins(0))

    def test_outside_bets_cover_18_numbers(self):
        for bet_type in [BetType.RED, BetType.BLACK, BetType.EVEN, BetType.ODD]:
            self.assertEqual(len(Bet(bet_type, 1).winning_numbers()), 18)


class WheelTests(unittest.TestCase):
    def win_rate(self, multiplier: float, spins: int = 40000) -> float:
        wheel = RouletteWheel(random.Random(42))
        bet = Bet(BetType.RED, 1)
        return sum(bet.wins(wheel.spin(bet, multiplier)) for _ in range(spins)) / spins

    def test_base_win_chance_is_18_of_37(self):
        self.assertAlmostEqual(self.win_rate(1.0), 18 / 37, delta=0.01)

    def test_lucky_wheel_raises_win_chance(self):
        self.assertAlmostEqual(self.win_rate(1.10), 18 / 37 * 1.10, delta=0.01)

    def test_win_chance_is_capped(self):
        self.assertAlmostEqual(self.win_rate(5.0), 0.75, delta=0.01)


class UpgradeTests(unittest.TestCase):
    def test_price_grows_exponentially(self):
        lucky = UPGRADE_CATALOG["lucky_wheel"]
        self.assertEqual([lucky.price(level) for level in range(3)], [100, 150, 225])

    def test_modifiers_combine_upgrades(self):
        modifiers = compute_modifiers({"lucky_wheel": 2, "better_tables": 1, "efficient_staff": 2, "junior_bot": 3})
        self.assertAlmostEqual(modifiers.win_chance_multiplier, 1.10)
        self.assertAlmostEqual(modifiers.payout_multiplier, 1.10)
        self.assertAlmostEqual(modifiers.upkeep_multiplier, 0.81)
        self.assertEqual(modifiers.bot_count, 3)


if __name__ == "__main__":
    unittest.main()

import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from game.errors import InvalidBetError  # noqa: E402
from game.roulette import Bet, BetType, RouletteWheel, parse_bets, total_net  # noqa: E402
from game.upgrades import UPGRADE_CATALOG, compute_modifiers  # noqa: E402


class BetTests(unittest.TestCase):
    def test_from_dict_accepts_valid_bets(self):
        self.assertEqual(Bet.from_dict({"bet_type": "red", "amount": 10}), Bet(BetType.RED, 10))
        self.assertEqual(Bet.from_dict({"bet_type": "number", "value": 17, "amount": 5}).value, 17)
        self.assertEqual(Bet.from_dict({"bet_type": "dozen", "value": 2, "amount": 5}), Bet(BetType.DOZEN, 5, 2))

    def test_from_dict_rejects_invalid_bets(self):
        for payload in [
            {"bet_type": "blue", "amount": 10},
            {"bet_type": "red", "amount": 0},
            {"bet_type": "red", "amount": 2.5},
            {"bet_type": "red", "amount": True},
            {"bet_type": "number", "value": 37, "amount": 10},
            {"bet_type": "number", "amount": 10},
            {"bet_type": "dozen", "value": 4, "amount": 10},
            {"bet_type": "column", "value": 0, "amount": 10},
            {"bet_type": "street", "value": 13, "amount": 10},
        ]:
            with self.subTest(payload=payload), self.assertRaises(InvalidBetError):
                Bet.from_dict(payload)

    def test_zero_loses_on_outside_bets(self):
        for bet_type in [BetType.RED, BetType.BLACK, BetType.EVEN, BetType.ODD]:
            self.assertFalse(Bet(bet_type, 1).wins(0))

    def test_outside_bets_cover_18_numbers(self):
        for bet_type in [BetType.RED, BetType.BLACK, BetType.EVEN, BetType.ODD]:
            self.assertEqual(len(Bet(bet_type, 1).numbers()), 18)

    def test_dozens_columns_and_streets(self):
        self.assertEqual(Bet(BetType.DOZEN, 1, 2).numbers(), frozenset(range(13, 25)))
        self.assertEqual(Bet(BetType.COLUMN, 1, 1).numbers(), frozenset(range(1, 37, 3)))
        self.assertEqual(Bet(BetType.COLUMN, 1, 3).numbers(), frozenset(range(3, 37, 3)))
        self.assertEqual(Bet(BetType.STREET, 1, 12).numbers(), frozenset({34, 35, 36}))
        for bet_type in [BetType.DOZEN, BetType.COLUMN]:
            self.assertFalse(Bet(bet_type, 1, 1).wins(0))

    def test_payouts(self):
        self.assertEqual(Bet(BetType.DOZEN, 10, 1).net(5), 20)
        self.assertEqual(Bet(BetType.COLUMN, 10, 2).net(5), 20)
        self.assertEqual(Bet(BetType.STREET, 10, 2).net(5), 110)
        self.assertEqual(Bet(BetType.NUMBER, 10, 5).net(5), 350)
        self.assertEqual(Bet(BetType.STREET, 10, 2).net(7), -10)

    def test_multiple_bets_add_up(self):
        bets = parse_bets({"bets": [
            {"bet_type": "red", "amount": 10},
            {"bet_type": "dozen", "value": 1, "amount": 5},
            {"bet_type": "street", "value": 4, "amount": 2},
        ]})
        self.assertEqual(total_net(bets, 12), 10 + 10 + 22)  # rood, 1e 12, straat 10-11-12
        self.assertEqual(total_net(bets, 0), -17)

    def test_parse_bets_rejects_empty_list(self):
        with self.assertRaises(InvalidBetError):
            parse_bets({"bets": []})


class WheelTests(unittest.TestCase):
    def win_rate(self, multiplier: float, spins: int = 40000) -> float:
        wheel = RouletteWheel(random.Random(42))
        bet = Bet(BetType.RED, 1)
        return sum(bet.wins(wheel.spin([bet], multiplier)) for _ in range(spins)) / spins

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

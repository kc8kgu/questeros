"""Tests for town casino rules."""
import unittest
from unittest.mock import patch

import casino


class CasinoTests(unittest.TestCase):
    def test_flip_is_fair(self):
        with patch("casino.random.random", return_value=0.4):
            self.assertTrue(casino.flip())
        with patch("casino.random.random", return_value=0.6):
            self.assertFalse(casino.flip())

    def test_bet_amounts_are_positive(self):
        self.assertTrue(all(amount > 0 for amount in casino.BET_AMOUNTS))


if __name__ == "__main__":
    unittest.main()

"""Tests for versioned save-game serialization."""
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import savegame
from player import Player


class SaveGameTests(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.path = Path(self.directory.name) / "savegame.json"

    def tearDown(self):
        self.directory.cleanup()

    def test_round_trip_restores_player_and_town_state(self):
        player = Player(5, 6)
        player.max_hp = 80
        player.hp = 47
        player.gold = 345
        player.food = 62
        player.level = 4
        player.xp = 19
        player.steps = 123
        player._since_food = 8
        player._since_starve = 3
        player.weapon = 2
        player.armor = 1
        player.weapons_owned.update((1, 2))
        player.armors_owned.add(1)
        location = {
            "kind": "town",
            "x": 9,
            "y": 10,
            "town_x": 20,
            "town_y": 21,
            "return_x": 19,
            "return_y": 21,
        }

        savegame.save_game(self.path, 42, player, location)
        seed, restored, restored_location = savegame.load_game(self.path)

        self.assertEqual(seed, 42)
        self.assertEqual(restored_location, location)
        self.assertEqual((restored.x, restored.y), (9, 10))
        self.assertEqual(restored.hp, 47)
        self.assertEqual(restored.max_hp, 80)
        self.assertEqual(restored.gold, 345)
        self.assertEqual(restored.food, 62)
        self.assertEqual(restored.level, 4)
        self.assertEqual(restored.xp, 19)
        self.assertEqual(restored.steps, 123)
        self.assertEqual(restored._since_food, 8)
        self.assertEqual(restored._since_starve, 3)
        self.assertEqual(restored.weapon, 2)
        self.assertEqual(restored.armor, 1)
        self.assertEqual(restored.weapons_owned, {0, 1, 2})
        self.assertEqual(restored.armors_owned, {0, 1})
        self.assertFalse(restored.invincible)

    def test_missing_corrupt_and_unsupported_saves_are_rejected(self):
        with self.assertRaisesRegex(savegame.SaveGameError, "No saved"):
            savegame.load_game(self.path)

        self.path.write_text("{", encoding="utf-8")
        with self.assertRaisesRegex(savegame.SaveGameError, "could not be read"):
            savegame.load_game(self.path)

        self.path.write_text(json.dumps({"version": 999}), encoding="utf-8")
        with self.assertRaisesRegex(savegame.SaveGameError, "unsupported"):
            savegame.load_game(self.path)

    def test_inconsistent_equipment_is_rejected(self):
        player = Player(0, 0)
        savegame.save_game(
            self.path, 42, player,
            {"kind": "world", "x": 1, "y": 1})
        data = json.loads(self.path.read_text(encoding="utf-8"))
        data["player"]["weapon"] = 1
        self.path.write_text(json.dumps(data), encoding="utf-8")

        with self.assertRaisesRegex(savegame.SaveGameError, "inconsistent"):
            savegame.load_game(self.path)


if __name__ == "__main__":
    unittest.main()

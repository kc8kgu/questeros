"""Tests for the shared tile-map contract."""
import unittest

from game_map import GameMap


class GameMapTests(unittest.TestCase):
    def setUp(self):
        self.game_map = GameMap([
            ["wall", "floor", "wall"],
            ["floor", "floor", "water"],
        ], blocked={"wall", "water"})

    def test_dimensions_tiles_and_count_are_derived_from_rows(self):
        self.assertEqual(self.game_map.width, 3)
        self.assertEqual(self.game_map.height, 2)
        self.assertEqual(self.game_map.tile_at(1, 0), "floor")
        self.assertEqual(list(self.game_map.tiles()).count("floor"), 3)
        self.assertEqual(self.game_map.count("wall"), 2)

    def test_walkability_includes_bounds_and_blocked_tiles(self):
        self.assertTrue(self.game_map.is_walkable(1, 0))
        self.assertFalse(self.game_map.is_walkable(0, 0))
        self.assertFalse(self.game_map.is_walkable(3, 0))

    def test_out_of_bounds_tile_access_is_rejected(self):
        with self.assertRaises(IndexError):
            self.game_map.tile_at(-1, 0)
        with self.assertRaises(IndexError):
            self.game_map.tile_at(3, 0)

    def test_neighbors_only_include_cardinal_in_bounds_tiles(self):
        self.assertEqual(self.game_map.neighbors(1, 0), {
            "down": "floor",
            "left": "wall",
            "right": "wall",
        })

    def test_rows_must_be_nonempty_and_rectangular(self):
        with self.assertRaises(ValueError):
            GameMap([])
        with self.assertRaises(ValueError):
            GameMap([[]])
        with self.assertRaises(ValueError):
            GameMap([["floor"], ["floor", "floor"]])

    def test_map_copies_input_rows(self):
        rows = [["floor"]]
        game_map = GameMap(rows)
        rows[0][0] = "wall"
        self.assertEqual(game_map.tile_at(0, 0), "floor")

if __name__ == "__main__":
    unittest.main()

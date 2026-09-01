"""Tests for native-resolution map rendering."""
import unittest
from types import SimpleNamespace

import pygame

import palette as p
import settings as s
from camera import Camera
from game_map import GameMap
from graphics.actors import PLAYER
from graphics.terrain import mountain_key, tree_key
from map_view import MapView


class MapViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_fractional_camera_aligns_tiles_and_actor_without_edge_gaps(self):
        grass = pygame.Surface((s.TILE, s.TILE))
        grass.fill(p.GREEN)
        marker = pygame.Surface((s.TILE, s.TILE))
        marker.fill(p.CRIMSON)
        edge = pygame.Surface((s.TILE, s.TILE))
        edge.fill(p.GOLD)
        player_art = pygame.Surface((s.TILE, s.TILE), pygame.SRCALPHA)
        player_art.fill(p.LTBLUE, (0, 0, 1, 1))
        cache = {
            "grass": grass,
            "grass:v1": grass,
            "grass:v2": grass,
            "grass:v3": grass,
            "marker": marker,
            "edge": edge,
            PLAYER: player_art,
            "player:up": player_art,
            "player:down": player_art,
            "player:left": player_art,
            "player:right": player_art,
        }
        grid = [["grass"] * 5 for _ in range(5)]
        grid[2][2] = "marker"
        grid[3][3] = "edge"
        game_map = GameMap(grid)
        view = MapView(view_width=3, view_height=3)
        screen = pygame.Surface((
            s.TILE * 3 * s.RENDER_SCALE,
            s.TILE * 3 * s.RENDER_SCALE,
        ))
        player = SimpleNamespace(fx=2.0, fy=2.0)

        view.draw(screen, game_map, player, cache, Camera(3, 3))

        self.assertEqual(screen.get_at((96, 96))[:3], p.LTBLUE)
        self.assertEqual(screen.get_at((99, 96))[:3], p.CRIMSON)
        self.assertEqual(screen.get_at((191, 191))[:3], p.GOLD)

    def test_world_scenery_uses_only_single_cell_tiles(self):
        tree = pygame.Surface((s.TILE, s.TILE))
        tree.fill(p.GREEN)
        mountain = pygame.Surface((s.TILE, s.TILE))
        mountain.fill(p.GREY)
        town = pygame.Surface((s.TILE, s.TILE))
        town.fill(p.GOLD)
        player_art = pygame.Surface((s.TILE, s.TILE), pygame.SRCALPHA)
        cache = {
            tree_key(0): tree,
            mountain_key(0): mountain,
            "town": town,
            "player:down": player_art,
        }
        screen = pygame.Surface((s.TILE * 3, s.TILE))
        view = MapView(view_width=3, view_height=1)

        view.draw(
            screen, GameMap([["tree", "mountain", "town"]]),
            SimpleNamespace(fx=2.0, fy=0.0, facing="down"), cache,
            Camera(3, 1),
        )

        self.assertEqual(screen.get_at((32, 32))[:3], p.GREEN)
        self.assertEqual(screen.get_at((96, 32))[:3], p.GREY)
        self.assertEqual(screen.get_at((160, 32))[:3], p.GOLD)
        self.assertEqual(view._scaled_art, {})


if __name__ == "__main__":
    unittest.main()

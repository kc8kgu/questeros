"""Tests for native-resolution map rendering."""
import unittest
from types import SimpleNamespace

import pygame

import palette as p
import settings as s
from camera import Camera
from game_map import GameMap
from graphics.actors import PLAYER
from map_view import (
    DOWN, LEFT, RIGHT, UP, MapView, _is_cluster_anchor, _shoreline_flip,
)


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

    def test_cluster_props_are_thinned_without_leaving_blocked_cells_bare(self):
        game_map = GameMap([["tree"] * 5 for _ in range(5)], {"tree"})
        anchors = {
            (x, y)
            for y in range(game_map.height)
            for x in range(game_map.width)
            if _is_cluster_anchor(game_map, x, y, "tree")
        }

        self.assertLess(len(anchors), game_map.width * game_map.height)
        for y in range(game_map.height):
            for x in range(game_map.width):
                self.assertTrue(any(
                    (x + dx, y + dy) in anchors
                    for dy in (-1, 0, 1)
                    for dx in (-1, 0, 1)
                ))

    def test_straight_shoreline_variants_only_flip_along_the_coast(self):
        self.assertEqual(
            _shoreline_flip(UP | RIGHT | DOWN, 1, 0), (False, True))
        self.assertEqual(
            _shoreline_flip(RIGHT | DOWN | LEFT, 1, 0), (True, False))
        self.assertEqual(_shoreline_flip(RIGHT, 1, 0), (False, False))


if __name__ == "__main__":
    unittest.main()

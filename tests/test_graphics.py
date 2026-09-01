"""Tests for the committed asset sheets and visual cache."""
import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import combat
import graphics
import hud
import settings as s
from battle_view import BATTLE_RENDER_SIZE
from graphics import assets
from graphics.actors import GUARD, PLAYER, VENDOR
from graphics.battle_actors import (
    BATTLE_ART_SIZE, BATTLE_MONSTER_LOOKS, BATTLE_PLAYER_KEY,
    battle_monster_key,
)
from graphics.battle_backdrops import (
    BATTLE_BACKDROP_SIZE, BATTLE_BACKDROP_TERRAINS, battle_backdrop_key,
)
from graphics.monsters import MONSTER_LOOKS
from graphics.terrain import (
    GRASS_VARIANTS, SAND_VARIANTS, WATER_VARIANTS, mountain_key, tree_key,
    twall_key, water_key,
)
from graphics.ui import (
    CURSOR, ICON_KEYS, PANEL, PANEL_ALT, UI_BAR_FILL, UI_BAR_FRAME,
    UI_DIVIDER,
)
from tools.vga_art import audit_surface


class GraphicsCacheTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_cache_is_deterministic(self):
        first = graphics.build_cache()
        second = graphics.build_cache()
        self.assertEqual(first.keys(), second.keys())
        for key in first:
            self.assertEqual(
                pygame.image.tobytes(first[key], "RGBA"),
                pygame.image.tobytes(second[key], "RGBA"),
            )

    def test_required_sheet_dimensions_and_alpha(self):
        for name, (relative, grid, cell_size, alpha) in assets.SHEET_SPECS.items():
            path = assets.ASSET_ROOT / relative
            sheet = pygame.image.load(str(path))
            self.assertEqual(
                sheet.get_size(),
                (grid[0] * cell_size[0], grid[1] * cell_size[1]),
            )
            self.assertEqual(bool(sheet.get_flags() & pygame.SRCALPHA), alpha)

    def test_vga_pilot_sheets_obey_art_contract(self):
        pilot_names = (
            "overworld_simple_vga",
            "exploration_vga",
        )
        for name in pilot_names:
            relative, grid, cell_size, alpha = assets.SHEET_SPECS[name]
            sheet = pygame.image.load(str(assets.ASSET_ROOT / relative))
            with self.subTest(name=name):
                self.assertEqual(
                    sheet.get_size(),
                    (grid[0] * cell_size[0], grid[1] * cell_size[1]),
                )
                self.assertEqual(audit_surface(sheet, 1, alpha), [])

    def test_cache_has_expected_surface_sizes(self):
        cache = graphics.build_cache()
        self.assertTrue(cache)
        ui_keys = {
            PANEL, PANEL_ALT, CURSOR, *ICON_KEYS, UI_BAR_FILL, UI_BAR_FRAME,
            UI_DIVIDER, "ui_selection", "ui_status", "ui_ornament",
            *(assets.PANEL_SLICES), *(assets.PANEL_ALT_SLICES),
        }
        backdrop_keys = {
            battle_backdrop_key(terrain)
            for terrain in BATTLE_BACKDROP_TERRAINS
        }
        screen_keys = {
            "screen_title", "screen_win", "screen_death", "town_background",
        }
        effect_keys = {f"battle_slash_{index}" for index in range(6)}
        world_prop_keys = set(assets.OVERWORLD_PROP_MAP)
        town_prop_keys = set(assets.TOWN_PROP_MAP)
        battle_keys = {
            BATTLE_PLAYER_KEY,
            *(battle_monster_key(monster_id)
              for monster_id in BATTLE_MONSTER_LOOKS),
        }
        for key, cached_surface in cache.items():
            if key in ui_keys:
                expected = (s.UI_TILE, s.UI_TILE)
            elif key in backdrop_keys:
                expected = BATTLE_BACKDROP_SIZE
            elif key in screen_keys:
                expected = (320, 208)
            elif key in effect_keys:
                expected = (160, 80)
            elif key in battle_keys:
                expected = (BATTLE_ART_SIZE, BATTLE_ART_SIZE)
            elif key in world_prop_keys:
                expected = (256, 256)
            elif key in town_prop_keys:
                expected = (256, 192)
            else:
                expected = (s.TILE, s.TILE)
            with self.subTest(key=key):
                self.assertEqual(cached_surface.get_size(), expected)

    def test_terrain_cache_has_locked_variant_counts_and_masks(self):
        cache = graphics.build_cache()
        self.assertEqual(
            {key for key in cache if key == "grass" or key.startswith("grass:v")},
            {"grass", "grass:v1", "grass:v2", "grass:v3"},
        )
        self.assertEqual(
            {key for key in cache if key == "sand" or key.startswith("sand:v")},
            {"sand", "sand:v1", "sand:v2", "sand:v3"},
        )
        self.assertEqual(
            {key for key in cache if key.startswith("water:m")},
            {water_key(mask) for mask in range(16)},
        )
        self.assertEqual(
            {key for key in cache if key.startswith("tree:m")},
            {tree_key(mask) for mask in range(16)},
        )
        self.assertEqual(
            {key for key in cache if key.startswith("mountain:m")},
            {mountain_key(mask) for mask in range(16)},
        )
        self.assertEqual(
            {key for key in cache if key.startswith("twall:m")},
            {twall_key(mask) for mask in range(16)},
        )
        self.assertEqual((GRASS_VARIANTS, SAND_VARIANTS, WATER_VARIANTS), (4, 4, 1))

    def test_actor_and_ui_alpha_are_preserved(self):
        cache = graphics.build_cache()
        for key in (PLAYER, VENDOR, GUARD, "player:up", BATTLE_PLAYER_KEY):
            with self.subTest(key=key):
                self.assertTrue(cache[key].get_flags() & pygame.SRCALPHA)
                self.assertLess(
                    max(cache[key].get_at((0, 0)).a,
                        cache[key].get_at((63, 63)).a),
                    256,
                )
        for key in ICON_KEYS:
            with self.subTest(key=key):
                self.assertTrue(cache[key].get_flags() & pygame.SRCALPHA)
        for key in (*assets.OVERWORLD_PROP_MAP, *assets.TOWN_PROP_MAP):
            with self.subTest(key=key):
                self.assertTrue(cache[key].get_flags() & pygame.SRCALPHA)
                self.assertEqual(cache[key].get_at((0, 0)).a, 0)

    def test_overworld_props_have_no_pale_pixels_on_alpha_edges(self):
        cache = graphics.build_cache()
        neighbors = (
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (1, -1), (-1, 1), (1, 1),
        )
        for key in assets.OVERWORLD_PROP_MAP:
            surface = cache[key]
            width, height = surface.get_size()
            pale_edge_pixels = []
            for y in range(height):
                for x in range(width):
                    color = surface.get_at((x, y))
                    rgb = color[:3]
                    if color.a == 0 or min(rgb) < 190 \
                            or max(rgb) - min(rgb) > 24:
                        continue
                    if any(
                            0 <= x + dx < width
                            and 0 <= y + dy < height
                            and surface.get_at((x + dx, y + dy)).a == 0
                            for dx, dy in neighbors):
                        pale_edge_pixels.append((x, y))
            with self.subTest(key=key):
                self.assertEqual(pale_edge_pixels, [])

    def test_monster_rules_and_asset_registries_match(self):
        monster_ids = {monster["id"] for monster in combat.MONSTERS}
        self.assertEqual(monster_ids, set(MONSTER_LOOKS))
        self.assertEqual(monster_ids, set(BATTLE_MONSTER_LOOKS))
        for monster_id, look in BATTLE_MONSTER_LOOKS.items():
            with self.subTest(monster_id=monster_id):
                self.assertEqual(set(look), {"asset"})
                self.assertIn(look["asset"], assets.BATTLE_MAP)

    def test_battle_art_is_complete_distinct_and_transparent(self):
        cache = graphics.build_cache()
        keys = [
            BATTLE_PLAYER_KEY,
            *(battle_monster_key(monster_id)
              for monster_id in BATTLE_MONSTER_LOOKS),
        ]
        self.assertEqual(
            len({pygame.image.tobytes(cache[key], "RGBA") for key in keys}),
            len(keys),
        )
        for key in keys:
            self.assertTrue(cache[key].get_flags() & pygame.SRCALPHA)
            alpha = [
                cache[key].get_at((x, y)).a
                for x, y in ((0, 0), (63, 0), (0, 63), (63, 63))
            ]
            self.assertIn(0, alpha)

    def test_battle_backdrops_and_scene_screens_are_opaque(self):
        cache = graphics.build_cache()
        backdrop_keys = [
            battle_backdrop_key(terrain)
            for terrain in BATTLE_BACKDROP_TERRAINS
        ]
        self.assertEqual(
            len({pygame.image.tobytes(cache[key], "RGB") for key in backdrop_keys}),
            len(backdrop_keys),
        )
        for key in backdrop_keys + [
                "screen_title", "screen_win", "screen_death",
                "town_background"]:
            self.assertFalse(cache[key].get_flags() & pygame.SRCALPHA)

    def test_battle_sizes_remain_unchanged(self):
        self.assertEqual(BATTLE_RENDER_SIZE, (960, 624))
        self.assertEqual(BATTLE_BACKDROP_SIZE, (320, 144))
        self.assertEqual(BATTLE_ART_SIZE, 64)
        self.assertEqual(s.TILE, 64)

    def test_battle_effect_frames_are_complete_and_distinct(self):
        cache = graphics.build_cache()
        keys = [f"battle_slash_{index}" for index in range(6)]
        self.assertEqual(
            len({pygame.image.tobytes(cache[key], "RGBA") for key in keys}),
            len(keys),
        )
        for key in keys:
            self.assertTrue(cache[key].get_flags() & pygame.SRCALPHA)

    def test_font_files_are_loadable(self):
        for bold in (False, True):
            self.assertTrue(assets.font_path(bold).is_file())
            self.assertIsNotNone(hud.get_font(12, bold=bold))

    def test_battle_monster_key_rejects_unknown_ids(self):
        with self.assertRaises(ValueError):
            battle_monster_key("mimic")


if __name__ == "__main__":
    unittest.main()

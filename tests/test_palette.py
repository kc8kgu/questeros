"""Tests for the centralized retro pixel-art palette."""
import unittest

import palette


class PaletteTests(unittest.TestCase):
    def test_master_palette_contains_unique_rgb_colors(self):
        self.assertEqual(
            len(palette.MASTER_PALETTE), len(set(palette.MASTER_PALETTE)))
        for color in palette.MASTER_PALETTE:
            self.assertEqual(len(color), 3)
            self.assertTrue(all(
                isinstance(channel, int) and 0 <= channel <= 255
                for channel in color))

    def test_material_ramps_only_use_master_palette_colors(self):
        expected = {
            "foliage", "earth", "stone", "water", "skin",
            "metal", "fire", "magic", "interface",
        }
        self.assertEqual(set(palette.RAMPS), expected)
        master = set(palette.MASTER_PALETTE)
        for ramp in palette.RAMPS.values():
            self.assertGreaterEqual(len(ramp), 6)
            self.assertTrue(set(ramp) <= master)

    def test_legacy_settings_colors_reference_palette(self):
        import settings as s

        for name in (
            "BLACK", "WHITE", "RED", "CYAN", "PURPLE", "GREEN",
            "BLUE", "YELLOW", "ORANGE", "BROWN", "LTRED", "DKGREY",
            "GREY", "LTGREEN", "LTBLUE", "LTGREY",
        ):
            self.assertIs(getattr(s, name), getattr(palette, name))

    def test_named_interface_overlays_are_rgba_colors(self):
        self.assertEqual(palette.OVERLAY_DIM, (*palette.BLACK, 160))
        self.assertEqual(palette.OVERLAY_DEATH, (*palette.BLACK, 200))


if __name__ == "__main__":
    unittest.main()

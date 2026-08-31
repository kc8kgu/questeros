"""Tests for the centralized retro pixel-art palette."""
import unittest

import palette


class PaletteTests(unittest.TestCase):
    def test_master_palette_has_all_256_vga_slots(self):
        self.assertEqual(len(palette.VGA_PALETTE_6BIT), 256)
        self.assertEqual(len(palette.MASTER_PALETTE), 256)
        for color in palette.VGA_PALETTE_6BIT:
            self.assertEqual(len(color), 3)
            self.assertTrue(all(
                isinstance(channel, int) and 0 <= channel <= 63
                for channel in color))
        for color in palette.MASTER_PALETTE:
            self.assertEqual(len(color), 3)
            self.assertTrue(all(
                isinstance(channel, int) and 0 <= channel <= 255
                for channel in color))

    def test_palette_matches_mode_13h_layout_and_conversion(self):
        self.assertEqual(palette.MASTER_PALETTE[:16], (
            (0, 0, 0), (0, 0, 170), (0, 170, 0), (0, 170, 170),
            (170, 0, 0), (170, 0, 170), (170, 85, 0),
            (170, 170, 170), (85, 85, 85), (85, 85, 255),
            (85, 255, 85), (85, 255, 255), (255, 85, 85),
            (255, 85, 255), (255, 255, 85), (255, 255, 255),
        ))
        self.assertEqual(
            palette.MASTER_PALETTE[16:32],
            tuple((value, value, value) for value in (
                0, 20, 32, 44, 56, 69, 81, 97,
                113, 130, 146, 162, 182, 203, 227, 255,
            )),
        )
        self.assertEqual(palette.MASTER_PALETTE[32], (0, 0, 255))
        self.assertEqual(palette.MASTER_PALETTE[247], (44, 48, 65))
        self.assertEqual(palette.MASTER_PALETTE[248:], ((0, 0, 0),) * 8)

    def test_palette_helpers_validate_and_return_master_colors(self):
        self.assertEqual(palette.palette_color(15), (255, 255, 255))
        self.assertIn(palette.nearest_color(120, 90, 30),
                      palette.MASTER_COLOR_SET)
        self.assertTrue(palette.is_master_color((*palette.BLUE, 255)))
        with self.assertRaises(ValueError):
            palette.palette_color(256)
        with self.assertRaises(ValueError):
            palette.nearest_color(-1, 0, 0)

    def test_material_ramps_only_use_master_palette_colors(self):
        expected = {
            "foliage", "earth", "stone", "water", "skin",
            "metal", "fire", "magic", "interface",
        }
        self.assertEqual(set(palette.RAMPS), expected)
        master = set(palette.MASTER_PALETTE)
        for ramp in palette.RAMPS.values():
            self.assertGreaterEqual(len(ramp), 6)
            self.assertEqual(len(ramp), len(set(ramp)))
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

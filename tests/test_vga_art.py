"""Tests for the offline VGA artwork workflow."""
import unittest

import pygame

import palette
from tools import vga_art


class VgaArtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_quantize_enlarges_into_uniform_vga_blocks(self):
        source = pygame.Surface((4, 4), pygame.SRCALPHA)
        source.fill((71, 129, 74, 255))
        converted = vga_art.quantize(source, (2, 2), scale=2)

        self.assertEqual(converted.get_size(), (4, 4))
        self.assertEqual(vga_art.audit_surface(converted), [])
        self.assertTrue(all(
            palette.is_master_color(converted.get_at((x, y)))
            for y in range(4) for x in range(4)))

    def test_transparency_is_binary_after_conversion(self):
        source = pygame.Surface((2, 1), pygame.SRCALPHA)
        source.set_at((0, 0), (255, 255, 255, 20))
        source.set_at((1, 0), (20, 40, 60, 220))
        converted = vga_art.quantize(source, (2, 1), scale=2)

        self.assertEqual(converted.get_at((0, 0)).a, 0)
        self.assertEqual(converted.get_at((3, 0)).a, 255)

    def test_seamless_conversion_matches_opposite_edges(self):
        source = pygame.Surface((6, 6), pygame.SRCALPHA)
        for y in range(6):
            for x in range(6):
                source.set_at((x, y), (x * 30, y * 30, 60, 255))
        converted = vga_art.quantize(
            source, (8, 8), scale=2, seamless=True)

        for y in range(converted.get_height()):
            self.assertEqual(
                converted.get_at((0, y)),
                converted.get_at((converted.get_width() - 1, y)))
        for x in range(converted.get_width()):
            self.assertEqual(
                converted.get_at((x, 0)),
                converted.get_at((x, converted.get_height() - 1)))

    def test_pack_uses_row_major_cells(self):
        red = pygame.Surface((2, 2), pygame.SRCALPHA)
        blue = pygame.Surface((2, 2), pygame.SRCALPHA)
        red.fill((*palette.RED, 255))
        blue.fill((*palette.BLUE, 255))
        packed = vga_art.pack_surfaces(
            [red, blue], (2, 1), (2, 2), alpha=True)

        self.assertEqual(packed.get_at((0, 0))[:3], palette.RED)
        self.assertEqual(packed.get_at((3, 0))[:3], palette.BLUE)

    def test_connected_light_background_becomes_transparent(self):
        source = pygame.Surface((5, 5))
        source.fill((245, 245, 245))
        source.fill((40, 70, 50), (1, 1, 3, 3))
        source.set_at((2, 2), (250, 250, 250))
        result = vga_art.remove_connected_background(source)

        self.assertEqual(result.get_at((0, 0)).a, 0)
        self.assertEqual(result.get_at((1, 1)).a, 255)
        self.assertEqual(result.get_at((2, 2)).a, 255)

    def test_connected_dark_background_becomes_transparent(self):
        source = pygame.Surface((5, 5))
        source.fill((1, 1, 1))
        source.fill((40, 70, 50), (1, 1, 3, 3))
        source.set_at((2, 2), (0, 0, 0))
        result = vga_art.remove_connected_background(source)

        self.assertEqual(result.get_at((0, 0)).a, 0)
        self.assertEqual(result.get_at((1, 1)).a, 255)
        self.assertEqual(result.get_at((2, 2)), (0, 0, 0, 255))

    def test_fit_alpha_centers_cutout_on_square_canvas(self):
        source = pygame.Surface((12, 8), pygame.SRCALPHA)
        source.fill((0, 0, 0, 0))
        source.fill((*palette.GREEN, 255), (4, 1, 2, 6))
        result = vga_art.fit_alpha(source, padding_ratio=0.0)

        self.assertEqual(result.get_size(), (8, 8))
        self.assertEqual(result.get_bounding_rect(min_alpha=1),
                         pygame.Rect(3, 1, 2, 6))

    def test_shoreline_atlas_has_sixteen_scaled_binary_frames(self):
        atlas = vga_art.build_shoreline_atlas()

        self.assertEqual(atlas.get_size(), (256, 256))
        self.assertEqual(vga_art.audit_surface(atlas), [])
        interior = atlas.subsurface((192, 192, 64, 64))
        self.assertEqual(interior.get_bounding_rect(min_alpha=1).size, (0, 0))
        isolated = atlas.subsurface((0, 0, 64, 64))
        self.assertGreater(isolated.get_bounding_rect(min_alpha=1).width, 0)

    def test_pale_cutout_edge_cleanup_preserves_scaled_blocks(self):
        source = pygame.Surface((6, 4), pygame.SRCALPHA)
        source.fill((0, 0, 0, 0))
        source.fill((227, 227, 227, 255), (2, 0, 2, 2))
        source.fill((*palette.ROCK, 255), (2, 2, 2, 2))
        result = vga_art.strip_pale_alpha_edges(source)

        self.assertEqual(result.get_at((2, 0)).a, 0)
        self.assertEqual(result.get_at((2, 2))[:3], palette.ROCK)
        self.assertEqual(vga_art.audit_surface(result), [])

    def test_outline_cleans_pale_edges_and_surrounds_silhouette(self):
        source = pygame.Surface((7, 7), pygame.SRCALPHA)
        source.fill((0, 0, 0, 0))
        source.set_at((3, 3), (*palette.GREEN, 255))
        source.set_at((4, 3), (182, 182, 182, 255))

        result = vga_art.outline_alpha(source)

        self.assertEqual(result.get_at((3, 3))[:3], palette.GREEN)
        self.assertEqual(result.get_at((4, 3))[:3], palette.BLACK)
        self.assertEqual(result.get_at((2, 2)), (*palette.BLACK, 255))
        self.assertEqual(result.get_at((5, 3)), (*palette.BLACK, 255))
        self.assertEqual(result.get_at((0, 0)).a, 0)


if __name__ == "__main__":
    unittest.main()

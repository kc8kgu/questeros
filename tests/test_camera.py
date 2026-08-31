"""Tests for pygame-free camera positioning and projection."""
import unittest

from camera import Camera


class CameraTests(unittest.TestCase):
    def setUp(self):
        self.camera = Camera(20, 13)

    def test_follow_centers_on_target_away_from_edges(self):
        self.camera.follow(48, 48, 96, 96)

        self.assertEqual(self.camera.x, 38)
        self.assertEqual(self.camera.y, 41.5)
        self.assertEqual(self.camera.tile_origin(), (38, 41))

    def test_follow_clamps_to_top_left_edge(self):
        self.camera.follow(2, 2, 96, 96)
        self.assertEqual((self.camera.x, self.camera.y), (0, 0))

    def test_follow_clamps_to_bottom_right_edge(self):
        self.camera.follow(95, 95, 96, 96)
        self.assertEqual((self.camera.x, self.camera.y), (76, 83))

    def test_map_no_larger_than_viewport_keeps_camera_at_origin(self):
        self.camera.follow(5, 5, 20, 13)
        self.assertEqual((self.camera.x, self.camera.y), (0, 0))

    def test_world_coordinates_project_relative_to_camera(self):
        self.camera.follow(48, 48, 96, 96)
        pixel_x, pixel_y = self.camera.world_to_pixel(48, 48, 16)

        self.assertEqual(pixel_x, 160)
        self.assertEqual(pixel_y, 104)


if __name__ == "__main__":
    unittest.main()

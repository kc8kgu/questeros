"""Pygame-free camera positioning for tile maps."""


class Camera:
    def __init__(self, view_width, view_height):
        self.view_width = view_width
        self.view_height = view_height
        self.x = 0.0
        self.y = 0.0

    def follow(self, target_x, target_y, map_width, map_height):
        max_x = max(0, map_width - self.view_width)
        max_y = max(0, map_height - self.view_height)
        self.x = min(max(target_x - self.view_width / 2, 0), max_x)
        self.y = min(max(target_y - self.view_height / 2, 0), max_y)

    def tile_origin(self):
        return int(self.x), int(self.y)

    def world_to_pixel(self, world_x, world_y, tile_size):
        return (round((world_x - self.x) * tile_size),
                round((world_y - self.y) * tile_size))

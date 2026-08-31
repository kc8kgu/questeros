"""Overworld generation and map state."""
import random

import settings as s
from game_map import GameMap

# Simple value-noise-ish scatter using a seeded RNG; good enough for a demo.
# Later this can be replaced by a hand-designed map file.


def generate(seed=42):
    """Return a deterministic overworld and its town coordinates."""
    rng = random.Random(seed)
    grid = [["grass"] * s.MAP_W for _ in range(s.MAP_H)]

    # Ocean border: water ring around the continent.
    for y in range(s.MAP_H):
        for x in range(s.MAP_W):
            edge = min(x, y, s.MAP_W - 1 - x, s.MAP_H - 1 - y)
            if edge < 3:
                grid[y][x] = "water"
            elif edge < 5 and rng.random() < 0.7:
                grid[y][x] = "sand"

    # Mountain ranges: random walks leaving ridges.
    for _ in range(4):
        x, y = rng.randrange(10, s.MAP_W - 10), rng.randrange(10, s.MAP_H - 10)
        for _ in range(35):
            if grid[y][x] == "grass":
                grid[y][x] = "mountain"
            x = max(5, min(s.MAP_W - 6, x + rng.randint(-1, 1)))
            y = max(5, min(s.MAP_H - 6, y + rng.randint(-1, 1)))

    # Forests: scattered clumps.
    for _ in range(24):
        x, y = rng.randrange(5, s.MAP_W - 5), rng.randrange(5, s.MAP_H - 5)
        for _ in range(12):
            if grid[y][x] == "grass":
                grid[y][x] = "tree"
            x = max(5, min(s.MAP_W - 6, x + rng.randint(-1, 1)))
            y = max(5, min(s.MAP_H - 6, y + rng.randint(-1, 1)))

    # A few lakes.
    for _ in range(4):
        cx, cy = rng.randrange(8, s.MAP_W - 8), rng.randrange(8, s.MAP_H - 8)
        r = rng.randint(2, 3)
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r and 5 < x < s.MAP_W - 6 and 5 < y < s.MAP_H - 6:
                    grid[y][x] = "water"

    # Towns on open grass.
    towns = []
    for _ in range(2):
        while True:
            x, y = rng.randrange(8, s.MAP_W - 8), rng.randrange(8, s.MAP_H - 8)
            if grid[y][x] == "grass":
                grid[y][x] = "town"
                towns.append((x, y))
                break

    # One distant volcano marks the dragon boss encounter.
    center_x, center_y = s.MAP_W // 2, s.MAP_H // 2
    while True:
        x, y = rng.randrange(8, s.MAP_W - 8), rng.randrange(8, s.MAP_H - 8)
        distance = abs(x - center_x) + abs(y - center_y)
        if grid[y][x] == "grass" and distance >= s.MAP_W // 3:
            grid[y][x] = "boss"
            break

    return GameMap(grid, s.BLOCKED), towns


def find_start(game_map):
    """A grass tile near the center of the map."""
    cx, cy = game_map.width // 2, game_map.height // 2
    for r in range(0, max(game_map.width, game_map.height)):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if game_map.in_bounds(x, y) and game_map.tile_at(x, y) == "grass":
                    return x, y
    return cx, cy

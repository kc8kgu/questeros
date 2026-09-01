"""Native-resolution tile-map and actor rendering."""
import math

import pygame

import settings as s
from graphics.actors import PLAYER
from graphics.terrain import (
    DOWN, GRASS_VARIANTS, LEFT, RIGHT, SAND_VARIANTS, UP, WATER_VARIANTS,
    grass_key, mountain_key, sand_key, tree_key, twall_key, water_key,
)

WATER_NEIGHBORS = (
    (0, -1, UP),
    (1, 0, RIGHT),
    (0, 1, DOWN),
    (-1, 0, LEFT),
)


class MapView:
    def __init__(self, view_width=s.VIEW_W, view_height=s.VIEW_H,
                 tile_size=s.TILE):
        self.view_width = view_width
        self.view_height = view_height
        self.tile_size = tile_size
        self.surface = pygame.Surface(
            (view_width * tile_size, view_height * tile_size))
        self._scaled_art = {}

    def draw(self, screen, game_map, player, cache, camera, actors=()):
        surface_size = (
            screen.get_width() // s.RENDER_SCALE,
            screen.get_height() // s.RENDER_SCALE,
        )
        if self.surface.get_size() != surface_size:
            self.surface = pygame.Surface(surface_size)
        self.surface.fill(s.BLACK)
        self.view_width = surface_size[0] / self.tile_size
        self.view_height = surface_size[1] / self.tile_size

        camera.view_width = min(self.view_width, game_map.width)
        camera.view_height = min(self.view_height, game_map.height)
        camera.follow(player.fx, player.fy, game_map.width, game_map.height)

        offset_x = max(
            0, (surface_size[0] - game_map.width * self.tile_size) // 2)
        offset_y = max(
            0, (surface_size[1] - game_map.height * self.tile_size) // 2)
        town_scene = _is_town_map(game_map) and "town_background" in cache

        if town_scene:
            self._draw_town_base(
                game_map, cache, camera, offset_x, offset_y, surface_size)
            self._draw_town_props(game_map, cache, camera, offset_x, offset_y)
        else:
            for map_x, map_y, pixel_x, pixel_y in self._visible_tiles(
                    game_map, camera, offset_x, offset_y):
                key = _legacy_tile_key(game_map, map_x, map_y)
                self.surface.blit(cache[key], (pixel_x, pixel_y))

        self._draw_actors(
            cache, camera, player, actors, offset_x, offset_y)
        screen.blit(self.surface, (0, 0))

    def _visible_bounds(self, game_map, camera):
        return (
            max(0, math.floor(camera.x)),
            max(0, math.floor(camera.y)),
            min(game_map.width, math.ceil(camera.x + camera.view_width)),
            min(game_map.height, math.ceil(camera.y + camera.view_height)),
        )

    def _visible_tiles(self, game_map, camera, offset_x, offset_y):
        left, top, right, bottom = self._visible_bounds(game_map, camera)
        for map_y in range(top, bottom):
            for map_x in range(left, right):
                pixel_x, pixel_y = camera.world_to_pixel(
                    map_x, map_y, self.tile_size)
                yield (
                    map_x, map_y, pixel_x + offset_x, pixel_y + offset_y)

    def _draw_town_base(
            self, game_map, cache, camera, offset_x, offset_y, surface_size):
        background = cache[game_map.tile_at(0, 0)]
        for y in range(0, surface_size[1], self.tile_size):
            for x in range(0, surface_size[0], self.tile_size):
                self.surface.blit(
                    background, (x, y),
                    pygame.Rect(
                        x % background.get_width(),
                        y % background.get_height(),
                        self.tile_size, self.tile_size,
                    ))

        size = (game_map.width * self.tile_size,
                game_map.height * self.tile_size)
        art_key = "town_background", size
        if art_key not in self._scaled_art:
            self._scaled_art[art_key] = pygame.transform.scale(
                cache["town_background"], size)
        self.surface.blit(self._scaled_art[art_key], (offset_x, offset_y))

        for map_x, map_y, pixel_x, pixel_y in self._visible_tiles(
                game_map, camera, offset_x, offset_y):
            self._draw_town_cell(
                game_map, cache, map_x, map_y, pixel_x, pixel_y)

    def _draw_town_cell(
            self, game_map, cache, map_x, map_y, pixel_x, pixel_y):
        tile = game_map.tile_at(map_x, map_y)
        if tile == "twall":
            if map_x in (0, game_map.width - 1) \
                    or map_y in (0, game_map.height - 1):
                return
            key = twall_key(_neighbor_mask(game_map, map_x, map_y, tile))
            self.surface.blit(cache[key], (pixel_x, pixel_y))
        elif tile in ("bush", "crate"):
            self.surface.blit(cache[tile], (pixel_x, pixel_y))
        elif tile not in {
                "tfloor", "gate", "counter_weapon", "counter_armor",
                "counter_food", "counter_inn", "counter_casino",
        }:
            self.surface.blit(cache[tile], (pixel_x, pixel_y))

    def _draw_town_props(
            self, game_map, cache, camera, offset_x, offset_y):
        features = []
        for map_x, map_y, pixel_x, pixel_y in self._visible_tiles(
                game_map, camera, offset_x, offset_y):
            tile = game_map.tile_at(map_x, map_y)
            if not tile.startswith("counter_"):
                continue
            service = tile.removeprefix("counter_")
            features.append((
                map_y, map_x, f"town_prop_{service}",
                (pixel_x - 38, pixel_y - 88),
            ))
        size = (204, 153)
        for _, _, key, position in sorted(features):
            if key not in cache:
                continue
            art_key = key, size
            if art_key not in self._scaled_art:
                self._scaled_art[art_key] = pygame.transform.scale(
                    cache[key], size)
            self.surface.blit(self._scaled_art[art_key], position)

    def _draw_actors(
            self, cache, camera, player, actors, offset_x, offset_y):
        for actor in actors:
            actor_x, actor_y = camera.world_to_pixel(
                actor.fx, actor.fy, self.tile_size)
            self.surface.blit(
                cache[actor.sprite],
                (actor_x + offset_x, actor_y + offset_y))
        player_x, player_y = camera.world_to_pixel(
            player.fx, player.fy, self.tile_size)
        player_key = f"{PLAYER}:{getattr(player, 'facing', 'down')}"
        self.surface.blit(
            cache[player_key], (player_x + offset_x, player_y + offset_y))


def _neighbor_mask(game_map, x, y, tile):
    mask = 0
    for dx, dy, bit in WATER_NEIGHBORS:
        nx, ny = x + dx, y + dy
        if game_map.in_bounds(nx, ny) and game_map.tile_at(nx, ny) == tile:
            mask |= bit
    return mask


def _variant(x, y, count):
    return (x * 17 + y * 31 + x * y * 3) % count


def _legacy_tile_key(game_map, map_x, map_y):
    tile = game_map.tile_at(map_x, map_y)
    if tile == "grass":
        return grass_key(_variant(map_x, map_y, GRASS_VARIANTS))
    if tile == "sand":
        return sand_key(_variant(map_x, map_y, SAND_VARIANTS))
    if tile == "water":
        return water_key(
            _neighbor_mask(game_map, map_x, map_y, tile),
            _variant(map_x, map_y, WATER_VARIANTS),
        )
    if tile == "tree":
        return tree_key(_neighbor_mask(game_map, map_x, map_y, tile))
    if tile == "mountain":
        return mountain_key(_neighbor_mask(game_map, map_x, map_y, tile))
    if tile == "twall":
        return twall_key(_neighbor_mask(game_map, map_x, map_y, tile))
    return tile


def _is_town_map(game_map):
    return any(tile.startswith("counter_") for tile in game_map.tiles())

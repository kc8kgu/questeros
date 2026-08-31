"""Shared map exploration, movement, inventory, and overlay behavior."""
import pygame

import inventory
from scenes.base import Scene

DELTAS = {
    "up": (0, -1),
    "down": (0, 1),
    "left": (-1, 0),
    "right": (1, 0),
}


class ExplorationScene(Scene):
    def __init__(self, game, game_map):
        super().__init__(game)
        self.game_map = game_map
        self.menu = None
        self.inventory = None
        self.held = {direction: False for direction in DELTAS}
        self.directions = {
            pygame.K_UP: "up", pygame.K_w: "up",
            pygame.K_DOWN: "down", pygame.K_s: "down",
            pygame.K_LEFT: "left", pygame.K_a: "left",
            pygame.K_RIGHT: "right", pygame.K_d: "right",
        }

    def on_exit(self):
        for direction in self.held:
            self.held[direction] = False

    def cancel_overlay(self):
        if self.inventory:
            self.inventory = None
            return True
        if self.menu:
            self.menu = None
            return True
        return False

    def handle_event(self, event):
        if event.type == pygame.KEYUP and event.key in self.directions:
            self.held[self.directions[event.key]] = False
            return True
        if event.type != pygame.KEYDOWN:
            return True

        key = event.key
        if self.inventory:
            if key in (pygame.K_UP, pygame.K_w):
                self.inventory.move(-1)
            elif key in (pygame.K_DOWN, pygame.K_s):
                self.inventory.move(1)
            elif key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.inventory.confirm()
            elif key in (pygame.K_ESCAPE, pygame.K_i):
                self.inventory = None
            return True

        if key == pygame.K_ESCAPE:
            return self.cancel_overlay()

        if self.menu:
            if key in (pygame.K_UP, pygame.K_w):
                self.menu.move(-1)
            elif key in (pygame.K_DOWN, pygame.K_s):
                self.menu.move(1)
            elif key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.menu_selected()
            return True

        if key == pygame.K_i:
            self.inventory = inventory.Inventory(self.game.player)
            return True
        if key in self.directions:
            self.held[self.directions[key]] = True
        return True

    def update(self, dt):
        player = self.game.player
        if not self.menu and not self.inventory and not player.dead \
                and not player.target:
            for direction in ("up", "down", "left", "right"):
                if self.held[direction]:
                    dx, dy = DELTAS[direction]
                    player.try_step(dx, dy, self.game_map)
                    break

        player.update(dt)
        if player.just_arrived:
            player.just_arrived = False
            self.on_arrive()

    def map_actors(self):
        return ()

    def draw(self):
        game = self.game
        game.map_view.draw(
            game.screen, self.game_map, game.player, game.cache, game.camera,
            actors=self.map_actors())
        if self.menu:
            self.menu.draw(game.screen, game.cache)
        if self.inventory:
            self.inventory.draw(game.screen, game.cache)

    def on_arrive(self):
        pass

    def menu_selected(self):
        pass

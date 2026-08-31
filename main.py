"""Questeros — a Questron/Ultima-style RPG prototype.

Milestone 1: walkable overworld (grid movement, collision, camera).
Milestone 2: player stats + status bar (HP, gold, food, level, XP).
Milestone 3: towns (counters, vendors, guards, casino) + inventory.
Milestone 4: random encounters + turn-based combat.
Milestone 5: dragon boss + explicit victory ending.
Milestone 6: single-slot save and continue support.

Run:  ./quest
"""
import argparse
import math
import sys
from pathlib import Path

import pygame

import graphics
import hud
import map_view
import savegame
import settings as s
import town
import world
from camera import Camera
from player import Player
from scenes import TitleScene, TownScene, WorldScene

DEFAULT_WORLD_SEED = 42
SAVE_NOTICE_MS = 2000


class Game:
    def __init__(self, no_encounters=False, god_mode=False, save_path=None):
        pygame.init()
        hud.reset_fonts()
        self.screen = pygame.Surface(s.RENDER_SIZE)
        self.window = pygame.display.set_mode(s.WINDOW_SIZE, pygame.RESIZABLE)
        self.windowed_size = self.window.get_size()
        self.fullscreen = False
        self._resize_canvas()
        pygame.display.set_caption("Questeros")
        self.clock = pygame.time.Clock()
        self.cache = graphics.build_cache()
        self.camera = Camera(s.VIEW_W, s.VIEW_H)
        self.map_view = map_view.MapView()
        self.save_path = (
            Path(save_path) if save_path is not None
            else savegame.default_path())
        self.start_no_encounters = no_encounters
        self.start_god_mode = god_mode
        self.world_seed = None
        self.world_map = None
        self.towns = []
        self.encounters_enabled = True
        self.player = None
        self.save_notice = ""
        self.save_notice_color = s.GREY
        self.save_notice_until = 0
        self.quit_confirm = False
        self.scene = None
        self.change_scene(TitleScene(self))

    # --- scenes ----------------------------------------------------------------

    def change_scene(self, scene):
        if self.scene:
            self.scene.on_exit()
        self.scene = scene

    def start_new_game(
            self, no_encounters=False, god_mode=False,
            world_seed=DEFAULT_WORLD_SEED):
        self.world_seed = world_seed
        self.world_map, self.towns = world.generate(world_seed)
        self.encounters_enabled = not no_encounters
        self.player = Player(
            *world.find_start(self.world_map), god_mode=god_mode)
        self.save_notice = ""
        self.change_scene(WorldScene(self))

    def restart(self):
        self.start_new_game(world_seed=self.world_seed or DEFAULT_WORLD_SEED)

    # --- save games -------------------------------------------------------------

    def save_current_game(self):
        if not isinstance(self.scene, (WorldScene, TownScene)) \
                or not self.player or self.player.dead:
            self._set_save_notice("You cannot save here.", s.LTRED)
            return False
        if self.player.invincible:
            self._set_save_notice(
                "Disable god mode before saving.", s.LTRED)
            return False

        player = self.player
        if isinstance(self.scene, TownScene):
            location = {
                "kind": "town",
                "x": player.x,
                "y": player.y,
                "town_x": self.scene.town_x,
                "town_y": self.scene.town_y,
                "return_x": self.scene.return_pos[0],
                "return_y": self.scene.return_pos[1],
            }
        else:
            location = {
                "kind": "world",
                "x": player.x,
                "y": player.y,
            }

        try:
            savegame.save_game(
                self.save_path, self.world_seed, player, location)
        except savegame.SaveGameError as exc:
            self._set_save_notice(str(exc), s.LTRED)
            return False
        self._set_save_notice("Game saved.", s.LTGREEN)
        return True

    def load_saved_game(self):
        try:
            world_seed, player, location = savegame.load_game(self.save_path)
            world_map, towns = world.generate(world_seed)
            self._validate_loaded_location(world_map, towns, location)
        except savegame.SaveGameError as exc:
            return str(exc)

        self.world_seed = world_seed
        self.world_map = world_map
        self.towns = towns
        self.player = player
        self.encounters_enabled = True
        self.save_notice = ""

        world_scene = WorldScene(self)
        if location["kind"] == "world":
            self.change_scene(world_scene)
        else:
            town_scene = TownScene(
                self, world_scene,
                location["town_x"], location["town_y"],
                (location["return_x"], location["return_y"]))
            self._place_player(location["x"], location["y"])
            self.change_scene(town_scene)
        return None

    def continue_saved_game(self):
        error = self.load_saved_game()
        if not error:
            return True
        self.restart()
        self._set_save_notice(
            f"{error} Starting a new game.", s.LTRED)
        return False

    @staticmethod
    def _validate_loaded_location(world_map, towns, location):
        if location["kind"] == "world":
            if not world_map.is_walkable(location["x"], location["y"]):
                raise savegame.SaveGameError(
                    "The saved world position is invalid.")
            return

        town_pos = location["town_x"], location["town_y"]
        return_pos = location["return_x"], location["return_y"]
        if town_pos not in towns or not world_map.is_walkable(*return_pos):
            raise savegame.SaveGameError(
                "The saved town position is invalid.")
        town_map, _ = town.generate(*town_pos)
        if not town_map.is_walkable(location["x"], location["y"]):
            raise savegame.SaveGameError(
                "The saved town position is invalid.")

    def _place_player(self, x, y):
        player = self.player
        player.x, player.y = x, y
        player.fx, player.fy = float(x), float(y)
        player.last_pos = (x, y)
        player.target = None

    def _set_save_notice(self, text, color):
        self.save_notice = text
        self.save_notice_color = color
        self.save_notice_until = pygame.time.get_ticks() + SAVE_NOTICE_MS

    def toggle_fullscreen(self):
        if self.fullscreen:
            self.window = pygame.display.set_mode(
                self.windowed_size, pygame.RESIZABLE)
            self.fullscreen = False
        else:
            self.windowed_size = self.window.get_size()
            self.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.fullscreen = True
        self._resize_canvas()

    def _resize_canvas(self):
        window_w, window_h = self.window.get_size()
        base_w, base_h = s.RENDER_SIZE
        if window_w * base_h >= window_h * base_w:
            render_w = math.ceil(
                base_h * window_w / window_h / s.RENDER_SCALE)
            render_size = (render_w * s.RENDER_SCALE, base_h)
        else:
            render_h = math.ceil(
                base_w * window_h / window_w / s.RENDER_SCALE)
            render_size = (base_w, render_h * s.RENDER_SCALE)
        self.screen = pygame.Surface(render_size)

    # --- events ----------------------------------------------------------------

    def handle_event(self, event):
        """Returns False when the game should quit."""
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN and self.quit_confirm:
            if event.key in (
                    pygame.K_y, pygame.K_RETURN, pygame.K_KP_ENTER,
                    pygame.K_SPACE):
                return False
            if event.key in (pygame.K_n, pygame.K_ESCAPE):
                self.quit_confirm = False
            return True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            self.quit_confirm = True
            return True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if not self.scene.cancel_overlay():
                self.quit_confirm = True
            return True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
            self.toggle_fullscreen()
            return True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F5:
            self.save_current_game()
            return True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_g \
                and self.player:
            self.player.toggle_god_mode()
            return True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_e \
                and self.player:
            self.encounters_enabled = not self.encounters_enabled
            return True
        if event.type == pygame.VIDEORESIZE and not self.fullscreen:
            self.windowed_size = (max(1, event.w), max(1, event.h))
            self.window = pygame.display.set_mode(
                self.windowed_size, pygame.RESIZABLE)
            self._resize_canvas()
            return True
        if event.type == pygame.KEYDOWN and self.player and self.player.dead:
            if event.key == pygame.K_r:
                self.restart()
            elif event.key == pygame.K_c:
                self.continue_saved_game()
            return True
        return self.scene.handle_event(event)

    # --- rendering ----------------------------------------------------------------

    def render(self):
        self.scene.draw()
        if self.scene.show_stats and self.player:
            hud.draw_stats_bar(
                self.screen, self.player, self.cache,
                encounters_enabled=self.encounters_enabled)
        if self.save_notice and not (self.player and self.player.dead) and \
                pygame.time.get_ticks() < self.save_notice_until:
            hud.draw_notice(
                self.screen, self.save_notice, self.save_notice_color,
                self.cache)
        if self.player and self.player.dead:
            hud.draw_death(
                self.screen, self.save_path.is_file(), self.cache)
        if self.quit_confirm:
            hud.draw_quit_confirm(self.screen, self.cache)
        self._present()
        pygame.display.flip()

    def _present(self):
        pygame.transform.scale(
            self.screen, self.window.get_size(), self.window)

    # --- main loop ----------------------------------------------------------------

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(s.FPS) / 1000.0
            for event in pygame.event.get():
                if not self.handle_event(event):
                    running = False
            self.scene.update(dt)
            self.render()
        pygame.quit()


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--no-encounters", action="store_true",
        help="disable random overworld encounters")
    parser.add_argument(
        "--god-mode", action="store_true",
        help="start with 1000 HP, 1000 gold, and invincibility")
    return parser.parse_args(argv)


def main():
    args = parse_args()
    Game(
        no_encounters=args.no_encounters,
        god_mode=args.god_mode,
    ).run()
    sys.exit(0)


if __name__ == "__main__":
    main()

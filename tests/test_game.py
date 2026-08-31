"""Headless integration tests for game services and input routing."""
import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import battle_view
import combat
import items
import settings as s
import town
from main import Game, parse_args
from battle_feedback import HIT_DURATION
from scenes import BattleScene, TitleScene, TownScene, WinScene, WorldScene


class GameIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.save_dir = TemporaryDirectory()
        self.save_path = Path(self.save_dir.name) / "savegame.json"
        self.game = Game(save_path=self.save_path)
        self.game.start_new_game()

    def tearDown(self):
        pygame.quit()
        self.save_dir.cleanup()

    @staticmethod
    def key_event(key):
        return pygame.event.Event(pygame.KEYDOWN, key=key)

    def enter_town(self):
        world_scene = self.game.scene
        tx, ty = self.game.towns[0]
        return_pos = next(
            (tx + dx, ty + dy)
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1))
            if self.game.world_map.is_walkable(tx + dx, ty + dy)
        )
        player = self.game.player
        player.x, player.y = tx, ty
        player.last_pos = return_pos
        world_scene.on_arrive()
        return world_scene, self.game.scene, return_pos

    def start_battle(self, return_scene=None):
        return_scene = return_scene or self.game.scene
        scene = BattleScene(
            self.game, return_scene, dict(combat.MONSTERS[0]))
        self.game.change_scene(scene)
        return scene

    def test_game_starts_in_world_scene(self):
        self.assertIsInstance(self.game.scene, WorldScene)

    def test_title_screen_starts_a_new_game(self):
        game = Game(save_path=self.save_path)

        self.assertIsInstance(game.scene, TitleScene)
        game.handle_event(self.key_event(pygame.K_RETURN))

        self.assertIsInstance(game.scene, WorldScene)
        self.assertIsNotNone(game.player)

    def test_game_uses_larger_resizable_window_and_base_canvas(self):
        self.assertEqual(self.game.screen.get_size(), s.RENDER_SIZE)
        self.assertEqual(self.game.window.get_size(), s.WINDOW_SIZE)
        self.assertTrue(self.game.window.get_flags() & pygame.RESIZABLE)

    def test_window_can_be_resized(self):
        size = (1100, 700)

        keep_running = self.game.handle_event(pygame.event.Event(
            pygame.VIDEORESIZE, size=size, w=size[0], h=size[1]))

        self.assertTrue(keep_running)
        self.assertEqual(self.game.windowed_size, size)
        self.assertEqual(self.game.window.get_size(), size)
        self.assertGreater(self.game.screen.get_width(), s.RENDER_SIZE[0])
        self.assertEqual(self.game.screen.get_height(), s.RENDER_SIZE[1])
        self.game.render()
        self.assertGreater(self.game.camera.view_width, s.VIEW_W)

    def test_tall_window_expands_vertical_viewport(self):
        size = (700, 1100)

        self.game.handle_event(pygame.event.Event(
            pygame.VIDEORESIZE, size=size, w=size[0], h=size[1]))
        self.game.render()

        self.assertEqual(self.game.screen.get_width(), s.RENDER_SIZE[0])
        self.assertGreater(self.game.screen.get_height(), s.RENDER_SIZE[1])
        self.assertGreater(self.game.camera.view_height, s.VIEW_H)

    def test_presented_frame_fills_resized_window(self):
        size = (1100, 700)
        self.game.handle_event(pygame.event.Event(
            pygame.VIDEORESIZE, size=size, w=size[0], h=size[1]))
        self.game.screen.fill(s.WHITE)

        self.game._present()

        self.assertEqual(self.game.window.get_at((0, 0))[:3], s.WHITE)
        self.assertEqual(
            self.game.window.get_at((size[0] - 1, size[1] - 1))[:3],
            s.WHITE,
        )

    def test_f11_toggles_fullscreen_and_restores_window_size(self):
        windowed_size = self.game.window.get_size()
        fullscreen_surface = pygame.Surface((1600, 900))
        windowed_surface = pygame.Surface(windowed_size)

        with patch(
                "main.pygame.display.set_mode",
                side_effect=[fullscreen_surface, windowed_surface]) as set_mode:
            self.game.handle_event(self.key_event(pygame.K_F11))
            self.assertTrue(self.game.fullscreen)
            self.assertIs(self.game.window, fullscreen_surface)

            self.game.handle_event(self.key_event(pygame.K_F11))
            self.assertFalse(self.game.fullscreen)
            self.assertIs(self.game.window, windowed_surface)

        self.assertEqual(
            set_mode.call_args_list,
            [
                unittest.mock.call((0, 0), pygame.FULLSCREEN),
                unittest.mock.call(windowed_size, pygame.RESIZABLE),
            ],
        )

    def test_town_entry_and_gate_exit_restore_world_position(self):
        world_scene, town_scene, return_pos = self.enter_town()
        player = self.game.player

        self.assertIsInstance(town_scene, TownScene)
        self.assertEqual((player.x, player.y), town.SPAWN)
        self.assertEqual(town_scene.return_pos, return_pos)

        player.x, player.y = town.GATE_X, s.TOWN_H - 1
        town_scene.on_arrive()

        self.assertIs(self.game.scene, world_scene)
        self.assertEqual((player.x, player.y), return_pos)

    def test_grass_arrival_can_start_a_battle(self):
        monster = dict(combat.MONSTERS[0])

        world_scene = self.game.scene
        with patch("scenes.world.random.random", return_value=0.0), \
                patch("scenes.world.combat.pick_monster", return_value=monster):
            world_scene.on_arrive()

        self.assertIsInstance(self.game.scene, BattleScene)
        self.assertIs(self.game.scene.return_scene, world_scene)
        self.assertEqual(self.game.scene.battle.monster, monster)
        self.assertEqual(self.game.scene.terrain, "grass")

    def test_boss_arrival_starts_the_dragon_battle(self):
        world_scene = self.game.scene
        boss_pos = next(
            (x, y)
            for y in range(self.game.world_map.height)
            for x in range(self.game.world_map.width)
            if self.game.world_map.tile_at(x, y) == "boss"
        )
        self.game.player.x, self.game.player.y = boss_pos

        world_scene.on_arrive()

        self.assertIsInstance(self.game.scene, BattleScene)
        self.assertIs(self.game.scene.return_scene, world_scene)
        self.assertIs(
            self.game.scene.battle.monster, combat.BOSS_MONSTER)
        self.assertEqual(self.game.scene.terrain, "boss")

    def test_random_encounters_can_be_disabled(self):
        self.game.encounters_enabled = False
        world_scene = self.game.scene

        with patch("scenes.world.random.random") as random_roll:
            world_scene.on_arrive()

        random_roll.assert_not_called()
        self.assertIs(self.game.scene, world_scene)

    def test_escape_opens_quit_confirmation_during_an_active_battle(self):
        battle_scene = self.start_battle()

        keep_running = self.game.handle_event(self.key_event(pygame.K_ESCAPE))

        self.assertTrue(keep_running)
        self.assertIs(self.game.scene, battle_scene)
        self.assertTrue(self.game.quit_confirm)

        self.game.handle_event(self.key_event(pygame.K_ESCAPE))

        self.assertFalse(self.game.quit_confirm)

    def test_any_key_closes_a_finished_battle(self):
        world_scene = self.game.scene
        battle_scene = self.start_battle(world_scene)
        battle_scene.battle.over = True

        self.game.handle_event(self.key_event(pygame.K_SPACE))

        self.assertIs(self.game.scene, world_scene)

    def test_defeating_the_boss_opens_the_victory_scene(self):
        world_scene = self.game.scene
        battle_scene = BattleScene(
            self.game, world_scene, combat.BOSS_MONSTER)
        self.game.change_scene(battle_scene)
        battle_scene.battle.over = True
        battle_scene.battle.result = "won"

        self.game.handle_event(self.key_event(pygame.K_SPACE))

        self.assertIsInstance(self.game.scene, WinScene)

    def test_victory_scene_renders_and_can_restart(self):
        original_player = self.game.player
        self.game.change_scene(WinScene(self.game))

        self.game.render()
        self.game.handle_event(self.key_event(pygame.K_r))

        self.assertIsInstance(self.game.scene, WorldScene)
        self.assertIsNot(self.game.player, original_player)

    def test_inventory_key_opens_and_closes_inventory(self):
        world_scene = self.game.scene
        self.game.handle_event(self.key_event(pygame.K_i))
        self.assertIsNotNone(world_scene.inventory)

        self.game.handle_event(self.key_event(pygame.K_i))
        self.assertIsNone(world_scene.inventory)

    def test_overworld_q_asks_before_quitting(self):
        self.assertTrue(self.game.handle_event(self.key_event(pygame.K_q)))
        self.assertTrue(self.game.quit_confirm)
        self.assertFalse(self.game.handle_event(self.key_event(pygame.K_y)))

    def test_escape_closes_inventory_before_asking_to_quit(self):
        world_scene = self.game.scene
        self.game.handle_event(self.key_event(pygame.K_i))

        self.game.handle_event(self.key_event(pygame.K_ESCAPE))

        self.assertIsNone(world_scene.inventory)
        self.assertFalse(self.game.quit_confirm)

    def test_overworld_g_toggles_god_mode(self):
        player = self.game.player

        self.game.handle_event(self.key_event(pygame.K_g))

        self.assertEqual(player.hp, 1000)
        self.assertEqual(player.max_hp, 1000)
        self.assertEqual(player.gold, 1000)
        self.assertTrue(player.invincible)

        self.game.handle_event(self.key_event(pygame.K_g))

        self.assertEqual(player.hp, 50)
        self.assertEqual(player.max_hp, 50)
        self.assertEqual(player.gold, 100)
        self.assertFalse(player.invincible)

    def test_overworld_e_disables_random_encounters(self):
        self.assertTrue(self.game.encounters_enabled)

        self.game.handle_event(self.key_event(pygame.K_e))

        self.assertFalse(self.game.encounters_enabled)

    def test_f5_saves_and_title_continue_restores_world_state(self):
        player = self.game.player
        player.max_hp = 70
        player.hp = 44
        player.gold = 321
        player.food = 53
        player.level = 3
        player.xp = 27
        player.steps = 88
        player._since_food = 7
        player._since_starve = 2
        player.weapon = 1
        player.armor = 1
        player.weapons_owned.add(1)
        player.armors_owned.add(1)
        saved_position = player.x, player.y

        self.game.handle_event(self.key_event(pygame.K_F5))

        self.assertTrue(self.save_path.is_file())
        loaded = Game(save_path=self.save_path)
        self.assertIsInstance(loaded.scene, TitleScene)
        self.assertTrue(loaded.scene.menu.options[1][1])
        loaded.handle_event(self.key_event(pygame.K_DOWN))
        loaded.handle_event(self.key_event(pygame.K_RETURN))

        self.assertIsInstance(loaded.scene, WorldScene)
        self.assertEqual((loaded.player.x, loaded.player.y), saved_position)
        self.assertEqual(loaded.player.hp, 44)
        self.assertEqual(loaded.player.max_hp, 70)
        self.assertEqual(loaded.player.gold, 321)
        self.assertEqual(loaded.player.food, 53)
        self.assertEqual(loaded.player.level, 3)
        self.assertEqual(loaded.player.xp, 27)
        self.assertEqual(loaded.player.steps, 88)
        self.assertEqual(loaded.player._since_food, 7)
        self.assertEqual(loaded.player._since_starve, 2)
        self.assertEqual(loaded.player.weapon, 1)
        self.assertEqual(loaded.player.armor, 1)

    def test_town_save_restores_local_and_return_positions(self):
        _, town_scene, return_pos = self.enter_town()
        saved_position = self.game.player.x, self.game.player.y
        town_pos = town_scene.town_x, town_scene.town_y
        self.game.player.gold = 234

        self.game.handle_event(self.key_event(pygame.K_F5))
        loaded = Game(save_path=self.save_path)
        error = loaded.load_saved_game()

        self.assertIsNone(error)
        self.assertIsInstance(loaded.scene, TownScene)
        self.assertEqual(
            (loaded.scene.town_x, loaded.scene.town_y), town_pos)
        self.assertEqual(loaded.scene.return_pos, return_pos)
        self.assertEqual((loaded.player.x, loaded.player.y), saved_position)
        self.assertEqual(loaded.player.gold, 234)

    def test_saving_is_blocked_during_battle_and_god_mode(self):
        with patch("main.savegame.save_game") as save:
            self.start_battle()
            self.game.handle_event(self.key_event(pygame.K_F5))
            save.assert_not_called()

            self.game.change_scene(WorldScene(self.game))
            self.game.player.toggle_god_mode()
            self.game.handle_event(self.key_event(pygame.K_F5))
            save.assert_not_called()

    def test_corrupt_title_continue_warns_and_starts_a_new_game(self):
        self.save_path.write_text("{", encoding="utf-8")
        game = Game(save_path=self.save_path)
        game.handle_event(self.key_event(pygame.K_DOWN))

        game.handle_event(self.key_event(pygame.K_RETURN))

        self.assertIsInstance(game.scene, WorldScene)
        self.assertFalse(game.player.dead)
        self.assertEqual(
            game.save_notice,
            "The saved game could not be read. Starting a new game.")

    def test_status_bar_changes_with_runtime_modes(self):
        self.game.render()
        w, h = self.game.screen.get_size()
        indicator_area = pygame.Rect(w - 180, h - 34, 180, 34)
        normal = pygame.image.tobytes(
            self.game.screen.subsurface(indicator_area), "RGB")

        self.game.handle_event(self.key_event(pygame.K_g))
        self.game.handle_event(self.key_event(pygame.K_e))
        self.game.render()
        cheats = pygame.image.tobytes(
            self.game.screen.subsurface(indicator_area), "RGB")

        self.assertNotEqual(normal, cheats)

    def test_world_scene_updates_player_movement(self):
        world_scene = self.game.scene
        player = self.game.player
        start = (player.x, player.y)
        directions = {
            "up": (0, -1), "down": (0, 1),
            "left": (-1, 0), "right": (1, 0),
        }
        direction, delta = next(
            (name, delta) for name, delta in directions.items()
            if world_scene.game_map.is_walkable(
                player.x + delta[0], player.y + delta[1])
            and world_scene.game_map.tile_at(
                player.x + delta[0], player.y + delta[1]) == "grass"
        )
        world_scene.held[direction] = True

        with patch("scenes.world.random.random", return_value=1.0):
            world_scene.update(s.STEP_TIME)

        self.assertEqual(
            (player.x, player.y),
            (start[0] + delta[0], start[1] + delta[1]))

    def test_town_scene_counter_opens_its_menu(self):
        _, town_scene, _ = self.enter_town()
        vendor = town_scene.town_state.vendors[0]
        self.game.player.x, self.game.player.y = vendor.counter_x, vendor.counter_y

        town_scene.on_arrive()

        self.assertEqual(town_scene.menu.kind, vendor.service)

    def test_town_service_menus_have_one_icon_per_option(self):
        _, town_scene, _ = self.enter_town()
        inn = town_scene.build_inn_menu()
        weapon = town_scene.build_weapon_menu()
        vendor = town_scene.town_state.vendors[0]
        crime = town_scene.build_vendor_menu(vendor)

        self.assertEqual(len(inn.icons), len(inn.options))
        self.assertEqual(len(weapon.icons), len(weapon.options))
        self.assertEqual(len(crime.icons), len(crime.options))

    def test_battle_scene_routes_selected_action(self):
        battle_scene = self.start_battle()
        self.game.handle_event(self.key_event(pygame.K_DOWN))

        with patch.object(battle_scene.battle, "act") as act:
            self.game.handle_event(self.key_event(pygame.K_SPACE))

        self.assertEqual(battle_scene.selected, 1)
        act.assert_called_once_with(combat.ACTION_EAT)

    def test_battle_attack_queues_ordered_feedback_and_locks_input(self):
        battle_scene = self.start_battle()
        with patch("combat.random.randint", side_effect=[0, 1]):
            self.game.handle_event(self.key_event(pygame.K_SPACE))

        self.assertTrue(battle_scene.feedback.active)
        self.assertEqual(
            [event.target for event in battle_scene.feedback.events],
            ["monster", "player"])
        self.assertTrue(battle_scene.feedback.events[0].slash)

        self.game.handle_event(self.key_event(pygame.K_DOWN))
        self.assertEqual(battle_scene.selected, 0)

        battle_scene.update(HIT_DURATION)
        self.assertEqual(battle_scene.feedback.current.target, "player")
        battle_scene.update(HIT_DURATION)
        self.assertFalse(battle_scene.feedback.active)

    def test_battle_eat_feedback_accounts_for_healing_before_damage(self):
        battle_scene = self.start_battle()
        player = self.game.player
        player.hp = 20
        player.food = 20
        battle_scene.selected = combat.ACTIONS.index(combat.ACTION_EAT)

        with patch("combat.random.randint", return_value=0):
            self.game.handle_event(self.key_event(pygame.K_SPACE))

        self.assertEqual(len(battle_scene.feedback.events), 1)
        event = battle_scene.feedback.current
        self.assertEqual(event.target, "player")
        self.assertEqual(event.damage, battle_scene.battle.monster["atk"] - 1)

    def test_finished_battle_cannot_close_until_feedback_finishes(self):
        world_scene = self.game.scene
        battle_scene = self.start_battle(world_scene)
        battle_scene.battle.mhp = 1
        with patch("combat.random.randint", side_effect=[0, 0]):
            self.game.handle_event(self.key_event(pygame.K_SPACE))

        self.assertTrue(battle_scene.battle.over)
        self.game.handle_event(self.key_event(pygame.K_SPACE))
        self.assertIs(self.game.scene, battle_scene)

        battle_scene.update(HIT_DURATION)
        self.game.handle_event(self.key_event(pygame.K_SPACE))
        self.assertIs(self.game.scene, world_scene)

    def test_battle_feedback_effect_frame_renders_headlessly(self):
        battle_scene = self.start_battle()
        with patch("combat.random.randint", side_effect=[0, 1]):
            self.game.handle_event(self.key_event(pygame.K_SPACE))
        battle_scene.update(HIT_DURATION * 0.25)

        self.assertNotEqual(battle_view.shake_offset(battle_scene.feedback), (0, 0))
        self.assertNotEqual(
            battle_view.recoil_offset(battle_scene.feedback, "monster"),
            (0, 0))
        self.assertEqual(
            battle_view.recoil_offset(battle_scene.feedback, "player"),
            (0, 0))
        self.game.render()

    def test_battle_recoil_moves_each_struck_combatant_away_and_back(self):
        battle_scene = self.start_battle()
        with patch("combat.random.randint", side_effect=[0, 1]):
            self.game.handle_event(self.key_event(pygame.K_SPACE))

        feedback = battle_scene.feedback
        battle_scene.update(HIT_DURATION * battle_view.RECOIL_PEAK)
        self.assertEqual(
            battle_view.recoil_offset(feedback, "monster"),
            battle_view.RECOIL_DISTANCE["monster"])

        battle_scene.update(HIT_DURATION)
        self.assertEqual(feedback.current.target, "player")
        self.assertEqual(
            battle_view.recoil_offset(feedback, "player"),
            battle_view.RECOIL_DISTANCE["player"])

        battle_scene.update(
            HIT_DURATION * (battle_view.RECOIL_END - battle_view.RECOIL_PEAK))
        self.assertEqual(
            battle_view.recoil_offset(feedback, "player"), (0, 0))

    def test_battle_recoil_rejects_unknown_targets(self):
        battle_scene = self.start_battle()
        with self.assertRaises(ValueError):
            battle_view.recoil_offset(battle_scene.feedback, "floor")

    def test_inn_rest_heals_and_charges_player(self):
        _, town_scene, _ = self.enter_town()
        player = self.game.player
        player.hp = 1
        player.gold = 100
        town_scene.menu = town_scene.build_inn_menu()

        town_scene.inn_selected(0)

        self.assertEqual(player.hp, player.max_hp)
        self.assertEqual(player.gold, 100 - items.INN_REST)

    def test_weapon_purchase_owns_and_equips_gear(self):
        _, town_scene, _ = self.enter_town()
        player = self.game.player
        player.gold = 1000
        town_scene.menu = town_scene.build_weapon_menu()
        weapon_index = 1
        menu_index = town_scene.menu.entries.index(weapon_index)

        town_scene.weapon_selected(menu_index)

        self.assertIn(weapon_index, player.weapons_owned)
        self.assertEqual(player.weapon, weapon_index)
        self.assertEqual(player.gold, 1000 - items.WEAPONS[weapon_index][1])

    def test_robbing_vendor_alerts_guards(self):
        _, town_scene, _ = self.enter_town()
        vendor = town_scene.town_state.vendors[0]
        town_scene.menu = town_scene.build_vendor_menu(vendor)

        with patch("town_crime.rob_gold", return_value=15):
            town_scene.vendor_selected(0)

        self.assertTrue(vendor.robbed)
        self.assertTrue(town_scene.town_state.alerted)
        self.assertTrue(all(guard.hostile for guard in town_scene.town_state.guards))

    def test_generated_map_tiles_and_monsters_have_cached_art(self):
        world_tiles = set(self.game.world_map.tiles())
        town_map, _ = town.generate(*self.game.towns[0])
        town_tiles = set(town_map.tiles())
        monster_tiles = {f"mon_{monster['id']}" for monster in combat.MONSTERS}

        self.assertTrue(world_tiles <= self.game.cache.keys())
        self.assertTrue(town_tiles <= self.game.cache.keys())
        self.assertTrue(monster_tiles <= self.game.cache.keys())
        self.assertIn("player", self.game.cache)
        self.assertIn("vendor", self.game.cache)
        self.assertIn("guard", self.game.cache)

    def test_map_view_renders_static_player_while_moving(self):
        player = self.game.player
        player.facing = "left"
        player.target = (player.x - 1, player.y)
        player.t = 0.7

        self.game.render()

        self.assertTrue({
            "player", "player:up", "player:down", "player:left",
            "player:right",
        } <= self.game.cache.keys())

    def test_primary_screens_render_headlessly(self):
        self.game.render()

        _, town_scene, _ = self.enter_town()
        town_scene.menu = town_scene.build_inn_menu()
        self.game.render()

        town_scene.menu = None
        self.game.handle_event(self.key_event(pygame.K_i))
        self.game.render()

        town_scene.inventory = None
        self.start_battle(town_scene)
        self.game.render()

    def test_primary_screens_render_after_wide_resize(self):
        size = (1600, 900)
        self.game.handle_event(pygame.event.Event(
            pygame.VIDEORESIZE, size=size, w=size[0], h=size[1]))
        self.game.render()

        _, town_scene, _ = self.enter_town()
        town_scene.menu = town_scene.build_inn_menu()
        self.game.render()

        town_scene.menu = None
        self.game.handle_event(self.key_event(pygame.K_i))
        self.game.render()

        town_scene.inventory = None
        self.start_battle(town_scene)
        self.game.render()

    def test_scene_exit_releases_held_movement(self):
        world_scene = self.game.scene
        world_scene.held["right"] = True

        self.start_battle(world_scene)

        self.assertFalse(any(world_scene.held.values()))

    def test_restart_replaces_dead_state_with_new_world_scene(self):
        original_player = self.game.player
        original_player.dead = True

        self.game.handle_event(self.key_event(pygame.K_r))

        self.assertIsInstance(self.game.scene, WorldScene)
        self.assertIsNot(self.game.player, original_player)
        self.assertFalse(self.game.player.dead)

    def test_continue_from_death_restores_the_last_save(self):
        original_player = self.game.player
        original_player.gold = 456
        saved_position = original_player.x, original_player.y
        self.game.handle_event(self.key_event(pygame.K_F5))
        original_player.gold = 0
        original_player.take_damage(original_player.hp)

        self.game.handle_event(self.key_event(pygame.K_c))

        self.assertIsInstance(self.game.scene, WorldScene)
        self.assertIsNot(self.game.player, original_player)
        self.assertFalse(self.game.player.dead)
        self.assertEqual(self.game.player.gold, 456)
        self.assertEqual(
            (self.game.player.x, self.game.player.y), saved_position)

    def test_failed_continue_from_death_warns_and_restarts(self):
        player = self.game.player
        player.take_damage(player.hp)

        self.game.handle_event(self.key_event(pygame.K_c))
        self.game.render()

        self.assertIsInstance(self.game.scene, WorldScene)
        self.assertIsNot(self.game.player, player)
        self.assertFalse(self.game.player.dead)
        self.assertEqual(
            self.game.save_notice,
            "No saved game found. Starting a new game.")

    def test_restart_disables_cheats(self):
        game = Game(
            no_encounters=True, god_mode=True, save_path=self.save_path)
        game.start_new_game(no_encounters=True, god_mode=True)

        self.assertEqual(game.player.hp, 1000)
        self.assertEqual(game.player.max_hp, 1000)
        self.assertEqual(game.player.gold, 1000)
        self.assertTrue(game.player.invincible)
        self.assertFalse(game.encounters_enabled)

        game.restart()

        self.assertEqual(game.player.hp, 50)
        self.assertEqual(game.player.max_hp, 50)
        self.assertEqual(game.player.gold, 100)
        self.assertFalse(game.player.invincible)
        self.assertTrue(game.encounters_enabled)


class CommandLineTests(unittest.TestCase):
    def test_cheat_flags_are_parsed(self):
        args = parse_args(["--no-encounters", "--god-mode"])

        self.assertTrue(args.no_encounters)
        self.assertTrue(args.god_mode)


if __name__ == "__main__":
    unittest.main()

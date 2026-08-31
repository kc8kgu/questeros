"""Tests for player movement, survival, and progression rules."""
import unittest

import settings as s
from game_map import GameMap
from player import FOOD_STEP_INTERVAL, STARVE_STEP_INTERVAL, Player


class PlayerMovementTests(unittest.TestCase):
    def setUp(self):
        self.game_map = GameMap(
            [["grass"] * 3 for _ in range(3)], s.BLOCKED)
        self.player = Player(1, 1)

    def test_step_animates_then_commits_arrival(self):
        self.player.try_step(1, 0, self.game_map)

        self.assertEqual(self.player.target, (2, 1))
        self.player.update(s.STEP_TIME / 2)
        self.assertEqual((self.player.x, self.player.y), (1, 1))
        self.assertAlmostEqual(self.player.fx, 1.5)

        self.player.update(s.STEP_TIME / 2)
        self.assertEqual((self.player.x, self.player.y), (2, 1))
        self.assertEqual(self.player.last_pos, (1, 1))
        self.assertTrue(self.player.just_arrived)
        self.assertEqual(self.player.steps, 1)

    def test_blocked_and_out_of_bounds_steps_are_rejected(self):
        rows = [["grass"] * 3 for _ in range(3)]
        rows[1][2] = "water"
        game_map = GameMap(rows, s.BLOCKED)
        self.player.try_step(1, 0, game_map)
        self.assertIsNone(self.player.target)
        self.assertEqual(self.player.facing, "right")

        edge_player = Player(0, 0)
        edge_player.try_step(-1, 0, game_map)
        self.assertIsNone(edge_player.target)
        self.assertEqual(edge_player.facing, "left")

    def test_movement_uses_actual_grid_dimensions_and_custom_blocking(self):
        small_map = GameMap(
            [["floor", "wall"], ["floor", "floor"]], {"wall"})
        player = Player(0, 0)

        player.try_step(1, 0, small_map)
        self.assertIsNone(player.target)
        player.try_step(0, 1, small_map)
        self.assertEqual(player.target, (0, 1))


class PlayerSurvivalTests(unittest.TestCase):
    def test_god_mode_toggle_restores_previous_stats(self):
        player = Player(0, 0)
        player.hp = 23
        player.gold = 47

        player.toggle_god_mode()

        self.assertEqual((player.hp, player.max_hp, player.gold),
                         (1000, 1000, 1000))
        self.assertTrue(player.invincible)

        player.toggle_god_mode()

        self.assertEqual((player.hp, player.max_hp, player.gold), (23, 50, 47))
        self.assertFalse(player.invincible)

    def test_food_is_consumed_at_the_step_interval(self):
        player = Player(0, 0)

        for _ in range(FOOD_STEP_INTERVAL - 1):
            player.on_arrive()
        self.assertEqual(player.food, 100)

        player.on_arrive()
        self.assertEqual(player.food, 99)
        self.assertEqual(player.steps, FOOD_STEP_INTERVAL)

    def test_starvation_damages_and_can_kill(self):
        player = Player(0, 0)
        player.food = 0
        player.hp = 1

        for _ in range(STARVE_STEP_INTERVAL - 1):
            player.on_arrive()
        self.assertEqual(player.hp, 1)

        player.on_arrive()
        self.assertEqual(player.hp, 0)
        self.assertTrue(player.dead)

    def test_invincible_player_ignores_starvation_damage(self):
        player = Player(0, 0, god_mode=True)
        player.food = 0

        for _ in range(STARVE_STEP_INTERVAL):
            player.on_arrive()

        self.assertEqual(player.hp, 1000)
        self.assertFalse(player.dead)

    def test_eating_requires_missing_hp_and_enough_food(self):
        player = Player(0, 0)

        healed, _ = player.eat_ration()
        self.assertEqual(healed, 0)
        self.assertEqual(player.food, 100)

        player.hp = 20
        player.food = s.EAT_FOOD_COST - 1
        healed, _ = player.eat_ration()
        self.assertEqual(healed, 0)
        self.assertEqual(player.hp, 20)

        player.food = s.EAT_FOOD_COST
        healed, _ = player.eat_ration()
        self.assertEqual(healed, s.EAT_HEAL)
        self.assertEqual(player.hp, 20 + s.EAT_HEAL)
        self.assertEqual(player.food, 0)


class PlayerProgressionTests(unittest.TestCase):
    def test_large_xp_award_can_gain_multiple_levels(self):
        player = Player(0, 0)
        player.hp = 1

        player.gain_xp(350)

        self.assertEqual(player.level, 3)
        self.assertEqual(player.xp, 50)
        self.assertEqual(player.max_hp, 70)
        self.assertEqual(player.hp, 70)

    def test_spending_never_allows_negative_gold(self):
        player = Player(0, 0)
        player.gold = 10

        self.assertFalse(player.spend(11))
        self.assertEqual(player.gold, 10)
        self.assertTrue(player.spend(10))
        self.assertEqual(player.gold, 0)


if __name__ == "__main__":
    unittest.main()

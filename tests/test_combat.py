"""Tests for deterministic battle resolution."""
import unittest
from unittest.mock import patch

import combat
import settings as s
from player import Player


def make_monster(**changes):
    monster = {
        "id": "test",
        "name": "Test Beast",
        "hp": 10,
        "atk": 4,
        "dfn": 1,
        "gold": 10,
        "xp": 7,
        "min_level": 1,
    }
    monster.update(changes)
    return monster


class MonsterSelectionTests(unittest.TestCase):
    def test_selection_only_receives_level_eligible_monsters(self):
        with patch("combat.random.choice", side_effect=lambda choices: choices[-1]):
            monster = combat.pick_monster(2)

        self.assertLessEqual(monster["min_level"], 2)
        self.assertEqual(monster["id"], "orc")


class BattleTests(unittest.TestCase):
    def test_actions_dispatch_to_the_matching_rule(self):
        battle = combat.Battle(Player(0, 0), make_monster())

        with patch.object(battle, "player_attack") as attack, \
                patch.object(battle, "player_eat") as eat, \
                patch.object(battle, "player_run") as run:
            battle.act(combat.ACTION_ATTACK)
            battle.act(combat.ACTION_EAT)
            battle.act(combat.ACTION_RUN)

        attack.assert_called_once_with()
        eat.assert_called_once_with()
        run.assert_called_once_with()

    def test_unknown_action_is_rejected(self):
        battle = combat.Battle(Player(0, 0), make_monster())

        with self.assertRaises(ValueError):
            battle.act("dance")

    def test_attack_is_followed_by_monster_counterattack(self):
        player = Player(0, 0)
        battle = combat.Battle(player, make_monster())

        with patch("combat.random.randint", side_effect=[0, 1]):
            battle.player_attack()

        self.assertEqual(battle.mhp, 8)
        self.assertEqual(player.hp, 46)
        self.assertFalse(battle.over)

    def test_victory_awards_gold_and_xp(self):
        player = Player(0, 0)
        battle = combat.Battle(player, make_monster(hp=1, dfn=0))

        with patch("combat.random.randint", side_effect=[0, 4]):
            battle.player_attack()

        self.assertTrue(battle.over)
        self.assertEqual(battle.result, "won")
        self.assertEqual(battle.mhp, 0)
        self.assertEqual(player.gold, 114)
        self.assertEqual(player.xp, 7)

    def test_failed_eating_does_not_cost_a_turn(self):
        player = Player(0, 0)
        battle = combat.Battle(player, make_monster())

        with patch.object(battle, "monster_attack") as monster_attack:
            battle.player_eat()

        monster_attack.assert_not_called()
        self.assertEqual(player.hp, player.max_hp)
        self.assertEqual(player.food, 100)

    def test_successful_eating_costs_food_and_a_turn(self):
        player = Player(0, 0)
        player.hp = 20
        player.food = 20
        battle = combat.Battle(player, make_monster(atk=3))

        with patch("combat.random.randint", return_value=0):
            battle.player_eat()

        self.assertEqual(player.food, 20 - s.EAT_FOOD_COST)
        self.assertEqual(player.hp, 20 + s.EAT_HEAL - 2)

    def test_run_can_succeed_or_fail(self):
        player = Player(0, 0)
        escaped = combat.Battle(player, make_monster())
        with patch("combat.random.random", return_value=combat.RUN_CHANCE - 0.01):
            escaped.player_run()
        self.assertEqual(escaped.result, "fled")

        failed = combat.Battle(player, make_monster(atk=3))
        with patch("combat.random.random", return_value=combat.RUN_CHANCE), \
                patch("combat.random.randint", return_value=0):
            failed.player_run()
        self.assertFalse(failed.over)
        self.assertEqual(player.hp, player.max_hp - 2)

    def test_monster_attack_can_kill_player(self):
        player = Player(0, 0)
        player.hp = 1
        battle = combat.Battle(player, make_monster(atk=3))

        with patch("combat.random.randint", return_value=0):
            battle.monster_attack()

        self.assertTrue(player.dead)
        self.assertEqual(player.hp, 0)
        self.assertTrue(battle.over)
        self.assertEqual(battle.result, "lost")

    def test_monster_cannot_damage_invincible_player(self):
        player = Player(0, 0, god_mode=True)
        battle = combat.Battle(player, make_monster(atk=9999))

        with patch("combat.random.randint", return_value=2):
            battle.monster_attack()

        self.assertEqual(player.hp, 1000)
        self.assertFalse(player.dead)
        self.assertFalse(battle.over)
        self.assertEqual(battle.log[-1], "The Test Beast cannot hurt you!")


if __name__ == "__main__":
    unittest.main()

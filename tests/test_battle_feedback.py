"""Tests for battle presentation timing."""
import unittest

from battle_feedback import BattleFeedback, HIT_DURATION, HitEvent


class BattleFeedbackTests(unittest.TestCase):
    def test_hit_events_validate_target_and_damage(self):
        with self.assertRaises(ValueError):
            HitEvent("floor", 2)
        with self.assertRaises(ValueError):
            HitEvent("monster", 0)

    def test_feedback_advances_through_ordered_hit_events(self):
        feedback = BattleFeedback()
        monster_hit = HitEvent("monster", 3, slash=True)
        player_hit = HitEvent("player", 2)

        feedback.start((monster_hit, player_hit))
        feedback.update(HIT_DURATION / 2)
        self.assertIs(feedback.current, monster_hit)
        self.assertAlmostEqual(feedback.progress, 0.5)

        feedback.update(HIT_DURATION / 2)
        self.assertIs(feedback.current, player_hit)
        feedback.update(HIT_DURATION)
        self.assertFalse(feedback.active)

    def test_large_update_can_finish_the_complete_sequence(self):
        feedback = BattleFeedback()
        feedback.start((HitEvent("monster", 3), HitEvent("player", 2)))

        feedback.update(HIT_DURATION * 2)

        self.assertFalse(feedback.active)
        self.assertEqual(feedback.progress, 0.0)

    def test_feedback_rejects_negative_time_and_non_events(self):
        feedback = BattleFeedback()
        with self.assertRaises(ValueError):
            feedback.update(-0.1)
        with self.assertRaises(TypeError):
            feedback.start(("hit",))


if __name__ == "__main__":
    unittest.main()

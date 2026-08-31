"""Tests for deterministic overworld and town generation."""
import unittest

import settings as s
import town
import world


class WorldGenerationTests(unittest.TestCase):
    def test_default_world_is_deterministic_and_well_formed(self):
        game_map, towns = world.generate()
        repeated_map, repeated_towns = world.generate()

        self.assertEqual(game_map, repeated_map)
        self.assertEqual(towns, repeated_towns)
        self.assertEqual(game_map.height, s.MAP_H)
        self.assertEqual(game_map.width, s.MAP_W)
        self.assertEqual(game_map.blocked, frozenset(s.BLOCKED))
        self.assertEqual(len(towns), 2)
        self.assertEqual(len(set(towns)), 2)
        self.assertTrue(
            all(game_map.tile_at(x, y) == "town" for x, y in towns))
        self.assertEqual(game_map.count("boss"), 1)

    def test_different_seed_changes_the_world(self):
        first, _ = world.generate(42)
        second, _ = world.generate(43)
        self.assertNotEqual(first, second)

    def test_start_position_is_walkable_grass(self):
        game_map, _ = world.generate()
        x, y = world.find_start(game_map)
        self.assertEqual(game_map.tile_at(x, y), "grass")


class TownGenerationTests(unittest.TestCase):
    def test_town_is_deterministic_and_has_required_triggers(self):
        game_map, state = town.generate(10, 20)
        repeated_map, repeated_state = town.generate(10, 20)

        self.assertEqual(game_map, repeated_map)
        self.assertEqual(
            [(v.service, v.counter_x, v.counter_y, v.x, v.y)
             for v in state.vendors],
            [(v.service, v.counter_x, v.counter_y, v.x, v.y)
             for v in repeated_state.vendors])
        self.assertEqual(
            [guard.route for guard in state.guards],
            [guard.route for guard in repeated_state.guards])
        self.assertEqual(game_map.height, s.TOWN_H)
        self.assertEqual(game_map.width, s.TOWN_W)
        self.assertEqual(game_map.blocked, frozenset(s.TOWN_BLOCKED))
        self.assertEqual(
            game_map.tile_at(town.GATE_X, s.TOWN_H - 1), "gate")
        for service in town.SERVICES:
            self.assertEqual(game_map.count(town.COUNTER_TILES[service]), 1)
            counter, vendor = town.STATIONS[service]
            self.assertEqual(game_map.tile_at(*counter),
                             town.COUNTER_TILES[service])
            generated = next(
                item for item in state.vendors if item.service == service)
            self.assertEqual(
                (generated.counter_x, generated.counter_y), counter)
            self.assertEqual((generated.x, generated.y), vendor)
        self.assertEqual(len(state.vendors), 5)
        self.assertGreaterEqual(len(state.guards), 3)

    def test_spawn_is_inside_town_and_walkable(self):
        game_map, _ = town.generate(10, 20)
        x, y = town.SPAWN

        self.assertTrue(0 <= x < s.TOWN_W and 0 <= y < s.TOWN_H)
        self.assertTrue(game_map.is_walkable(x, y))

    def test_counters_are_reachable_from_spawn(self):
        game_map, _ = town.generate(10, 20)
        start = town.SPAWN
        for service in town.SERVICES:
            tile = town.COUNTER_TILES[service]
            counter = next(
                (x, y)
                for y in range(s.TOWN_H)
                for x in range(s.TOWN_W)
                if game_map.tile_at(x, y) == tile
            )
            self.assertTrue(_can_reach(game_map, start, counter))


def _can_reach(game_map, start, goal):
    seen = {start}
    queue = [start]
    while queue:
        x, y = queue.pop(0)
        if (x, y) == goal:
            return True
        for dx, dy in town.CARDINAL:
            nx, ny = x + dx, y + dy
            if (nx, ny) in seen:
                continue
            if game_map.is_walkable(nx, ny):
                seen.add((nx, ny))
                queue.append((nx, ny))
    return False


if __name__ == "__main__":
    unittest.main()

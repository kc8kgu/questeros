"""Overworld exploration and arrival triggers."""
import random

import combat
from scenes.exploration import ExplorationScene


class WorldScene(ExplorationScene):
    def __init__(self, game):
        super().__init__(game, game.world_map)

    def on_arrive(self):
        player = self.game.player
        tile = self.game_map.tile_at(player.x, player.y)
        if tile == "town":
            from scenes.town import TownScene

            scene = TownScene(
                self.game, self, player.x, player.y, player.last_pos)
            self.game.change_scene(scene)
        elif tile == "boss":
            from scenes.battle import BattleScene

            self.game.change_scene(BattleScene(
                self.game, self, combat.BOSS_MONSTER, terrain=tile))
        elif self.game.encounters_enabled and tile in ("grass", "sand") and \
                random.random() < combat.ENCOUNTER_CHANCE:
            from scenes.battle import BattleScene

            monster = combat.pick_monster(player.level)
            self.game.change_scene(BattleScene(
                self.game, self, monster, terrain=tile))

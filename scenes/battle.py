"""Battle input, presentation, and scene transitions."""
import pygame

import battle_view
import combat
import settings as s
from battle_feedback import BattleFeedback, HitEvent
from scenes.base import Scene
from scenes.win import WinScene


class BattleScene(Scene):
    def __init__(self, game, return_scene, monster, terrain="grass",
                 town_target=None):
        super().__init__(game)
        self.return_scene = return_scene
        self.battle = combat.Battle(game.player, monster)
        self.terrain = terrain
        self.town_target = town_target
        self.feedback = BattleFeedback()
        self.selected = 0

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return True

        if self.feedback.active:
            return True
        if self.battle.over:
            if self.town_target and hasattr(self.return_scene, "resolve_town_battle"):
                kind, target = self.town_target
                self.return_scene.resolve_town_battle(
                    kind, target, self.battle.result)
            if self.battle.result == "won" and \
                    self.battle.monster.get("boss"):
                self.game.change_scene(WinScene(self.game))
            else:
                self.game.change_scene(self.return_scene)
        elif event.key in (pygame.K_UP, pygame.K_w):
            self.selected = (self.selected - 1) % len(combat.ACTIONS)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.selected = (self.selected + 1) % len(combat.ACTIONS)
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
            self._act(combat.ACTIONS[self.selected])
        return True

    def _act(self, action):
        battle = self.battle
        player = battle.player
        monster_hp = battle.mhp
        player_hp = player.hp
        player_food = player.food
        player_max_hp = player.max_hp

        battle.act(action)

        events = []
        monster_damage = max(0, monster_hp - battle.mhp)
        if monster_damage:
            events.append(HitEvent(
                "monster", monster_damage,
                slash=action == combat.ACTION_ATTACK))

        healed = 0
        if action == combat.ACTION_EAT and player.food < player_food:
            healed = min(s.EAT_HEAL, player_max_hp - player_hp)
        player_damage = max(0, player_hp + healed - player.hp)
        if player_damage:
            events.append(HitEvent("player", player_damage))
        self.feedback.start(events)

    def update(self, dt):
        self.feedback.update(dt)

    def draw(self):
        game = self.game
        battle_view.draw(
            game.screen, self.battle, game.cache, self.selected, self.feedback,
            self.terrain)

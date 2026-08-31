"""Startup menu for beginning or continuing a game."""
import pygame

import hud
import menus
import settings as s
from scenes.base import Scene


class TitleScene(Scene):
    show_stats = False

    def __init__(self, game):
        super().__init__(game)
        self.menu = menus.Menu("title", "Main Menu")
        self.menu.options = [
            ["New Game", True],
            ["Continue", game.save_path.is_file()],
            ["Quit", True],
        ]
        if not self.menu.options[1][1]:
            self.menu.set_status("No saved game found.", s.GREY)

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return True
        if event.key in (pygame.K_UP, pygame.K_w):
            self.menu.move(-1)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.menu.move(1)
        elif event.key in (
                pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
            return self._select()
        return True

    def _select(self):
        index = self.menu.selected
        if not self.menu.options[index][1]:
            self.menu.set_status("No saved game found.", s.GREY)
        elif index == 0:
            self.game.start_new_game(
                no_encounters=self.game.start_no_encounters,
                god_mode=self.game.start_god_mode)
        elif index == 1:
            self.game.continue_saved_game()
        else:
            return False
        return True

    def draw(self):
        screen = self.game.screen
        w, h = screen.get_size()
        screen.blit(
            pygame.transform.scale(
                self.game.cache["screen_title"], screen.get_size()),
            (0, 0),
        )
        title = hud.get_font(52).render("QUESTEROS", True, s.YELLOW)
        subtitle = hud.get_font(18).render(
            "A RETRO REALM AWAITS", True, s.LTGREEN)
        screen.blit(
            title,
            (w // 2 - title.get_width() // 2, h // 2 - s.ui(190)))
        screen.blit(
            subtitle,
            (w // 2 - subtitle.get_width() // 2, h // 2 - s.ui(126)))
        self.menu.draw(screen, self.game.cache)

"""Victory screen shown after the dragon is defeated."""
import pygame

import hud
import settings as s
import ui_view
from scenes.base import Scene


class WinScene(Scene):
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            self.game.restart()
        return True

    def draw(self):
        screen = self.game.screen
        w, h = screen.get_size()
        screen.blit(
            pygame.transform.scale(
                self.game.cache["screen_win"], screen.get_size()),
            (0, 0),
        )

        box_w, box_h = s.ui(700), s.ui(300)
        x, y = (w - box_w) // 2, (h - box_h) // 2
        ui_view.draw_panel(
            screen, (x, y, box_w, box_h), self.game.cache)

        title = hud.get_font(52).render("VICTORY", True, s.YELLOW)
        message = hud.get_font(24).render(
            "The Dragon is defeated!", True, s.WHITE)
        ending = hud.get_font(20).render(
            "Peace returns to the realm.", True, s.LTGREEN)
        hint = hud.get_font(18).render(
            "R restart    Q quit", True, s.GREY)

        lines = (
            (title, y + s.ui(42)),
            (message, y + s.ui(126)),
            (ending, y + s.ui(168)),
            (hint, y + s.ui(236)),
        )
        for text, line_y in lines:
            screen.blit(text, (w // 2 - text.get_width() // 2, line_y))

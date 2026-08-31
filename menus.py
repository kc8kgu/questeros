"""Keyboard-driven retro menus drawn as bordered text boxes."""
import pygame

import hud
import settings as s
import ui_view
from graphics.ui import CURSOR

ROW_H = s.ui(26)


class Menu:
    def __init__(self, kind, title):
        self.kind = kind        # key the game uses to route selections
        self.title = title
        self.options = []       # list of [label, enabled]
        self.selected = 0
        self.status = ""
        self.status_color = s.GREY
        self.entries = []       # per-option payload, set by the game
        self.icons = []         # optional cache key for each option

    def move(self, d):
        self.selected = (self.selected + d) % len(self.options)

    def set_status(self, text, color=None):
        self.status = text
        self.status_color = color or s.GREY

    def draw(self, screen, cache=None):
        w, h = screen.get_size()
        box_w = s.ui(600)
        box_h = s.ui(60) + ROW_H * len(self.options) + s.ui(40)
        x = (w - box_w) // 2
        if self.kind == "title":
            y = (h - box_h) // 2
        else:
            y = max(s.ui(20), h - box_h - s.ui(52))
        if cache:
            ui_view.draw_panel(screen, (x, y, box_w, box_h), cache)
        else:
            pygame.draw.rect(screen, s.BLACK, (x, y, box_w, box_h))
            pygame.draw.rect(
                screen, s.GREY, (x, y, box_w, box_h), s.ui(2))

        title = hud.get_font(22).render(self.title, True, s.YELLOW)
        screen.blit(
            title, (x + (box_w - title.get_width()) // 2, y + s.ui(14)))

        font = hud.get_font(18)
        for i, (label, enabled) in enumerate(self.options):
            ry = y + s.ui(56) + i * ROW_H
            screen.blit(font.render(label, True, s.WHITE if enabled else s.DKGREY),
                        (x + s.ui(68), ry))
            icon = self.icons[i] if i < len(self.icons) else None
            if cache and icon:
                ui_view.draw_icon(
                    screen, cache, icon, (x + s.ui(44), ry + s.ui(1)))
            if i == self.selected:
                if cache:
                    ui_view.draw_icon(
                        screen, cache, CURSOR,
                        (x + s.ui(20), ry + s.ui(1)))
                else:
                    screen.blit(
                        font.render(">", True, s.YELLOW),
                        (x + s.ui(24), ry))

        stat = hud.get_font(16).render(self.status, True, self.status_color)
        screen.blit(stat, (x + s.ui(24), y + box_h - s.ui(30)))

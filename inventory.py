"""Inventory & stats screen: view stats, equip owned gear, eat rations."""
import items
import pygame

import hud
import palette
import settings as s
import ui_view
from graphics.ui import (
    CURSOR, ICON_ARMOR, ICON_FOOD, ICON_GOLD, ICON_HP, ICON_WEAPON, ICON_XP,
)


class Inventory:
    def __init__(self, player):
        self.player = player
        self.rows = []      # (kind, payload): header / blank / weapon / armor / eat
        self.sel = 0        # index into the selectable rows
        self.status = ""
        self.status_color = s.GREY
        self.rebuild()

    def rebuild(self):
        p = self.player
        self.rows = [("header", "WEAPONS")]
        self.rows += [("weapon", i) for i in sorted(p.weapons_owned)]
        self.rows.append(("header", "ARMOR"))
        self.rows += [("armor", i) for i in sorted(p.armors_owned)]
        self.rows.append(("blank", None))
        self.rows.append(("eat", None))
        self.selectable = [k for k, (kind, _) in enumerate(self.rows)
                           if kind in ("weapon", "armor", "eat")]
        self.sel = min(self.sel, len(self.selectable) - 1)

    def move(self, d):
        self.sel = (self.sel + d) % len(self.selectable)

    def confirm(self):
        kind, idx = self.rows[self.selectable[self.sel]]
        p = self.player
        if kind == "eat":
            healed, msg = p.eat_ration()
            self.set_status(msg, s.LTGREEN if healed else s.GREY)
            return
        table, attr = (items.WEAPONS, "weapon") if kind == "weapon" \
            else (items.ARMORS, "armor")
        if getattr(p, attr) == idx:
            self.set_status("Already equipped.", s.GREY)
            return
        setattr(p, attr, idx)
        self.set_status(f"Equipped {table[idx][0]}.", s.LTGREEN)

    def set_status(self, text, color):
        self.status = text
        self.status_color = color

    def _label(self, kind, idx):
        p = self.player
        if kind == "weapon":
            name, _, bonus = items.WEAPONS[idx]
            tag = "  [E]" if p.weapon == idx else ""
            return f"{name}  ATK+{bonus}{tag}"
        if kind == "armor":
            name, _, bonus = items.ARMORS[idx]
            tag = "  [E]" if p.armor == idx else ""
            return f"{name}  DEF+{bonus}{tag}"
        return f"Eat Ration  (-{s.EAT_FOOD_COST} food, +{s.EAT_HEAL} HP)"

    def draw(self, screen, cache=None):
        w, h = screen.get_size()
        dim = pygame.Surface((w, h), pygame.SRCALPHA)
        dim.fill(palette.OVERLAY_DIM)
        screen.blit(dim, (0, 0))

        box_w, box_h = s.ui(820), s.ui(540)
        x, y = (w - box_w) // 2, (h - box_h) // 2
        if cache:
            ui_view.draw_panel(screen, (x, y, box_w, box_h), cache)
        else:
            pygame.draw.rect(screen, s.BLACK, (x, y, box_w, box_h))
            pygame.draw.rect(
                screen, s.GREY, (x, y, box_w, box_h), s.ui(2))

        title = hud.get_font(22).render("INVENTORY", True, s.YELLOW)
        screen.blit(
            title, (x + (box_w - title.get_width()) // 2, y + s.ui(16)))

        p = self.player
        stats = [
            (ICON_HP, "HP", f"{p.hp}/{p.max_hp}", s.LTRED),
            (ICON_GOLD, "GOLD", str(p.gold), s.YELLOW),
            (ICON_FOOD, "FOOD", str(p.food), s.ORANGE),
            (ICON_XP, "LEVEL", str(p.level), s.WHITE),
            (ICON_XP, "XP", f"{p.xp}/{p.xp_needed()}", s.LTBLUE),
            (ICON_WEAPON, "ATTACK", str(p.attack()), s.CYAN),
            (ICON_ARMOR, "DEFENSE", str(p.defense()), s.CYAN),
            (None, "STEPS", str(p.steps), s.GREY),
        ]
        font = hud.get_font(18)
        for i, (icon, label, value, color) in enumerate(stats):
            ry = y + s.ui(70) + i * s.ui(28)
            if cache and icon:
                ui_view.draw_icon(
                    screen, cache, icon, (x + s.ui(28), ry + s.ui(1)))
            screen.blit(
                font.render(label, True, s.GREY), (x + s.ui(50), ry))
            screen.blit(
                font.render(value, True, color), (x + s.ui(160), ry))
        pygame.draw.line(
            screen, s.DKGREY,
            (x + s.ui(290), y + s.ui(60)),
            (x + s.ui(290), y + box_h - s.ui(60)))

        sel_row = self.selectable[self.sel]
        for k, (kind, payload) in enumerate(self.rows):
            ry = y + s.ui(64) + k * s.ui(26)
            if kind == "blank":
                continue
            if kind == "header":
                screen.blit(
                    font.render(payload, True, s.YELLOW),
                    (x + s.ui(340), ry))
                continue
            selected = k == sel_row
            icon = {
                "weapon": ICON_WEAPON,
                "armor": ICON_ARMOR,
                "eat": ICON_FOOD,
            }[kind]
            if cache:
                ui_view.draw_icon(
                    screen, cache, icon,
                    (x + s.ui(364), ry + s.ui(1)))
            screen.blit(font.render(self._label(kind, payload), True,
                                    s.LTGREEN if selected else s.WHITE),
                        (x + s.ui(388), ry))
            if selected:
                if cache:
                    ui_view.draw_icon(
                        screen, cache, CURSOR,
                        (x + s.ui(340), ry + s.ui(1)))
                else:
                    screen.blit(
                        font.render(">", True, s.YELLOW),
                        (x + s.ui(340), ry))

        stat = hud.get_font(16).render(self.status, True, self.status_color)
        screen.blit(
            stat,
            (x + (box_w - stat.get_width()) // 2,
             y + box_h - s.ui(64)))
        hint = hud.get_font(16).render(
            "Up/Down select   Enter equip/eat   Esc close", True, s.GREY)
        screen.blit(
            hint,
            (x + (box_w - hint.get_width()) // 2,
             y + box_h - s.ui(40)))

"""Status bar and fullscreen overlays, drawn at window resolution."""
import pygame

import palette as p
import settings as s
import ui_view
from graphics.assets import font_path
from graphics.ui import (
    ICON_FOOD, ICON_GOLD, ICON_HP, ICON_XP, PANEL_ALT,
)

BAR_H = s.ui(34)
_fonts = {}


def reset_fonts():
    """Discard fonts invalidated by a pygame shutdown and reinitialization."""
    _fonts.clear()


def get_font(size, bold=True, scaled=True):
    actual_size = s.ui(size) if scaled else size
    key = (actual_size, bold)
    if key not in _fonts:
        _fonts[key] = pygame.font.Font(str(font_path(bold)), actual_size)
    return _fonts[key]


def _segments(player):
    return [
        (ICON_HP, "HP", f"{player.hp}/{player.max_hp}", s.LTRED),
        (ICON_GOLD, "GOLD", str(player.gold), s.YELLOW),
        (ICON_FOOD, "FOOD", str(player.food),
         s.ORANGE if player.food else s.RED),
        (ICON_XP, "LVL", str(player.level), s.WHITE),
        (ICON_XP, "XP", f"{player.xp}/{player.xp_needed()}", s.LTBLUE),
    ]


def draw_stats_bar(screen, player, cache=None, encounters_enabled=True):
    w, h = screen.get_size()
    if cache:
        ui_view.draw_panel(
            screen, (0, h - BAR_H, w, BAR_H), cache, PANEL_ALT)
    else:
        pygame.draw.rect(screen, s.BLACK, (0, h - BAR_H, w, BAR_H))
        pygame.draw.line(screen, s.GREY, (0, h - BAR_H), (w, h - BAR_H))

    font = get_font(18)
    mid = h - BAR_H // 2
    x = s.ui(14)
    for icon, label, value, color in _segments(player):
        if cache:
            ui_view.draw_icon(screen, cache, icon, (x, mid - s.ui(8)))
            x += s.ui(20)
        lab = font.render(label, True, s.GREY)
        val = font.render(value, True, color)
        screen.blit(lab, (x, mid - lab.get_height() // 2))
        x += lab.get_width() + s.ui(6)
        screen.blit(val, (x, mid - val.get_height() // 2))
        x += val.get_width() + s.ui(28)

    indicator_font = get_font(14)
    indicators = [
        ("GOD ON" if player.invincible else "GOD OFF",
         s.YELLOW if player.invincible else s.GREY),
        ("ENC ON" if encounters_enabled else "ENC OFF",
         s.LTGREEN if encounters_enabled else s.LTRED),
    ]
    indicator_x = w - s.ui(14)
    for text, color in reversed(indicators):
        rendered = indicator_font.render(text, True, color)
        indicator_x -= rendered.get_width()
        screen.blit(rendered, (
            indicator_x, mid - rendered.get_height() // 2))
        indicator_x -= s.ui(18)

    if player.food < 15 and (pygame.time.get_ticks() // 400) % 2 == 0:
        warn = font.render("HUNGRY!", True, s.RED)
        screen.blit(warn, (
            indicator_x - warn.get_width() - s.ui(4),
            mid - warn.get_height() // 2,
        ))


def draw_death(screen, can_continue=False, cache=None):
    w, h = screen.get_size()
    if cache:
        background = pygame.transform.scale(cache["screen_death"], (w, h))
        screen.blit(background, (0, 0))
    else:
        screen.fill(s.BLACK)
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    overlay.fill(p.OVERLAY_DEATH)
    screen.blit(overlay, (0, 0))
    t1 = get_font(52).render("YOU HAVE DIED", True, s.RED)
    t2 = get_font(20).render("R  restart", True, s.GREY)
    continue_color = s.GREY if can_continue else s.DKGREY
    t3 = get_font(20).render(
        "C  continue from last save", True, continue_color)
    screen.blit(t1, (w // 2 - t1.get_width() // 2, h // 2 - s.ui(70)))
    screen.blit(t2, (w // 2 - t2.get_width() // 2, h // 2 + s.ui(10)))
    screen.blit(t3, (w // 2 - t3.get_width() // 2, h // 2 + s.ui(48)))


def draw_notice(screen, message, color, cache=None):
    text = get_font(18).render(message, True, color)
    box_w, box_h = text.get_width() + s.ui(48), s.ui(52)
    x, y = (screen.get_width() - box_w) // 2, s.ui(20)
    if cache:
        ui_view.draw_panel(screen, (x, y, box_w, box_h), cache)
    else:
        pygame.draw.rect(screen, s.BLACK, (x, y, box_w, box_h))
        pygame.draw.rect(screen, s.GREY, (x, y, box_w, box_h), s.ui(2))
    screen.blit(text, (
        x + (box_w - text.get_width()) // 2,
        y + (box_h - text.get_height()) // 2,
    ))


def draw_quit_confirm(screen, cache=None):
    w, h = screen.get_size()
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    overlay.fill(p.OVERLAY_DIM)
    screen.blit(overlay, (0, 0))

    box_w, box_h = s.ui(460), s.ui(160)
    x, y = (w - box_w) // 2, (h - box_h) // 2
    if cache:
        ui_view.draw_panel(screen, (x, y, box_w, box_h), cache)
    else:
        pygame.draw.rect(screen, s.BLACK, (x, y, box_w, box_h))
        pygame.draw.rect(screen, s.GREY, (x, y, box_w, box_h), s.ui(2))

    title = get_font(26).render("QUIT GAME?", True, s.YELLOW)
    prompt = get_font(18).render(
        "Unsaved progress will be lost.", True, s.WHITE)
    hint = get_font(16).render(
        "Y / Enter confirm    N / Esc cancel", True, s.GREY)
    screen.blit(title, (x + (box_w - title.get_width()) // 2, y + s.ui(24)))
    screen.blit(prompt, (x + (box_w - prompt.get_width()) // 2, y + s.ui(68)))
    screen.blit(hint, (x + (box_w - hint.get_width()) // 2, y + s.ui(112)))

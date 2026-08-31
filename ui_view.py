"""Reusable rendering helpers for image-backed interface panels and bars."""
import pygame

import settings as s
from graphics.assets import PANEL_ALT_SLICES, PANEL_SLICES
from graphics.ui import PANEL, UI_BAR_FILL, UI_BAR_FRAME, UI_DIVIDER


def draw_panel(screen, rect, cache, texture=PANEL):
    """Draw a cached nine-slice panel at screen resolution."""
    area = pygame.Rect(rect)
    slices = PANEL_ALT_SLICES if texture == "ui_panel_alt" else PANEL_SLICES
    size = min(s.ui(16), area.width // 2, area.height // 2)
    left, top = area.left, area.top
    right, bottom = area.right, area.bottom
    positions = (
        (left, top, size, size), (left + size, top, right - left - 2 * size, size),
        (right - size, top, size, size),
        (left, top + size, size, bottom - top - 2 * size),
        (left + size, top + size, right - left - 2 * size, bottom - top - 2 * size),
        (right - size, top + size, size, bottom - top - 2 * size),
        (left, bottom - size, size, size),
        (left + size, bottom - size, right - left - 2 * size, size),
        (right - size, bottom - size, size, size),
    )
    for key, destination in zip(slices, positions):
        if destination[2] <= 0 or destination[3] <= 0:
            continue
        art = pygame.transform.scale(cache[key], destination[2:])
        screen.blit(art, destination[:2])


def draw_icon(screen, cache, key, position):
    """Blit one native-size cached interface icon when a key is present."""
    if key:
        icon = cache[key]
        size = tuple(s.ui(dimension) for dimension in icon.get_size())
        screen.blit(pygame.transform.scale(icon, size), position)


def draw_bar(screen, rect, fraction, cache):
    """Draw a framed health/status bar using atlas textures."""
    area = pygame.Rect(rect)
    fraction = max(0.0, min(1.0, fraction))
    frame = pygame.transform.scale(cache[UI_BAR_FRAME], area.size)
    screen.blit(frame, area.topleft)
    inset = max(1, s.ui(2))
    fill_width = max(0, int((area.width - inset * 2) * fraction))
    if fill_width:
        fill = pygame.transform.scale(
            cache[UI_BAR_FILL], (fill_width, max(1, area.height - inset * 2)))
        screen.blit(fill, (area.left + inset, area.top + inset))


def draw_divider(screen, rect, cache):
    """Draw a small image-backed divider."""
    area = pygame.Rect(rect)
    screen.blit(pygame.transform.scale(cache[UI_DIVIDER], area.size), area.topleft)

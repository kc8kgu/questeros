"""Rendering for the turn-based battle screen."""
import pygame

import combat
import hud
import palette as p
import settings as s
import ui_view
from graphics.battle_actors import BATTLE_PLAYER_KEY, battle_monster_key
from graphics.battle_backdrops import (
    BATTLE_BACKDROP_SIZE, battle_backdrop_key,
)
from graphics.ui import (
    ICON_FOOD, ICON_HP, ICON_LEAVE, ICON_WEAPON, PANEL, PANEL_ALT,
)

FLASH_START = 0.10
FLASH_END = 0.54
SLASH_END = 0.48
DAMAGE_START = 0.10
SHAKE_START = 0.08
SHAKE_END = 0.58
RECOIL_START = 0.08
RECOIL_PEAK = 0.30
RECOIL_END = 0.72

RECOIL_DISTANCE = {
    "monster": (14, -5),
    "player": (-10, 4),
}

MONSTER_POS = (594, 208)
MONSTER_SIZE = (250, 196)
PLAYER_POS = (112, 218)
PLAYER_SIZE = (188, 202)
BATTLE_RENDER_SIZE = (960, 624)
BACKDROP_DRAW_SIZE = (960, 432)

ACTION_LABELS = {
    combat.ACTION_ATTACK: "Attack",
    combat.ACTION_EAT: "Eat Ration",
    combat.ACTION_RUN: "Run",
}


def draw(screen, battle, cache, selected, feedback=None, terrain="grass"):
    canvas = pygame.Surface(BATTLE_RENDER_SIZE)
    _draw_scene(canvas, battle, cache, selected, feedback, terrain)
    shaken = pygame.Surface(BATTLE_RENDER_SIZE)
    shaken.fill(s.BLACK)
    shaken.blit(canvas, shake_offset(feedback))
    screen.fill(s.BLACK)
    scale = min(
        screen.get_width() / BATTLE_RENDER_SIZE[0],
        screen.get_height() / BATTLE_RENDER_SIZE[1],
    )
    draw_size = tuple(round(dimension * scale)
                      for dimension in BATTLE_RENDER_SIZE)
    frame = pygame.transform.scale(shaken, draw_size)
    screen.blit(frame, (
        (screen.get_width() - draw_size[0]) // 2,
        (screen.get_height() - draw_size[1]) // 2,
    ))


def _draw_scene(screen, battle, cache, selected, feedback, terrain):
    w, h = screen.get_size()
    offset = (0, 0)
    offset_x, offset_y = offset
    screen.fill(s.BLACK)
    backdrop = pygame.transform.scale(
        cache[battle_backdrop_key(terrain)], BACKDROP_DRAW_SIZE)
    screen.blit(backdrop, offset)
    ui_view.draw_panel(screen, (0, 430 + offset_y, w, h - 430), cache, PANEL_ALT)
    ui_view.draw_divider(screen, (0, 430 + offset_y, w, 3), cache)

    monster = battle.monster
    monster_art = cache[battle_monster_key(monster["id"])]
    _draw_combatant(
        screen, monster_art,
        _offset_position(
            _offset_position(MONSTER_POS, offset),
            recoil_offset(feedback, "monster")),
        MONSTER_SIZE,
        _target_flashes(feedback, "monster"))

    name = hud.get_font(22, scaled=False).render(
        monster["name"], True, s.YELLOW)
    name_x = MONSTER_POS[0] + (MONSTER_SIZE[0] - name.get_width()) // 2
    screen.blit(name, (name_x + offset_x, 78 + offset_y))
    frac = battle.mhp / monster["hp"]
    ui_view.draw_bar(
        screen, (MONSTER_POS[0] + 18 + offset_x, 112 + offset_y,
                 MONSTER_SIZE[0] - 36, 16), frac, cache)

    player = battle.player
    _draw_combatant(
        screen, cache[BATTLE_PLAYER_KEY],
        _offset_position(
            _offset_position(PLAYER_POS, offset),
            recoil_offset(feedback, "player")),
        PLAYER_SIZE,
        _target_flashes(feedback, "player"))

    _draw_hit_effects(screen, feedback, cache, offset)

    _draw_player_panel(screen, player, cache, offset)
    _draw_log_panel(screen, battle, cache, offset)

    if battle.over:
        hint = hud.get_font(18, scaled=False).render(
            "press any key", True, s.GREY)
        screen.blit(
            hint, (620 - hint.get_width() // 2 + offset_x, 565 + offset_y))
        return
    _draw_actions(screen, cache, selected, offset)


def _draw_player_panel(screen, player, cache, offset):
    offset_x, offset_y = offset
    area = pygame.Rect(14 + offset_x, 444 + offset_y, 286, 164)
    ui_view.draw_panel(screen, area, cache, PANEL)
    ui_view.draw_icon(screen, cache, ICON_HP, (34 + offset_x, 464 + offset_y))
    title = hud.get_font(20, scaled=False).render("YOU", True, s.YELLOW)
    screen.blit(title, (58 + offset_x, 463 + offset_y))

    hp = hud.get_font(16, scaled=False).render(
        f"HP {player.hp}/{player.max_hp}", True, s.LTRED)
    screen.blit(hp, (34 + offset_x, 493 + offset_y))
    ui_view.draw_bar(
        screen, (34 + offset_x, 518 + offset_y, 242, 14),
        player.hp / player.max_hp, cache)

    detail_font = hud.get_font(14, scaled=False)
    attack = detail_font.render(
        f"ATK {player.attack()}   DEF {player.defense()}", True, s.WHITE)
    supplies = detail_font.render(
        f"FOOD {player.food}   GOLD {player.gold}", True, s.GREY)
    screen.blit(attack, (34 + offset_x, 548 + offset_y))
    screen.blit(supplies, (34 + offset_x, 574 + offset_y))


def _draw_log_panel(screen, battle, cache, offset):
    offset_x, offset_y = offset
    area = pygame.Rect(312 + offset_x, 444 + offset_y, 634, 82)
    ui_view.draw_panel(screen, area, cache, PANEL_ALT)
    font = hud.get_font(15, scaled=False)
    lines = battle.log[-2:]
    for index, line in enumerate(lines):
        color = s.WHITE if index == len(lines) - 1 else s.GREY
        text = font.render(line, True, color)
        screen.blit(text, (334 + offset_x, 463 + offset_y + index * 25))


def _draw_actions(screen, cache, selected, offset):
    offset_x, offset_y = offset
    icons = (ICON_WEAPON, ICON_FOOD, ICON_LEAVE)
    action_font = hud.get_font(14, scaled=False)
    for index, action in enumerate(combat.ACTIONS):
        area = pygame.Rect(
            312 + offset_x + index * 212,
            536 + offset_y,
            206,
            72,
        )
        ui_view.draw_panel(
            screen, area, cache, PANEL if index == selected else PANEL_ALT)
        ui_view.draw_icon(
            screen, cache, icons[index],
            (area.left + 18, area.top + 25))
        label = ACTION_LABELS[action].upper()
        text = action_font.render(
            label, True, s.YELLOW if index == selected else s.GREY)
        screen.blit(text, (
            area.left + 48,
            area.top + (area.height - text.get_height()) // 2,
        ))


def _draw_combatant(screen, source, position, size, flashes):
    bounds = source.get_bounding_rect(min_alpha=1)
    visible = source.subsurface(bounds) if bounds.width and bounds.height else source
    art = pygame.transform.scale(visible, size)
    if flashes:
        art.fill(p.WHITE_WARM, special_flags=pygame.BLEND_RGB_MAX)
    screen.blit(art, position)


def _target_flashes(feedback, target):
    if not feedback or not feedback.active:
        return False
    event = feedback.current
    return event.target == target \
        and FLASH_START <= feedback.progress <= FLASH_END


def _offset_position(position, offset):
    return position[0] + offset[0], position[1] + offset[1]


def recoil_offset(feedback, target):
    """Return a short knockback-and-return offset for the struck combatant."""
    if target not in RECOIL_DISTANCE:
        raise ValueError(f"Unknown recoil target: {target!r}")
    if not feedback or not feedback.active or feedback.current.target != target:
        return 0, 0

    progress = feedback.progress
    if not RECOIL_START <= progress <= RECOIL_END:
        return 0, 0
    if progress <= RECOIL_PEAK:
        amount = (progress - RECOIL_START) / (RECOIL_PEAK - RECOIL_START)
    else:
        amount = (RECOIL_END - progress) / (RECOIL_END - RECOIL_PEAK)

    dx, dy = RECOIL_DISTANCE[target]
    return round(dx * amount), round(dy * amount)


def _draw_hit_effects(screen, feedback, cache, offset=(0, 0)):
    if not feedback or not feedback.active:
        return
    event = feedback.current
    progress = feedback.progress
    if event.slash and progress <= SLASH_END:
        _draw_slash(screen, progress / SLASH_END, cache, offset)
    if progress >= DAMAGE_START:
        _draw_damage_number(screen, event, progress, offset)


def _draw_slash(screen, progress, cache, offset=(0, 0)):
    frame = min(5, max(0, int(progress * 6)))
    art = pygame.transform.scale(cache[f"battle_slash_{frame}"], (240, 120))
    screen.blit(art, (582 + offset[0], 236 + offset[1]))


def _draw_damage_number(screen, event, progress, offset=(0, 0)):
    local = (progress - DAMAGE_START) / (1.0 - DAMAGE_START)
    anchor = (716, 228) if event.target == "monster" else (206, 248)
    anchor = _offset_position(anchor, offset)
    text = hud.get_font(28, scaled=False).render(
        f"-{event.damage}", True, p.PALE_YELLOW)
    text.set_alpha(max(0, int(255 * (1.0 - local))))
    x = anchor[0] - text.get_width() // 2
    y = anchor[1] - int(30 * local)
    shadow = hud.get_font(28, scaled=False).render(
        f"-{event.damage}", True, p.INK)
    shadow.set_alpha(text.get_alpha())
    screen.blit(shadow, (x + 3, y + 3))
    screen.blit(text, (x, y))


def shake_offset(feedback):
    """Return a deterministic, quickly decaying battle-screen shake."""
    if not feedback or not feedback.active:
        return 0, 0
    progress = feedback.progress
    if not SHAKE_START <= progress <= SHAKE_END:
        return 0, 0
    offsets = ((-4, 2), (4, -2), (-3, -1), (3, 1), (-2, 0), (2, 0))
    return offsets[int(progress * 30) % len(offsets)]

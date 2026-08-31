"""Validated, module-relative sprite-sheet loading for Questeros."""
from pathlib import Path

import pygame


ASSET_ROOT = Path(__file__).resolve().parent.parent / "assets"
FONT_ROOT = ASSET_ROOT / "fonts"

SHEET_SPECS = {
    "overworld": ("tiles/overworld.png", (8, 6), (64, 64), False),
    "town": ("tiles/town.png", (5, 5), (64, 64), False),

    "overworld_props": (
        "tiles/overworld-props.png", (3, 2), (256, 256), True),
    "town_props": ("tiles/town-props.png", (5, 1), (256, 192), True),
    "exploration": ("sprites/exploration.png", (4, 3), (64, 64), True),
    "battle": ("sprites/battle.png", (3, 3), (64, 64), True),
    "battle_backdrops": (
        "scenes/battle-backdrops.png", (2, 2), (320, 144), False),
    "town_scene": ("scenes/town.png", (1, 1), (320, 208), False),
    "screens": ("scenes/screens.png", (3, 1), (320, 208), False),
    "ui": ("ui/ui.png", (8, 5), (16, 16), True),
    "effects_battle": ("effects/battle.png", (6, 1), (160, 80), True),
}

GRASS_KEYS = ("grass", "grass:v1", "grass:v2", "grass:v3")
SAND_KEYS = ("sand", "sand:v1", "sand:v2", "sand:v3")

OVERWORLD_MAP = {
    **{key: (index % 8, index // 8) for index, key in enumerate(GRASS_KEYS)},
    **{key: ((index + 4) % 8, (index + 4) // 8)
       for index, key in enumerate(SAND_KEYS)},
    **{f"water:m{mask:02x}": ((8 + mask) % 8, (8 + mask) // 8)
       for mask in range(16)},
    **{f"tree:m{mask:02x}": ((24 + mask % 8) % 8, (24 + mask % 8) // 8)
       for mask in range(16)},
    **{f"mountain:m{mask:02x}": ((32 + mask % 8) % 8, (32 + mask % 8) // 8)
       for mask in range(16)},
    "town": (0, 5),
    "boss": (1, 5),
    "bush": (2, 5),
    "crate": (3, 5),
    "water": (0, 1),
    "tree": (0, 3),
    "mountain": (0, 4),
}

TOWN_MAP = {
    **{f"twall:m{mask:02x}": (mask % 5, mask // 5)
       for mask in range(16)},
    # The source sheet's fourth row starts with its plain plaza entrance.
    # The previous migration was offset by one cell here, so tfloor stamped
    # the weapon counter across every walkable town tile.
    "twall:m0f": (2, 2),
    "tfloor": (1, 4),
    "gate": (0, 3),
    "counter_weapon": (1, 3),
    "counter_armor": (2, 3),
    "counter_food": (0, 4),
    "counter_inn": (3, 3),
    "counter_casino": (4, 3),
    "twall": (0, 0),
}


OVERWORLD_PROP_MAP = {
    "prop_forest": (0, 0),
    "prop_mountains": (1, 0),
    "prop_town": (2, 0),
    "prop_boss": (0, 1),
    "prop_bridge": (1, 1),
    "prop_wilds": (2, 1),
}

TOWN_PROP_MAP = {
    "town_prop_weapon": (0, 0),
    "town_prop_armor": (1, 0),
    "town_prop_food": (2, 0),
    "town_prop_inn": (3, 0),
    "town_prop_casino": (4, 0),
}

EXPLORATION_MAP = {
    "player": (0, 0),
    "player:up": (1, 0),
    "player:down": (2, 0),
    "player:left": (3, 0),
    "player:right": (1, 0),
    "vendor": (0, 1),
    "vendor:alt": (1, 1),
    "vendor:food": (2, 1),
    "vendor:inn": (3, 1),
    "guard": (0, 2),
    "guard:alt": (1, 2),
    "guard:back": (2, 2),
    "guard:side": (3, 2),
}

BATTLE_MAP = {
    "battle_player": (0, 0),
    "battle_mon_rat": (1, 0),
    "battle_mon_bat": (2, 0),
    "battle_mon_goblin": (0, 1),
    "battle_mon_skeleton": (1, 1),
    "battle_mon_orc": (2, 1),
    "battle_mon_ogre": (0, 2),
    "battle_mon_troll": (1, 2),
    "battle_mon_dragon": (2, 2),
}

MONSTER_MAP = {
    "mon_rat": (1, 0), "mon_bat": (2, 0),
    "mon_goblin": (0, 1), "mon_skeleton": (1, 1),
    "mon_orc": (2, 1), "mon_ogre": (0, 2),
    "mon_troll": (1, 2), "mon_dragon": (2, 2),
}

BATTLE_BACKDROP_MAP = {
    "battle_backdrop_grass": (0, 0),
    "battle_backdrop_sand": (1, 0),
    "battle_backdrop_boss": (0, 1),
    "battle_backdrop_tfloor": (1, 1),
}

SCREEN_MAP = {
    "screen_title": (0, 0),
    "screen_win": (1, 0),
    "screen_death": (2, 0),
}

TOWN_SCENE_MAP = {"town_background": (0, 0)}

PANEL_SLICES = (
    "ui_panel_tl", "ui_panel_t", "ui_panel_tr",
    "ui_panel_l", "ui_panel_c", "ui_panel_r",
    "ui_panel_bl", "ui_panel_b", "ui_panel_br",
)
PANEL_ALT_SLICES = tuple(key.replace("ui_panel", "ui_panel_alt")
                         for key in PANEL_SLICES)

UI_MAP = {
    **{key: (column, row)
       for key, column, row in zip(
           PANEL_SLICES,
           (0, 1, 2, 0, 1, 2, 0, 1, 2),
           (0, 0, 0, 1, 1, 1, 2, 2, 2))},
    **{key: (column, row)
       for key, column, row in zip(
           PANEL_ALT_SLICES,
           (3, 4, 5, 3, 4, 5, 3, 4, 5),
           (0, 0, 0, 1, 1, 1, 2, 2, 2))},
    "ui_panel": (1, 1),
    "ui_panel_alt": (4, 1),
    "ui_cursor": (1, 4),
    "icon_hp": (0, 3),
    "icon_gold": (1, 3),
    "icon_food": (2, 3),
    "icon_xp": (3, 3),
    "icon_weapon": (4, 3),
    "icon_armor": (5, 3),
    "icon_rest": (6, 3),
    "icon_leave": (7, 3),
    "icon_casino": (0, 4),
    "ui_bar_frame": (2, 4),
    "ui_bar_fill": (3, 4),
    "ui_divider": (4, 4),
    "ui_selection": (5, 4),
    "ui_status": (6, 4),
    "ui_ornament": (7, 4),
}

EFFECT_MAP = {
    f"battle_slash_{index}": (index, 0)
    for index in range(6)
}


class AssetError(RuntimeError):
    """Raised when a required visual asset is missing or malformed."""


def font_path(bold=False):
    name = "Silkscreen-Bold.ttf" if bold else "Silkscreen-Regular.ttf"
    return FONT_ROOT / name


def _load_sheet(name):
    relative, grid, cell_size, alpha = SHEET_SPECS[name]
    path = ASSET_ROOT / relative
    if not path.is_file():
        raise AssetError(f"Missing required visual sheet: {path}")
    try:
        sheet = pygame.image.load(str(path))
    except pygame.error as exc:
        raise AssetError(f"Could not load visual sheet {path}: {exc}") from exc
    expected = (grid[0] * cell_size[0], grid[1] * cell_size[1])
    if sheet.get_size() != expected:
        raise AssetError(
            f"Malformed visual sheet {path}: expected {expected}, "
            f"got {sheet.get_size()}")
    has_alpha = bool(sheet.get_flags() & pygame.SRCALPHA)
    if has_alpha != alpha:
        expected_kind = "RGBA" if alpha else "opaque"
        raise AssetError(
            f"Malformed visual sheet {path}: expected {expected_kind} pixels")
    return sheet


def _slice(sheet, grid, cell_size, column, row):
    rect = pygame.Rect(
        column * cell_size[0], row * cell_size[1], *cell_size)
    return sheet.subsurface(rect).copy()


def _mapped(sheet, name, mapping):
    _, grid, cell_size, _ = SHEET_SPECS[name]
    return {
        key: _slice(sheet, grid, cell_size, column, row)
        for key, (column, row) in mapping.items()
    }


def _validate_fonts():
    for bold in (False, True):
        path = font_path(bold)
        if not path.is_file():
            raise AssetError(f"Missing required font: {path}")
        try:
            pygame.font.Font(str(path), 8)
        except pygame.error as exc:
            raise AssetError(f"Malformed font {path}: {exc}") from exc


def build_cache():
    """Load every required sheet once and return the complete visual cache."""
    _validate_fonts()
    sheets = {name: _load_sheet(name) for name in SHEET_SPECS}
    cache = {}
    cache.update(_mapped(sheets["overworld"], "overworld", OVERWORLD_MAP))
    cache.update(_mapped(sheets["town"], "town", TOWN_MAP))

    cache.update(_mapped(
        sheets["overworld_props"], "overworld_props", OVERWORLD_PROP_MAP))
    cache.update(_mapped(sheets["town_props"], "town_props", TOWN_PROP_MAP))
    cache.update(_mapped(sheets["exploration"], "exploration", EXPLORATION_MAP))
    cache.update(_mapped(sheets["battle"], "battle", BATTLE_MAP))
    cache.update(_mapped(sheets["battle"], "battle", MONSTER_MAP))
    cache.update(_mapped(
        sheets["battle_backdrops"], "battle_backdrops", BATTLE_BACKDROP_MAP))
    cache.update(_mapped(sheets["town_scene"], "town_scene", TOWN_SCENE_MAP))
    cache.update(_mapped(sheets["screens"], "screens", SCREEN_MAP))
    cache.update(_mapped(sheets["ui"], "ui", UI_MAP))
    cache.update(_mapped(sheets["effects_battle"], "effects_battle", EFFECT_MAP))
    return cache

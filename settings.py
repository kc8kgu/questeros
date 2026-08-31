"""Core display, gameplay, and map constants."""

from palette import (
    BLACK, BLUE, BROWN, CYAN, DKGREY, GREEN, GREY, LTBLUE, LTGREEN,
    LTGREY, LTRED, ORANGE, PURPLE, RED, WHITE, YELLOW,
)

TILE = 64                # native exploration tile size in pixels
UI_TILE = 16             # native interface texture and icon size
UI_SCALE = 4 / 3         # preserve interface proportions on the native canvas
VIEW_W, VIEW_H = 20, 13 # viewport size in tiles
FPS = 60

RENDER_SCALE = 1        # exploration renders at native resolution
WINDOW_SCALE = 1
RENDER_SIZE = (VIEW_W * TILE * RENDER_SCALE,
               VIEW_H * TILE * RENDER_SCALE)
WINDOW_SIZE = (VIEW_W * TILE * WINDOW_SCALE,
               VIEW_H * TILE * WINDOW_SCALE)

MAP_W, MAP_H = 64, 64   # overworld dimensions in tiles

# Town maps match the viewport so they don't scroll.
TOWN_W, TOWN_H = VIEW_W, VIEW_H

# Length of the animated step between two tiles, in seconds.
STEP_TIME = 0.14

# Rations: food cost and HP restored when eaten (from inventory or battle).
EAT_FOOD_COST = 10
EAT_HEAL = 15

# Tiles the player cannot walk onto.
BLOCKED = {"water", "tree", "mountain"}
TOWN_BLOCKED = {"twall", "bush", "crate"}

GUARD_STEP_TIME = 0.45


def ui(value):
    """Scale one legacy 960x624 interface measurement to the native canvas."""
    return round(value * UI_SCALE)

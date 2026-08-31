"""Semantic terrain keys for the asset-backed exploration renderer."""

UP = 1
RIGHT = 2
DOWN = 4
LEFT = 8
GRASS_VARIANTS = 4
SAND_VARIANTS = 4
WATER_VARIANTS = 1


def grass_key(variant):
    if not 0 <= variant < GRASS_VARIANTS:
        raise ValueError("Grass variant is out of range")
    return "grass" if variant == 0 else f"grass:v{variant}"


def sand_key(variant):
    if not 0 <= variant < SAND_VARIANTS:
        raise ValueError("Sand variant is out of range")
    return "sand" if variant == 0 else f"sand:v{variant}"


def water_key(mask, variant=0):
    if not 0 <= mask < 16:
        raise ValueError("Shoreline mask must be 0-15")
    if variant != 0:
        raise ValueError("Shoreline assets have one variant")
    return f"water:m{mask:02x}"


def tree_key(mask):
    if not 0 <= mask < 16:
        raise ValueError("Forest mask must be 0-15")
    return f"tree:m{mask:02x}"


def mountain_key(mask):
    if not 0 <= mask < 16:
        raise ValueError("Mountain mask must be 0-15")
    return f"mountain:m{mask:02x}"


def twall_key(mask):
    if not 0 <= mask < 16:
        raise ValueError("Town wall mask must be 0-15")
    return f"twall:m{mask:02x}"

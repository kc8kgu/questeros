"""Classic VGA Mode 13h palette and Questeros material ramps.

The VGA DAC stored six bits per RGB channel. ``MASTER_PALETTE`` exposes the
BIOS Mode 13h default palette converted to modern eight-bit channels by bit
replication. The final eight user-defined slots are black, matching the common
DOSBox-compatible default.
"""


def _rgb6_to_rgb8(value):
    """Expand one VGA six-bit channel to eight bits by bit replication."""
    if not 0 <= value <= 63:
        raise ValueError("VGA channel values must be in the range 0-63")
    return (value << 2) | (value >> 4)


def _build_vga_palette_6bit():
    colors = []

    # The CGA/EGA-compatible first 16 colors, encoded as IRGB.
    for index in range(16):
        high, low = ((63, 21) if index & 8 else (42, 0))
        red = high if index & 4 else low
        green = high if index & 2 else low
        blue = high if index & 1 else low
        if index == 6:
            green = 21  # Brown rather than dark yellow.
        colors.append((red, green, blue))

    # The BIOS default grayscale ramp at indices 16-31.
    for value in (0, 5, 8, 11, 14, 17, 20, 24,
                  28, 32, 36, 40, 45, 50, 56, 63):
        colors.append((value, value, value))

    def add_run(start, channel, low, medium_low, medium,
                medium_high, high):
        rgb = [
            high if start & 4 else low,
            high if start & 2 else low,
            high if start & 1 else low,
        ]
        colors.append(tuple(rgb))
        values = (
            (medium_high, medium, medium_low)
            if start & channel
            else (medium_low, medium, medium_high)
        )
        component = {4: 0, 2: 1, 1: 2}[channel]
        for value in values:
            rgb[component] = value
            colors.append(tuple(rgb))
        return start ^ channel

    def add_cycle(low, medium_low, medium, medium_high, high):
        hue = 1  # Each 24-color cycle begins at blue.
        for channel in (4, 1, 2, 4, 1, 2):
            hue = add_run(
                hue, channel, low, medium_low, medium, medium_high, high)

    # Nine HLS-like hue cycles: three lightness groups, each containing
    # pure, impure, and grayish saturation groups.
    for levels in (
        (0, 16, 31, 47, 63),
        (31, 39, 47, 55, 63),
        (45, 49, 54, 58, 63),
        (0, 7, 14, 21, 28),
        (14, 17, 21, 24, 28),
        (20, 22, 24, 26, 28),
        (0, 4, 8, 12, 16),
        (8, 10, 12, 14, 16),
        (11, 12, 13, 15, 16),
    ):
        add_cycle(*levels)

    colors.extend([(0, 0, 0)] * 8)
    if len(colors) != 256:
        raise AssertionError("VGA palette construction must yield 256 slots")
    return tuple(colors)


VGA_PALETTE_6BIT = _build_vga_palette_6bit()
MASTER_PALETTE = tuple(
    tuple(_rgb6_to_rgb8(channel) for channel in color)
    for color in VGA_PALETTE_6BIT
)
MASTER_COLOR_SET = frozenset(MASTER_PALETTE)


def palette_color(index):
    """Return the RGB value stored in one VGA palette slot."""
    if not 0 <= index < len(MASTER_PALETTE):
        raise ValueError("VGA palette index must be in the range 0-255")
    return MASTER_PALETTE[index]


def nearest_color(red, green, blue):
    """Return the nearest available VGA color to an eight-bit RGB value."""
    target = (red, green, blue)
    if not all(isinstance(channel, int) and 0 <= channel <= 255
               for channel in target):
        raise ValueError("RGB channels must be integers in the range 0-255")
    return min(
        MASTER_PALETTE,
        key=lambda color: sum(
            (channel - wanted) ** 2
            for channel, wanted in zip(color, target)),
    )


def is_master_color(color):
    """Return whether an RGB or RGBA value belongs to the VGA palette."""
    return tuple(color[:3]) in MASTER_COLOR_SET


# VGA-compatible legacy interface colors.
BLACK = palette_color(0)
BLUE = palette_color(1)
GREEN = palette_color(2)
CYAN = palette_color(3)
RED = palette_color(4)
PURPLE = palette_color(5)
BROWN = palette_color(6)
LTGREY = palette_color(7)
DKGREY = palette_color(8)
LTBLUE = palette_color(9)
LTGREEN = palette_color(10)
LTRED = palette_color(12)
YELLOW = palette_color(14)
WHITE = palette_color(15)
GREY = palette_color(24)
ORANGE = nearest_color(215, 135, 55)

# Semantic colors are snapped to exact entries in the VGA master palette.
INK = nearest_color(22, 20, 26)
NIGHT = nearest_color(32, 36, 62)
NAVY = nearest_color(42, 54, 94)
SKY = nearest_color(94, 140, 188)
ICE = nearest_color(174, 220, 232)
DEEP_WATER = nearest_color(31, 74, 98)
TEAL = nearest_color(45, 112, 116)
SEAFOAM = nearest_color(133, 202, 176)
DARK_GREEN = nearest_color(35, 71, 48)
FOREST = nearest_color(49, 104, 54)
MOSS = nearest_color(107, 137, 70)
PALE_GREEN = nearest_color(196, 224, 151)
DARK_BROWN = nearest_color(55, 40, 41)
UMBER = nearest_color(83, 57, 50)
OCHRE = nearest_color(177, 126, 64)
TAN = nearest_color(211, 169, 104)
SAND = nearest_color(225, 205, 137)
DARK_RED = nearest_color(92, 35, 42)
CRIMSON = nearest_color(173, 54, 55)
PINK = nearest_color(225, 124, 120)
DARK_PURPLE = nearest_color(62, 39, 76)
VIOLET = nearest_color(112, 64, 137)
LAVENDER = nearest_color(181, 127, 200)
GOLD = nearest_color(232, 181, 74)
PALE_YELLOW = nearest_color(244, 226, 142)
STEEL_DARK = nearest_color(55, 64, 73)
STEEL = nearest_color(102, 113, 125)
STEEL_LIGHT = nearest_color(181, 194, 199)
SKIN_DARK = nearest_color(94, 57, 49)
SKIN = nearest_color(196, 125, 83)
SKIN_LIGHT = nearest_color(238, 178, 128)
WHITE_WARM = palette_color(92)
MEADOW_DARK = palette_color(216)
MEADOW = palette_color(142)
MEADOW_LIGHT = palette_color(70)
DUNE_DARK = nearest_color(160, 124, 76)
DUNE = nearest_color(214, 183, 117)
DUNE_LIGHT = nearest_color(241, 218, 153)
OCEAN_DARK = nearest_color(25, 63, 91)
OCEAN = nearest_color(36, 98, 128)
OCEAN_LIGHT = nearest_color(76, 153, 171)
FOAM = nearest_color(171, 221, 198)
ROCK_SHADOW = nearest_color(49, 57, 70)
ROCK = nearest_color(91, 105, 119)
ROCK_LIGHT = nearest_color(153, 169, 177)

OVERLAY_DIM = (*BLACK, 160)
OVERLAY_DEATH = (*BLACK, 200)

FOLIAGE_RAMP = (
    palette_color(192), MEADOW_DARK, palette_color(144), MEADOW,
    MOSS, MEADOW_LIGHT, palette_color(94),
)
EARTH_RAMP = (
    palette_color(185), palette_color(209), palette_color(137),
    palette_color(138), BROWN, palette_color(65), palette_color(66),
    palette_color(67),
)
SAND_RAMP = (BROWN, OCHRE, DUNE_DARK, ORANGE, DUNE, DUNE_LIGHT)
STONE_RAMP = (
    INK, ROCK_SHADOW, STEEL_DARK, ROCK, GREY, ROCK_LIGHT, STEEL_LIGHT,
)
WATER_RAMP = (
    NIGHT, OCEAN_DARK, DEEP_WATER, OCEAN, TEAL, OCEAN_LIGHT, FOAM, ICE,
)
SKIN_RAMP = (
    palette_color(185), palette_color(209), palette_color(137),
    palette_color(65), palette_color(89), palette_color(91),
)
METAL_RAMP = (BLACK, INK, STEEL_DARK, STEEL, LTGREY, STEEL_LIGHT, WHITE)
FIRE_RAMP = (
    DARK_RED, RED, CRIMSON, ORANGE, GOLD, PALE_YELLOW, palette_color(15),
)
MAGIC_RAMP = (
    palette_color(176), palette_color(203), palette_color(128),
    palette_color(132), palette_color(80), palette_color(102),
)
INTERFACE_RAMP = (BLACK, INK, DKGREY, GREY, LTGREY, WHITE_WARM, WHITE)

RAMPS = {
    "foliage": FOLIAGE_RAMP,
    "earth": EARTH_RAMP,
    "sand": SAND_RAMP,
    "stone": STONE_RAMP,
    "water": WATER_RAMP,
    "skin": SKIN_RAMP,
    "metal": METAL_RAMP,
    "fire": FIRE_RAMP,
    "magic": MAGIC_RAMP,
    "interface": INTERFACE_RAMP,
}

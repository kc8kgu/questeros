"""Battle backdrop keys for the asset-backed renderer."""

BATTLE_BACKDROP_SIZE = (320, 144)
BATTLE_BACKDROP_TERRAINS = ("grass", "sand", "boss", "tfloor")


def battle_backdrop_key(terrain):
    if terrain not in BATTLE_BACKDROP_TERRAINS:
        raise ValueError(f"Unknown battle backdrop terrain: {terrain!r}")
    return f"battle_backdrop_{terrain}"

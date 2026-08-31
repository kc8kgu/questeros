"""Battle actor keys for the asset-backed renderer."""

from graphics.assets import BATTLE_MAP


BATTLE_ART_SIZE = 64
BATTLE_PLAYER_KEY = "battle_player"
BATTLE_MONSTER_LOOKS = {
    key.removeprefix("battle_mon_"): {"asset": key}
    for key in BATTLE_MAP
    if key.startswith("battle_mon_")
}


def battle_monster_key(monster_id):
    if monster_id not in BATTLE_MONSTER_LOOKS:
        raise ValueError(f"Unknown battle monster: {monster_id!r}")
    return f"battle_mon_{monster_id}"

"""Versioned, pygame-free save-game serialization."""
import json
import os
from pathlib import Path

import items
from player import FOOD_STEP_INTERVAL, STARVE_STEP_INTERVAL, Player

SAVE_VERSION = 1


class SaveGameError(Exception):
    """A save file could not be read, validated, or written."""


def default_path():
    return Path.home() / ".questeros" / "savegame.json"


def save_game(path, world_seed, player, location):
    path = Path(path)
    data = {
        "version": SAVE_VERSION,
        "world_seed": world_seed,
        "player": _player_data(player),
        "location": _location_data(location),
    }
    temporary = path.with_name(f".{path.name}.tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with temporary.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, sort_keys=True)
            file.write("\n")
        os.replace(temporary, path)
    except OSError as exc:
        raise SaveGameError("The game could not be saved.") from exc


def load_game(path):
    path = Path(path)
    try:
        with path.open(encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError as exc:
        raise SaveGameError("No saved game found.") from exc
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SaveGameError("The saved game could not be read.") from exc

    if not isinstance(data, dict):
        raise SaveGameError("The saved game has an invalid format.")
    if data.get("version") != SAVE_VERSION:
        raise SaveGameError("The saved game uses an unsupported version.")

    world_seed = _integer(data, "world_seed")
    location = _location_data(data.get("location"))
    player = _restore_player(
        data.get("player"), location["x"], location["y"])
    return world_seed, player, location


def _player_data(player):
    return {
        "max_hp": player.max_hp,
        "hp": player.hp,
        "gold": player.gold,
        "food": player.food,
        "level": player.level,
        "xp": player.xp,
        "steps": player.steps,
        "since_food": player._since_food,
        "since_starve": player._since_starve,
        "weapon": player.weapon,
        "armor": player.armor,
        "weapons_owned": sorted(player.weapons_owned),
        "armors_owned": sorted(player.armors_owned),
    }


def _restore_player(data, x, y):
    if not isinstance(data, dict):
        raise SaveGameError("The saved player has an invalid format.")

    max_hp = _integer(data, "max_hp", minimum=1)
    hp = _integer(data, "hp", minimum=1, maximum=max_hp)
    level = _integer(data, "level", minimum=1)
    weapon = _integer(
        data, "weapon", minimum=0, maximum=len(items.WEAPONS) - 1)
    armor = _integer(
        data, "armor", minimum=0, maximum=len(items.ARMORS) - 1)
    weapons_owned = _owned_items(
        data, "weapons_owned", len(items.WEAPONS))
    armors_owned = _owned_items(
        data, "armors_owned", len(items.ARMORS))
    if weapon not in weapons_owned or armor not in armors_owned:
        raise SaveGameError("The saved equipment is inconsistent.")

    player = Player(x, y)
    player.max_hp = max_hp
    player.hp = hp
    player.gold = _integer(data, "gold", minimum=0)
    player.food = _integer(data, "food", minimum=0, maximum=100)
    player.level = level
    player.xp = _integer(data, "xp", minimum=0)
    player.steps = _integer(data, "steps", minimum=0)
    player._since_food = _integer(
        data, "since_food", minimum=0, maximum=FOOD_STEP_INTERVAL - 1)
    player._since_starve = _integer(
        data, "since_starve", minimum=0,
        maximum=STARVE_STEP_INTERVAL - 1)
    player.weapon = weapon
    player.armor = armor
    player.weapons_owned = weapons_owned
    player.armors_owned = armors_owned
    return player


def _location_data(location):
    if not isinstance(location, dict):
        raise SaveGameError("The saved location has an invalid format.")
    kind = location.get("kind")
    if kind not in ("world", "town"):
        raise SaveGameError("The saved location is unknown.")

    result = {
        "kind": kind,
        "x": _integer(location, "x"),
        "y": _integer(location, "y"),
    }
    if kind == "town":
        result.update({
            "town_x": _integer(location, "town_x"),
            "town_y": _integer(location, "town_y"),
            "return_x": _integer(location, "return_x"),
            "return_y": _integer(location, "return_y"),
        })
    return result


def _integer(data, key, minimum=None, maximum=None):
    value = data.get(key)
    if type(value) is not int:
        raise SaveGameError(f"The saved value {key!r} is invalid.")
    if minimum is not None and value < minimum:
        raise SaveGameError(f"The saved value {key!r} is invalid.")
    if maximum is not None and value > maximum:
        raise SaveGameError(f"The saved value {key!r} is invalid.")
    return value


def _owned_items(data, key, item_count):
    values = data.get(key)
    if not isinstance(values, list) or not values:
        raise SaveGameError(f"The saved value {key!r} is invalid.")
    if any(type(value) is not int or not 0 <= value < item_count
           for value in values):
        raise SaveGameError(f"The saved value {key!r} is invalid.")
    return set(values)

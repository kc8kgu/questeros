"""Town maps: open plazas with counters, vendors, and patrolling guards."""
import random

import settings as s
from game_map import GameMap

GATE_X = s.TOWN_W // 2 - 1
SPAWN = (GATE_X, s.TOWN_H - 2)

SERVICES = ("weapon", "armor", "food", "inn", "casino")
COUNTER_TILES = {service: f"counter_{service}" for service in SERVICES}
STATIONS = {
    "weapon": ((4, 3), (5, 3)),
    "armor": ((14, 3), (15, 3)),
    "food": ((4, 7), (5, 7)),
    "casino": ((14, 7), (15, 7)),
    "inn": ((6, 10), (7, 10)),
}

ALCOVE_WALLS = (
    (3, 2), (4, 2), (5, 2),
    (13, 2), (14, 2), (15, 2),
    (3, 6), (4, 6), (3, 7),
    (14, 6), (15, 6), (16, 6),
    (5, 9), (5, 10), (5, 11), (6, 11), (7, 11),
    (14, 9), (15, 9), (16, 9), (16, 10),
)

CARDINAL = ((0, -1), (0, 1), (-1, 0), (1, 0))


class Vendor:
    def __init__(self, service, counter_x, counter_y, x, y):
        self.service = service
        self.counter_x = counter_x
        self.counter_y = counter_y
        self.x = x
        self.y = y
        self.alive = True
        self.robbed = False


class Guard:
    def __init__(self, route):
        self.route = route
        self.index = 0
        self.x, self.y = route[0]
        self.fx, self.fy = float(self.x), float(self.y)
        self.alive = True
        self.hostile = False
        self.step_timer = 0.0


class TownState:
    def __init__(self, vendors, guards):
        self.vendors = vendors
        self.guards = guards
        self.alerted = False


def generate(tx, ty):
    """Return a deterministic town map and its vendor/guard layout."""
    rng = random.Random(f"town-{tx}-{ty}")
    grid = [["tfloor"] * s.TOWN_W for _ in range(s.TOWN_H)]

    for x in range(s.TOWN_W):
        grid[0][x] = "twall"
        grid[s.TOWN_H - 1][x] = "twall"
    for y in range(s.TOWN_H):
        grid[y][0] = "twall"
        grid[y][s.TOWN_W - 1] = "twall"
    grid[s.TOWN_H - 1][GATE_X] = "gate"

    for x, y in ALCOVE_WALLS:
        grid[y][x] = "twall"
    vendors = _place_counters(grid)
    guards = _place_guards(rng, grid)
    _scatter_props(rng, grid)
    return GameMap(grid, s.TOWN_BLOCKED), TownState(vendors, guards)


def _place_counters(grid):
    vendors = []
    for service in SERVICES:
        (counter_x, counter_y), (vendor_x, vendor_y) = STATIONS[service]
        grid[counter_y][counter_x] = COUNTER_TILES[service]
        vendors.append(Vendor(
            service, counter_x, counter_y, vendor_x, vendor_y))
    return vendors


def _perimeter_route(grid):
    points = []
    for x in range(1, s.TOWN_W - 1):
        points.append((x, 1))
    for y in range(2, s.TOWN_H - 1):
        points.append((s.TOWN_W - 2, y))
    for x in range(s.TOWN_W - 3, 0, -1):
        points.append((x, s.TOWN_H - 2))
    for y in range(s.TOWN_H - 3, 1, -1):
        points.append((1, y))
    return [
        point for point in points
        if grid[point[1]][point[0]] == "tfloor"
    ]


def _place_guards(rng, grid):
    route = _perimeter_route(grid)
    if len(route) < 4:
        return []

    guards = []
    count = min(rng.randint(3, 4), len(route) // 4)
    spacing = max(1, len(route) // count)
    for index in range(count):
        start = (index * spacing) % len(route)
        length = min(rng.randint(4, 6), len(route))
        patrol = [route[(start + step) % len(route)] for step in range(length)]
        guards.append(Guard(patrol))
    return guards


def _scatter_props(rng, grid):
    corners = [(2, 2), (s.TOWN_W - 3, 2), (2, s.TOWN_H - 3),
               (s.TOWN_W - 3, s.TOWN_H - 3)]
    for x, y in corners:
        if grid[y][x] == "tfloor":
            grid[y][x] = "bush"
    extras = [
        (x, y) for x, y in ((2, 4), (17, 4), (2, 8), (17, 8), (10, 2))
        if grid[y][x] == "tfloor"
    ]
    if extras:
        x, y = rng.choice(extras)
        if rng.random() < 0.4:
            grid[y][x] = "crate"


def vendor_at(state, x, y):
    for vendor in state.vendors:
        if vendor.alive and vendor.x == x and vendor.y == y:
            return vendor
    return None


def guard_at(state, x, y):
    for guard in state.guards:
        if guard.alive and guard.x == x and guard.y == y:
            return guard
    return None


def vendor_for_service(state, service):
    for vendor in state.vendors:
        if vendor.service == service:
            return vendor
    return None

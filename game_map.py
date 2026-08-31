"""Pygame-free tile-map data and navigation rules."""

CARDINAL_DIRECTIONS = {
    "up": (0, -1),
    "down": (0, 1),
    "left": (-1, 0),
    "right": (1, 0),
}


class GameMap:
    def __init__(self, rows, blocked=()):
        if not rows or not rows[0]:
            raise ValueError("Map must contain at least one tile")

        width = len(rows[0])
        if any(len(row) != width for row in rows):
            raise ValueError("Map rows must all have the same width")

        self._rows = tuple(tuple(row) for row in rows)
        self.width = width
        self.height = len(rows)
        self.blocked = frozenset(blocked)

    def __eq__(self, other):
        if not isinstance(other, GameMap):
            return NotImplemented
        return self._rows == other._rows and self.blocked == other.blocked

    def __repr__(self):
        return (f"GameMap(width={self.width}, height={self.height}, "
                f"blocked={set(self.blocked)!r})")

    def in_bounds(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def tile_at(self, x, y):
        if not self.in_bounds(x, y):
            raise IndexError(f"Tile position out of bounds: ({x}, {y})")
        return self._rows[y][x]

    def is_walkable(self, x, y):
        return self.in_bounds(x, y) and self.tile_at(x, y) not in self.blocked

    def neighbors(self, x, y):
        if not self.in_bounds(x, y):
            raise IndexError(f"Tile position out of bounds: ({x}, {y})")

        result = {}
        for name, (dx, dy) in CARDINAL_DIRECTIONS.items():
            nx, ny = x + dx, y + dy
            if self.in_bounds(nx, ny):
                result[name] = self.tile_at(nx, ny)
        return result

    def tiles(self):
        for row in self._rows:
            yield from row

    def count(self, tile):
        return sum(row.count(tile) for row in self._rows)

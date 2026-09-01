"""Convert, pack, and audit committed VGA-compatible pixel artwork."""
import argparse
from collections import deque
from pathlib import Path
import sys

import pygame

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import palette

UP = 1
RIGHT = 2
DOWN = 4
LEFT = 8


def nearest_vga(color, cache=None, colors=None):
    """Return the nearest Mode 13h RGB color, caching repeated lookups."""
    rgb = tuple(color[:3])
    if cache is not None and rgb in cache:
        return cache[rgb]
    candidates = colors or palette.MASTER_PALETTE
    matched = min(
        candidates,
        key=lambda candidate: sum(
            (channel - wanted) ** 2
            for channel, wanted in zip(candidate, rgb)),
    )
    if cache is not None:
        cache[rgb] = matched
    return matched


def remove_connected_background(surface):
    """Make a light neutral background connected to an edge transparent."""
    source = surface.copy()
    width, height = source.get_size()
    visited = set()
    pending = deque()

    def background_candidate(x, y):
        color = source.get_at((x, y))
        rgb = color[:3]
        return min(rgb) >= 120 and max(rgb) - min(rgb) <= 24

    for x in range(width):
        for y in (0, height - 1):
            if background_candidate(x, y):
                pending.append((x, y))
    for y in range(height):
        for x in (0, width - 1):
            if background_candidate(x, y):
                pending.append((x, y))

    while pending:
        x, y = pending.popleft()
        if (x, y) in visited or not background_candidate(x, y):
            continue
        visited.add((x, y))
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height:
                pending.append((nx, ny))

    result = pygame.Surface((width, height), pygame.SRCALPHA)
    for y in range(height):
        for x in range(width):
            color = source.get_at((x, y))
            alpha = 0 if (x, y) in visited else 255
            result.set_at((x, y), (*color[:3], alpha))
    return result


def quantize(surface, logical_size, scale=2, alpha_threshold=128,
             seamless=False, colors=None, seamless_detail=64):
    """Reduce, VGA-quantize, and nearest-neighbor enlarge one surface."""
    logical_size = tuple(logical_size)
    if min(logical_size) <= 0 or scale <= 0 or seamless_detail <= 0:
        raise ValueError("Logical dimensions and scale must be positive")
    if seamless:
        if any(dimension % 2 for dimension in logical_size):
            raise ValueError("Seamless logical dimensions must be even")
        seed_size = tuple(dimension // 2 for dimension in logical_size)
        detail_size = tuple(
            min(dimension, seamless_detail) for dimension in seed_size)
        logical = pygame.transform.smoothscale(surface, detail_size)
    else:
        logical = pygame.transform.smoothscale(surface, logical_size)

    converted = pygame.Surface(logical.get_size(), pygame.SRCALPHA)
    color_cache = {}
    for y in range(logical.get_height()):
        for x in range(logical.get_width()):
            color = logical.get_at((x, y))
            if color.a < alpha_threshold:
                converted.set_at((x, y), (0, 0, 0, 0))
            else:
                converted.set_at(
                    (x, y), (*nearest_vga(color, color_cache, colors), 255))

    if seamless:
        if converted.get_size() != seed_size:
            converted = pygame.transform.scale(converted, seed_size)
        width, height = converted.get_size()
        logical = pygame.Surface(logical_size, pygame.SRCALPHA)
        logical.blit(converted, (0, 0))
        logical.blit(pygame.transform.flip(converted, True, False), (width, 0))
        logical.blit(pygame.transform.flip(converted, False, True), (0, height))
        logical.blit(pygame.transform.flip(converted, True, True), (width, height))
    else:
        logical = converted

    output_size = tuple(dimension * scale for dimension in logical_size)
    return pygame.transform.scale(logical, output_size)


def fit_alpha(surface, padding_ratio=0.08):
    """Crop a cutout to content and square-pad it for sprite conversion."""
    bounds = surface.get_bounding_rect(min_alpha=1)
    if not bounds.width or not bounds.height:
        raise ValueError("Cutout contains no opaque artwork")
    cropped = surface.subsurface(bounds).copy()
    side = max(bounds.size)
    padding = max(1, round(side * padding_ratio))
    fitted = pygame.Surface(
        (side + padding * 2, side + padding * 2), pygame.SRCALPHA)
    fitted.blit(cropped, (
        (fitted.get_width() - cropped.get_width()) // 2,
        (fitted.get_height() - cropped.get_height()) // 2,
    ))
    return fitted


def strip_pale_alpha_edges(surface, block_size=2):
    """Remove pale neutral blocks directly touching transparent cutout edges."""
    result = surface.copy()
    width, height = result.get_size()
    while True:
        removals = []
        for y in range(0, height, block_size):
            for x in range(0, width, block_size):
                color = result.get_at((x, y))
                rgb = color[:3]
                if color.a == 0 or min(rgb) < 190 \
                        or max(rgb) - min(rgb) > 24:
                    continue
                for dx, dy in (
                        (-block_size, -block_size), (0, -block_size),
                        (block_size, -block_size), (-block_size, 0),
                        (block_size, 0), (-block_size, block_size),
                        (0, block_size), (block_size, block_size)):
                    nx, ny = x + dx, y + dy
                    if not (0 <= nx < width and 0 <= ny < height) \
                            or result.get_at((nx, ny)).a == 0:
                        removals.append((x, y))
                        break
        if not removals:
            return result
        for x, y in removals:
            result.fill((0, 0, 0, 0), (x, y, block_size, block_size))


def pack_surfaces(surfaces, grid, cell_size, alpha=True):
    """Pack equally sized surfaces in row-major order."""
    columns, rows = grid
    if columns <= 0 or rows <= 0 or len(surfaces) > columns * rows:
        raise ValueError("Grid cannot contain the requested surfaces")
    flags = pygame.SRCALPHA if alpha else 0
    packed = pygame.Surface(
        (columns * cell_size[0], rows * cell_size[1]), flags, 32)
    if alpha:
        packed.fill((0, 0, 0, 0))
    for index, surface in enumerate(surfaces):
        if surface.get_size() != tuple(cell_size):
            raise ValueError("Every packed surface must match the cell size")
        packed.blit(surface, (
            index % columns * cell_size[0],
            index // columns * cell_size[1],
        ))
    return packed


def build_shoreline_atlas(scale=2):
    """Build the sixteen cardinal shoreline overlays at 32px logical size."""
    logical_size = 32
    band = 14
    frames = []
    for mask in range(16):
        frame = pygame.Surface((logical_size, logical_size), pygame.SRCALPHA)
        frame.fill((0, 0, 0, 0))
        for y in range(logical_size):
            for x in range(logical_size):
                distances = []
                if not mask & UP:
                    distances.append(y)
                if not mask & RIGHT:
                    distances.append(logical_size - 1 - x)
                if not mask & DOWN:
                    distances.append(logical_size - 1 - y)
                if not mask & LEFT:
                    distances.append(x)
                if not distances:
                    continue
                distance = min(distances)
                irregularity = ((x * 5 + y * 3 + mask * 7) % 5) - 2
                edge = band + irregularity
                if distance < edge:
                    color = palette.SAND_RAMP[4]
                    if (x * 11 + y * 7 + mask * 3) % 13 == 0:
                        color = palette.SAND_RAMP[1]
                    frame.set_at((x, y), (*color, 255))
                elif distance == edge:
                    frame.set_at((x, y), (*palette.FOAM, 255))
                elif distance == edge + 1 and (x + y + mask) % 3:
                    frame.set_at((x, y), (*palette.OCEAN_LIGHT, 255))
        frames.append(pygame.transform.scale(
            frame, (logical_size * scale, logical_size * scale)))
    return pack_surfaces(frames, (4, 4), (64, 64), alpha=True)


def audit_surface(surface, block_size=2, require_alpha=None):
    """Return human-readable violations of the VGA asset contract."""
    violations = []
    has_alpha = bool(surface.get_flags() & pygame.SRCALPHA)
    if require_alpha is not None and has_alpha != require_alpha:
        violations.append(
            f"expected {'RGBA' if require_alpha else 'opaque'} pixels")
    if block_size:
        if surface.get_width() % block_size or surface.get_height() % block_size:
            violations.append("dimensions are not divisible by block size")
        else:
            for y in range(0, surface.get_height(), block_size):
                for x in range(0, surface.get_width(), block_size):
                    expected = surface.get_at((x, y))
                    if expected.a not in (0, 255):
                        violations.append(f"semi-transparent pixel at {(x, y)}")
                        return violations
                    if expected.a and not palette.is_master_color(expected):
                        violations.append(
                            f"off-palette pixel at {(x, y)}: {expected[:3]}")
                        return violations
                    for dy in range(block_size):
                        for dx in range(block_size):
                            if surface.get_at((x + dx, y + dy)) != expected:
                                violations.append(
                                    f"nonuniform {block_size}x{block_size} block at {(x, y)}")
                                return violations
    else:
        for y in range(surface.get_height()):
            for x in range(surface.get_width()):
                color = surface.get_at((x, y))
                if color.a not in (0, 255):
                    violations.append(f"semi-transparent pixel at {(x, y)}")
                    return violations
                if color.a and not palette.is_master_color(color):
                    violations.append(
                        f"off-palette pixel at {(x, y)}: {color[:3]}")
                    return violations
    return violations


def _parse_pair(values, label):
    if len(values) != 2:
        raise ValueError(f"{label} requires two integers")
    return tuple(values)


def _convert_command(args):
    source = pygame.image.load(str(args.input))
    if args.crop:
        source = source.subsurface(pygame.Rect(args.crop)).copy()
    if args.cutout:
        source = remove_connected_background(source)
    if args.fit:
        source = fit_alpha(source)
    colors = None
    if args.ramp:
        colors = tuple(dict.fromkeys(
            color for ramp_name in args.ramp
            for color in palette.RAMPS[ramp_name]))
    result = quantize(
        source, _parse_pair(args.logical_size, "logical size"), args.scale,
        args.alpha_threshold, args.seamless, colors, args.detail_size)
    if args.cutout:
        result = strip_pale_alpha_edges(result, args.scale)
    pygame.image.save(result, str(args.output))


def _pack_command(args):
    surfaces = [pygame.image.load(str(path)) for path in args.inputs]
    packed = pack_surfaces(
        surfaces, _parse_pair(args.grid, "grid"),
        _parse_pair(args.cell_size, "cell size"), args.alpha)
    pygame.image.save(packed, str(args.output))


def _audit_command(args):
    failed = False
    for path in args.inputs:
        surface = pygame.image.load(str(path))
        violations = audit_surface(surface, args.block_size, args.alpha)
        if args.expect_size and surface.get_size() != tuple(args.expect_size):
            violations.append(
                f"expected size {tuple(args.expect_size)}, got {surface.get_size()}")
        if violations:
            failed = True
            print(f"{path}: {'; '.join(violations)}")
        else:
            print(f"{path}: OK")
    return 1 if failed else 0


def _shorelines_command(args):
    pygame.image.save(build_shoreline_atlas(args.scale), str(args.output))


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    convert = commands.add_parser("convert")
    convert.add_argument("input", type=Path)
    convert.add_argument("output", type=Path)
    convert.add_argument("--logical-size", nargs=2, type=int, required=True)
    convert.add_argument("--scale", type=int, default=2)
    convert.add_argument("--crop", nargs=4, type=int)
    convert.add_argument("--alpha-threshold", type=int, default=128)
    convert.add_argument("--cutout", action="store_true")
    convert.add_argument("--fit", action="store_true")
    convert.add_argument("--ramp", action="append", choices=palette.RAMPS)
    convert.add_argument("--seamless", action="store_true")
    convert.add_argument("--detail-size", type=int, default=64)
    convert.set_defaults(run=_convert_command)

    pack = commands.add_parser("pack")
    pack.add_argument("output", type=Path)
    pack.add_argument("inputs", nargs="+", type=Path)
    pack.add_argument("--grid", nargs=2, type=int, required=True)
    pack.add_argument("--cell-size", nargs=2, type=int, required=True)
    pack.add_argument("--alpha", action="store_true")
    pack.set_defaults(run=_pack_command)

    audit = commands.add_parser("audit")
    audit.add_argument("inputs", nargs="+", type=Path)
    audit.add_argument("--block-size", type=int, default=2)
    audit.add_argument("--expect-size", nargs=2, type=int)
    alpha = audit.add_mutually_exclusive_group()
    alpha.add_argument("--alpha", action="store_true", dest="alpha")
    alpha.add_argument("--opaque", action="store_false", dest="alpha")
    audit.set_defaults(run=_audit_command, alpha=None)

    shorelines = commands.add_parser("shorelines")
    shorelines.add_argument("output", type=Path)
    shorelines.add_argument("--scale", type=int, default=2)
    shorelines.set_defaults(run=_shorelines_command)
    return parser


def main(argv=None):
    pygame.init()
    try:
        args = build_parser().parse_args(argv)
        return args.run(args) or 0
    finally:
        pygame.quit()


if __name__ == "__main__":
    raise SystemExit(main())

# Questeros Visual Style

## Direction

- Use the approved original 16-bit Western-fantasy direction: earthy materials,
  cool shadows, upper-left lighting, strong silhouettes, and deliberate pixel
  clusters.
- Use the canonical VGA Mode 13h default palette defined in `palette.py` for
  every new or replacement asset. Opaque pixels must match one of its RGB
  entries exactly; transparent sheets use only alpha 0 or 255. Keep each asset
  on a focused subset of the full 256-slot palette.
- Use committed PNG family sprite sheets loaded through graphics/assets.py.
  Runtime code may composite, crop, fade, dim, shake, and fill dynamic bars,
  but must not generate replacement art.
- Keep crisp nearest-neighbor edges. Do not use antialiasing, blur, smooth
  gradients, generated text, logos, or watermarks.
- Generate source concepts for transparent sprites against a uniform black
  matte, not directly against transparency or a light background. Remove the
  connected matte offline with `tools/vga_art.py convert --cutout`, quantize
  to binary-alpha VGA pixels, apply `tools/vga_art.py outline`, and audit the
  finished sheet. The generated image is only a source concept; do not treat a
  generated checkerboard or claimed transparent background as final alpha.

## Readability

- The logical grid remains authoritative for movement, collision, saves, and map
  state. The visible layer may use multi-cell scenery and layered sprites.
- Keep walkable and blocked areas visually distinct and never imply collision
  that the map does not implement.
- Keep actors, gates, counters, landmarks, hazards, and UI selection states
  readable at native gameplay scale.

## Asset families

- tiles/overworld-simple-vga.png: 6x1 opaque 64px cells containing grass,
  sand, water, forest, mountain, and town in that order. Overworld scenery is
  drawn as ordinary single-cell tiles without large overlays.
- sprites/exploration-vga.png: 4x1 transparent native 64px player cells
  ordered up, down, left, right.
- Active VGA overworld artwork is authored and committed directly at 64x64.
  It is not enlarged from a smaller logical grid; retain crisp, blocky pixel
  clusters through palette reduction and nearest-neighbor presentation.
- tiles/overworld.png: 8x6 64px cells: 4 grass, 4 sand, 16 shoreline,
  8 forest, 8 mountain, and landmarks/spares.
- tiles/town.png: 5x5 64px cells with 16 wall masks, plaza, gate, and six
  service counters.
- sprites/exploration.png and sprites/battle.png: transparent actor sheets.
- scenes/battle-backdrops.png and scenes/screens.png: opaque backgrounds.
- ui/ui.png: transparent 16px UI cells including nine-slice skins, icons,
  bars, dividers, and selection art.
- effects/battle.png: transparent six-frame slash sheet.

Inspect intentional art changes at native size and in a resized gameplay view.

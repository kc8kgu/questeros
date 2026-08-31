# Questeros Visual Style

## Direction

- Use the approved original 16-bit Western-fantasy direction: earthy materials,
  cool shadows, upper-left lighting, strong silhouettes, and deliberate pixel
  clusters.
- Use committed PNG family sprite sheets loaded through graphics/assets.py.
  Runtime code may composite, crop, fade, dim, shake, and fill dynamic bars,
  but must not generate replacement art.
- Keep crisp nearest-neighbor edges. Do not use antialiasing, blur, smooth
  gradients, generated text, logos, or watermarks.

## Readability

- The logical grid remains authoritative for movement, collision, saves, and map
  state. The visible layer may use multi-cell scenery and layered sprites.
- Keep walkable and blocked areas visually distinct and never imply collision
  that the map does not implement.
- Keep actors, gates, counters, landmarks, hazards, and UI selection states
  readable at native gameplay scale.

## Asset families

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

# Questeros Plan

Questeros is a proof-of-concept and learning project. The current goal is a
small, understandable codebase, not a finished, content-rich, or highly polished
game. Prefer removing complexity and reusing existing systems over adding
flexibility, visual variety, or user-experience polish.

Core exploration, combat, equipment, and native 64x64 asset-backed graphics
already work. Towns are shared open-plaza scenes with separate weapon, armor,
food, inn, and casino counters, rob-or-fight vendors, and guards that react to
crime. The current game has a visible dragon boss, an explicit victory ending,
restart support, and a single save slot with continue support.

## Current visual-system migration

- Keep the grid-based rules and map state unchanged.
- Use the committed atlas families in assets/ through graphics/assets.py.
- Preserve dynamic text, runtime fades/dimming/shake, and deterministic map
  generation without procedural art fallbacks.

## Possible Future Directions

- Add a small dungeon system or one handcrafted dungeon.
- Expand the world with more biomes, towns, monsters, or gear.
- Curate additional atlas variants or animation while preserving readability.
- Add another focused battle-effects pass if playtesting identifies a need.
- Add sound only as a separate, explicitly scoped feature.
- Package the game for easier installation and distribution.
- Improve a specific user-experience problem identified through playtesting.

Choose a direction only when it serves a specific learning goal or addresses a
concrete problem found through playtesting.

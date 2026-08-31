# Questeros — Agent Guide

Python 3.13 + pygame 2.6.1 top-down RPG with committed 16-bit Western-fantasy
PNG sprite sheets.

## Commands

- Run: bash quest.sh
- Static check: git diff --check and .venv/Scripts/python.exe -m tabnanny .
- Full tests: SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/Scripts/python.exe -m unittest discover -v
- Smoke test:

  SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/Scripts/python.exe -c "import threading, pygame; from main import Game; game = Game(); threading.Timer(5, lambda: pygame.event.post(pygame.event.Event(pygame.QUIT))).start(); game.run()"

## Rules

- All visual art is committed PNG atlas data. Do not add generated-at-runtime
  art or audio assets. Follow STYLE_GUIDE.md for visual work.
- Keep clear boundaries between pygame presentation and internal game rules.
  Gameplay logic and map state stay pygame-free; rendering and input stay in
  scenes, views, and graphics code.
- Scenes implement handle_event, update, and draw. Change scenes through
  Game.change_scene() and retain return scenes when needed.
- Handle walk-on behavior in the active scene's on_arrive(), not movement code.
- Use GameMap for bounds and collision. Do not hardcode overworld dimensions.
- Every map tile name must have a matching cached surface.
- Town services use walkable counter_* tiles and overlay vendor/guard sprites.
- Preserve deterministic world, town, and visual presentation.
- Add monsters to combat.MONSTERS and the matching asset mappings.
- Keep colors, rules, and constants centralized; use hud.get_font() for UI text.
- Keep asset paths and row-major mappings in graphics/assets.py; resolve paths
  relative to that module and fail clearly for missing or malformed assets.
- Preserve the logical tile grid for movement, collision, saves, and map state;
  visuals may span multiple cells through layered atlas sprites.
- Prefer the simplest direct implementation and remove unnecessary code.
- Visually inspect intentional art changes at native and resized gameplay scale.

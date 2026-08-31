# Questeros

Questeros is a small Questron/Ultima-style top-down RPG prototype built with
Python and pygame. It currently includes a deterministic overworld, grid-based
exploration, hunger, character progression, random encounters, turn-based
combat, and a dragon boss with an explicit victory ending at a volcanic
landmark. A single save slot can preserve progress between sessions.

Towns are open stone-walled plazas. Walk onto a wooden counter to shop
(weapons, armor, food, inn, or casino). Walk onto the vendor beside a counter
to rob or fight them. Guards patrol the plaza and turn hostile after a crime
or a large casino payout. Dead vendors and guard alerts reset when you leave
the town.

The presentation uses original committed PNG sprite sheets in a cohesive
16-bit Western-fantasy style with native 64x64 exploration art, detailed
open-plaza towns, dedicated battle combatants, terrain-aware backdrops,
image-backed UI panels, and bundled Silkscreen fonts. The logical world remains
tile-based, while multi-cell scenery and layered sprites provide the richer
scene composition. Audio is out of scope.

## Requirements

- Python 3.13
- pygame 2.6.1
- A Bash-compatible shell for the optional `quest.sh` launcher

## Initialize the local environment

From the repository root, create a Python 3.13 virtual environment and install
the pinned dependencies into it:

```bash
python3.13 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
```

On Windows PowerShell, use the Windows launcher and virtual-environment path:

```powershell
py -3.13 -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

The `.venv` directory is local to the checkout and ignored by Git. Activation
is optional: the project commands below invoke its interpreter directly so they
do not accidentally use a different system Python.

## Running

The checked-in [`quest.sh`](quest.sh) launcher resolves the repository directory
and starts `main.py` with the local virtual environment. It supports the POSIX
`.venv/bin/python` and Windows `.venv/Scripts/python.exe` layouts:

```bash
bash quest.sh
```

Because the launcher resolves its own location, it can also be invoked by path
from another working directory. You can instead run `main.py` directly with the
appropriate virtual-environment interpreter.

Optional flags for New Game:

- `--no-encounters`: disable random overworld encounters.
- `--god-mode`: start with 1000 HP, 1000 gold, and invincibility.

Flags can be combined, for example:
`bash quest.sh --no-encounters --god-mode`.

Controls:

- Arrow keys or WASD: move and navigate menus
- Enter or Space: confirm
- I: open or close inventory
- F5: save while exploring the overworld or a town
- F11: toggle fullscreen
- Q: open quit confirmation from any scene
- Escape: close an overlay, or open quit confirmation if none is active
- G: toggle god mode from any scene
- E: toggle random encounters from any scene
- Any key: leave a completed battle
- R: restart after death or victory
- C: continue from the last save after death

Restarting returns to normal stats and enables random encounters.

The game opens on a menu with New Game, Continue, and Quit. Continue becomes
available after the first save. Saves are stored at
`~/.questeros/savegame.json`; battles, death, victory, and god mode cannot be
saved. Loading restores player progression and overworld or town position, but
does not restore developer-mode toggles. If Continue cannot read the save, the
game shows a warning and starts a fresh run.

The game starts on a native 1280x832 canvas in a resizable window. Wider or
taller windows expand the viewport to reveal more of the map.

## Testing

Run the complete regression suite with the same virtual environment:

```bash
.venv/bin/python -m unittest discover -v
```

On Windows, replace `.venv/bin/python` with
`.venv\Scripts\python.exe`.

The tests configure pygame's dummy video and audio drivers automatically and
cover gameplay rules, deterministic generation, scene transitions, input routing,
rendering, save-game validation, and graphics-cache determinism.

## Project structure

- `main.py` owns the game lifecycle, shared resources, and scene transitions.
- `scenes/` contains startup, exploration, battle, and ending behavior.
- `graphics/` loads and validates the committed atlas sheets and exposes the
  cache used by scenes and views.
- `assets/` contains the PNG sheets and Silkscreen font files used at runtime.
- `player.py`, `combat.py`, `casino.py`, and `town_crime.py` contain
  display-independent gameplay rules.
- `savegame.py` provides versioned JSON serialization and validation.
- `world.py`, `town.py`, and `game_map.py` provide deterministic maps.
- `tests/` contains unit and headless integration coverage, including asset
  dimensions, mappings, alpha, and startup validation.
- `PLAN.md` tracks possible future directions.

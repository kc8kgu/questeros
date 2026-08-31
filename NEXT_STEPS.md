Continue the uncommitted Questeros visual-system migration in:

C:\code\questeros

Preserve every existing working-tree change. Do not reset, checkout, clean, discard, or overwrite unrelated work. Do not commit unless I explicitly request it.

Start by:

1. Reading AGENTS.md and STYLE\_GUIDE.md.
2. Inspecting `git status --short --untracked-files=all`.
3. Inspecting the current renderer and asset mappings.
4. Visually inspecting the latest overworld capture with `view_image`:

C:\Users\dlc.codex\visualizations\2026\08\31\01a055a7-a5c5-7030-bc5b-4e77fc425207\runtime-overworld.png

Compare it against the approved target:

C:\Users\dlc.codex\visualizations\2026\08\31\01a05572-f727-7040-83ed-cf59312d9a47\mockup-overworld.png

Current state:

- The asset-backed migration is implemented but uncommitted.
- The overworld uses continuous 1024-pixel world-space material textures and layered transparent multi-cell forest, mountain, town, and boss props.
- Water uses the continuous material layer plus translucent shoreline transitions.
- Town presentation now uses a composed plaza backdrop and large service structures.
- Battle backdrops no longer contain embedded actors or UI.
- The UI atlas and battle lower combat interface were rebuilt.
- Runtime text remains dynamically rendered with the bundled Silkscreen fonts.
- No gameplay rules, collision, walkability, map generation, saves, timing, camera behavior, display geometry, or audio were changed.

The most recent overworld correction removed actual white/checkerboard fringe pixels from:

C:\code\questeros\assets\tiles\overworld-props.png

A regression test now verifies that pale neutral pixels do not touch transparent prop edges. The latest alpha-cleaned overworld capture is the `runtime-overworld.png` path above.

Relevant changed files include:

- assets/scenes/battle-backdrops.png
- assets/scenes/town.png
- assets/tiles/materials.png
- assets/tiles/overworld-props.png
- assets/tiles/town-props.png
- assets/ui/ui.png
- battle\_view\.py
- graphics/assets.py
- map\_view\.py
- menus.py
- tests/test\_graphics.py

Verification already completed:

- Full suite passed before the final alpha cleanup: 111 tests.
- After alpha cleanup, 14 graphics/map rendering tests passed.
- `git diff --check` passed.
- Earlier `tabnanny`, `compileall`, and five-second dummy-SDL smoke tests passed.

Continue the overworld visual review from this exact state. Diagnose remaining differences from the approved mockup before editing. Pay particular attention to terrain repetition, forest and mountain clustering, shoreline composition, landmark scale, and whether any opaque matte remnants remain at gameplay scale.

For replacement raster artwork, use the built-in image-generation workflow and commit final PNG atlases into the workspace. Do not restore procedural runtime art or add a procedural fallback. Maintain the approved cohesive 16-bit Western-fantasy direction: earthy materials, cool shadows, upper-left lighting, deliberate pixel clusters, crisp nearest-neighbor edges, no generated text, and no watermarks.

After changes, capture and visually inspect a new overworld screenshot containing shoreline, forest, mountains, player, and HUD. Run the relevant tests and `git diff --check`; run the full verification suite before declaring the visual pass complete. Do not create Markdown files, modify audio, or commit.
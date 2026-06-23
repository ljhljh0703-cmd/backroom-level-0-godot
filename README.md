# Level 0: No Exit

Godot 4 point-and-click horror prototype.

## Run

```bash
godot --path .
```

## Validate

```bash
python3 tools/validate_routes.py
godot --headless --path . --script tools/qa_game_flow.gd
```

## Export Web

```bash
mkdir -p builds/web
godot --headless --path . --export-release Web builds/web/index.html
python3 tools/prepare_web_build.py
```

`prepare_web_build.py` creates a commit-suffixed `.pck` and updates `index.html` so GitHub Pages/browser caches cannot keep serving an older game pack.

## Portfolio HTML

```bash
python3 tools/build_portfolio_html.py
```

The portfolio builder creates `docs/backroom-portfolio.html` as the source artifact and copies the same single-file HTML to `builds/web/portfolio.html` for GitHub Pages deployment. It also writes `backroom-pages-registry.json`, which tracks both deployed HTML entry points: `index.html` for the playable Godot export and `portfolio.html` for the case study.

The current creature sprite is a placeholder. Replace `assets/images/creature.png` with a processed portrait-derived creature when the final source photo is available.

## Development Notes

- [GDD](docs/GDD.md): approved game design direction.
- [Development Requirements](docs/DEV_REQUIREMENTS.md): approved GDD converted into route, hotspot, state, and ending requirements.
- [CodeGraph](docs/CODEGRAPH.md): code/data map for efficient edits.
- [Progress](docs/PROGRESS.md): current decisions, enhancement direction, review log, and next work packet.
- [Play Experience Proposal](docs/PLAY_EXPERIENCE_PROPOSAL.md): next pass recommendations for tension, clues, and ending feel.

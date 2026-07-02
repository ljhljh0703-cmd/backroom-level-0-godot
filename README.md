# BackRoom Level 0

Short Backrooms-inspired point-and-click horror game built with Godot 4.

Enter the space behind the STOP sign, read how the room changes, and find the route that leads home. The game is intentionally compact: one looping fork, a few state changes, and three endings.

## Play

- [Play the web build](https://ljhljh0703-cmd.github.io/backroom-level-0-godot/)
- [Read the portfolio page](https://ljhljh0703-cmd.github.io/backroom-level-0-godot/portfolio.html)

The GitHub Pages root is kept as the playable game. The portfolio page is published separately at `/portfolio.html` so the game link stays direct.

## Game Notes

- Genre: short single-player horror click adventure.
- Goal: read the clues and room states to find the real exit.
- Endings: true escape, false exit, and failed re-entry.
- Build: Godot 4 Web export.

## Run Locally

```bash
godot --path .
```

## Validate Routes and Endings

```bash
python3 tools/validate_routes.py
godot --headless --path . --script tools/qa_game_flow.gd
```

## Export the Web Build

```bash
mkdir -p builds/web
godot --headless --path . --export-release Web builds/web/index.html
python3 tools/prepare_web_build.py
```

`prepare_web_build.py` creates a commit-suffixed `.pck` and updates `index.html` so GitHub Pages/browser caches cannot keep serving an older game pack.

## Build the Portfolio Page

```bash
python3 tools/build_portfolio_html.py
```

The portfolio builder creates `docs/backroom-portfolio.html` as the source artifact and copies the same single-file HTML to `builds/web/portfolio.html` for GitHub Pages deployment. It also writes `backroom-pages-registry.json`, which tracks both deployed HTML entry points: `index.html` for the playable Godot export and `portfolio.html` for the case study.

## Deployment Shape

```text
GitHub Pages
/                playable Godot Web game
/portfolio.html  game detail and portfolio case study
```

The current creature sprite is a placeholder. Replace `assets/images/creature.png` with a processed portrait-derived creature when the final source photo is available.

## Development Notes

- [GDD](docs/GDD.md): approved game design direction.
- [Development Requirements](docs/DEV_REQUIREMENTS.md): approved GDD converted into route, hotspot, state, and ending requirements.
- [CodeGraph](docs/CODEGRAPH.md): code/data map for efficient edits.
- [Progress](docs/PROGRESS.md): current decisions, enhancement direction, review log, and next work packet.
- [Play Experience Proposal](docs/PLAY_EXPERIENCE_PROPOSAL.md): next pass recommendations for tension, clues, and ending feel.

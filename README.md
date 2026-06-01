# Level 0: No Exit

Godot 4 point-and-click horror prototype.

## Run

```bash
godot --path .
```

## Export Web

```bash
mkdir -p builds/web
godot --headless --path . --export-release Web builds/web/index.html
```

The current creature sprite is a placeholder. Replace `assets/images/creature.png` with a processed portrait-derived creature when the final source photo is available.

## Development Notes

- [CodeGraph](docs/CODEGRAPH.md): code/data map for efficient edits.
- [Progress](docs/PROGRESS.md): current decisions, enhancement direction, review log, and next work packet.

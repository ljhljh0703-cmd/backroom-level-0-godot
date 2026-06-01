from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BUILD_DIR = ROOT / "builds" / "web"
CONFIG_RE = re.compile(r"const GODOT_CONFIG = (\{.*?\});")


def current_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    return result.stdout.strip()


def patch_html(html_path: Path, versioned_pack: str, pack_size: int) -> None:
    html = html_path.read_text(encoding="utf-8")
    match = CONFIG_RE.search(html)
    if match is None:
        raise RuntimeError(f"GODOT_CONFIG not found in {html_path}")

    config = json.loads(match.group(1))
    file_sizes = dict(config.get("fileSizes", {}))
    file_sizes[versioned_pack] = pack_size
    config["fileSizes"] = file_sizes
    config["mainPack"] = versioned_pack

    patched_config = json.dumps(config, separators=(",", ":"), ensure_ascii=False)
    html_path.write_text(
        html[: match.start(1)] + patched_config + html[match.end(1) :],
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Add a cache-busted Godot Web pack file.")
    parser.add_argument("--build-dir", default=str(DEFAULT_BUILD_DIR), help="Directory containing index.html and index.pck.")
    parser.add_argument("--version", default=current_commit(), help="Version suffix for the copied .pck file.")
    args = parser.parse_args()

    build_dir = Path(args.build_dir).resolve()
    html_path = build_dir / "index.html"
    pack_path = build_dir / "index.pck"
    if not html_path.exists():
        raise FileNotFoundError(html_path)
    if not pack_path.exists():
        raise FileNotFoundError(pack_path)

    versioned_pack = f"index-{args.version}.pck"
    versioned_path = build_dir / versioned_pack
    shutil.copy2(pack_path, versioned_path)
    patch_html(html_path, versioned_pack, versioned_path.stat().st_size)

    print(f"Prepared web build: {versioned_pack}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

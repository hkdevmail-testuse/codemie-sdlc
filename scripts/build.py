#!/usr/bin/env python3
"""Build script to create a deployable artifact for the Flask application.

Creates a zip containing:
- src/ (application code)
- scripts/ (utility scripts)
- README.md

No secrets are embedded.
"""

from __future__ import annotations

import argparse
import os
import pathlib
import sys
import zipfile


ROOT = pathlib.Path(__file__).resolve().parents[1]


def add_dir(zf: zipfile.ZipFile, base: pathlib.Path, arc_prefix: str) -> None:
    for path in base.rglob("*"):
        if path.is_dir():
            continue
        rel = path.relative_to(base)
        arcname = str(pathlib.Path(arc_prefix) / rel)
        zf.write(path, arcname)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, help="Output zip path")
    args = parser.parse_args(argv)

    out_path = pathlib.Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        add_dir(zf, ROOT / "src", "src")
        if (ROOT / "scripts").exists():
            add_dir(zf, ROOT / "scripts", "scripts")
        if (ROOT / "README.md").exists():
            zf.write(ROOT / "README.md", "README.md")

    size = out_path.stat().st_size
    print(f"Created artifact: {out_path} ({size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

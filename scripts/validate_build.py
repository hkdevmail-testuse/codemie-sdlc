#!/usr/bin/env python3
"""Lightweight build validation.

- Builds the zip artifact
- Verifies expected files exist in the zip
"""

from __future__ import annotations

import pathlib
import subprocess
import sys
import zipfile


ROOT = pathlib.Path(__file__).resolve().parents[1]


def main() -> int:
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    artifact = dist / "expense-tracker.zip"

    subprocess.check_call([sys.executable, str(ROOT / "scripts" / "build.py"), "--out", str(artifact)])

    required = {
        "src/app.py",
        "src/requirements.txt",
        "src/templates/index.html",
    }

    with zipfile.ZipFile(artifact) as zf:
        names = set(zf.namelist())

    missing = sorted(required - names)
    if missing:
        print("Artifact validation failed. Missing:")
        for m in missing:
            print(f"- {m}")
        return 2

    print(f"Build validation OK: {artifact}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

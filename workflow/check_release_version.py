# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Check that the requested release version matches ``pyproject.toml``.

Run before building, so a release can never be cut from a tree whose
declared version is still a ``.devN`` (or otherwise different) version.
"""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_release_version.py VERSION", file=sys.stderr)
        return 2

    version = sys.argv[1].strip().lstrip("v")
    declared = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))[
        "project"
    ]["version"]

    if re.fullmatch(r"\d+(\.\d+)*", version) is None:
        print(f"FAIL  {version} is not a release version", file=sys.stderr)
        return 1
    if declared != version:
        print(
            f"FAIL  pyproject.toml declares {declared}, not {version}: "
            "bump the version before publishing",
            file=sys.stderr,
        )
        return 1

    print(f"PASS  version {version} matches pyproject.toml")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

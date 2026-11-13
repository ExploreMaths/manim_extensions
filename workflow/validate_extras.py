# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Validate the optional-dependency table in ``pyproject.toml``.

Rules enforced here:

* an extra that names a module must declare at least one dependency;
* ``all`` must reference every module extra, and no unknown extra;
* ``all`` itself must not be empty.

An empty extra can never gain dependencies without changing the module's
install contract, so it is permanent metadata noise.  Adding a dependency
to a module means adding the extra at the same time.
"""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = ROOT / "pyproject.toml"
TOOLING_EXTRAS = {"dev", "docs", "all"}

SELF_REFERENCE = re.compile(r"^manim_extensions\[([^\]]+)\]$")


def load_extras() -> dict[str, list[str]]:
    """Return ``project.optional-dependencies`` from ``pyproject.toml``."""
    with PYPROJECT.open("rb") as file:
        data = tomllib.load(file)
    return data["project"]["optional-dependencies"]


def all_references(value: list[str]) -> set[str]:
    """Return the extras named by the ``all`` self-reference."""
    for requirement in value:
        match = SELF_REFERENCE.match(requirement)
        if match:
            return {name.strip() for name in match.group(1).split(",") if name.strip()}
    return set()


def main() -> int:
    """Report extras that are empty or missing from ``all``."""
    extras = load_extras()
    issues: list[str] = []

    module_extras = set(extras) - TOOLING_EXTRAS
    for name in sorted(module_extras):
        if not extras[name]:
            issues.append(f"extra '{name}' is empty; remove it or add its dependencies")

    referenced = all_references(extras.get("all", []))
    missing = module_extras - referenced
    unknown = referenced - module_extras
    if missing:
        issues.append(f"'all' is missing extras: {', '.join(sorted(missing))}")
    if unknown:
        issues.append(f"'all' references unknown extras: {', '.join(sorted(unknown))}")
    if not referenced:
        issues.append("'all' does not reference any module extra")

    if issues:
        for issue in issues:
            print(f"FAIL optional-extras: {issue}")
        return 1

    print(f"PASS optional-extras ({len(module_extras)} module extras)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

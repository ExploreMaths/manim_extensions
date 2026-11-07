# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Prepare the tree for a release.

Sets the version in ``pyproject.toml`` and moves the changelog badge from
the previous version to the one being published, so the manual publish
workflow does not need a separate hand-written version commit.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

VERSION_RE = re.compile(r"^v(?P<version>\d+(?:\.\d+)*)")
BADGE_RE = re.compile(r"\s*:bdg-[A-Za-z0-9_-]+:`[^`]*`")
LATEST = " :bdg-success-line:`Latest`"


def bump_pyproject(text: str, version: str) -> str:
    updated, count = re.subn(
        r'(?m)^version = "[^"]*"$', f'version = "{version}"', text, count=1
    )
    if count != 1:
        raise SystemExit("could not find the version line in pyproject.toml")
    return updated


def bump_changelog(text: str, version: str) -> str:
    lines = text.splitlines(True)
    versions = [i for i, line in enumerate(lines) if VERSION_RE.match(line)]
    targets = [
        i
        for i in versions
        if VERSION_RE.match(lines[i]).group("version") == version
    ]
    if not targets:
        raise SystemExit(f"changelog.rst has no section for version {version}")

    target = targets[0]
    lines[target] = f"v{version}{LATEST}\n"

    # The previous release keeps its content but loses the "Latest" badge.
    previous = [i for i in versions if i > target]
    if previous:
        line = BADGE_RE.sub("", lines[previous[0]]).rstrip()
        lines[previous[0]] = line + "\n"

    return "".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True, help="version to prepare, no leading v")
    parser.add_argument(
        "--pyproject", type=Path, default=Path("pyproject.toml"), help="pyproject.toml path"
    )
    parser.add_argument(
        "--changelog",
        type=Path,
        default=Path("docs/source/changelog.rst"),
        help="changelog path",
    )
    parser.add_argument(
        "--check", action="store_true", help="report the changes without writing them"
    )
    args = parser.parse_args()

    version = args.version.strip().lstrip("v")
    if re.fullmatch(r"\d+(\.\d+)*", version) is None:
        print(f"FAIL  {version} is not a release version", file=sys.stderr)
        return 1

    pyproject = bump_pyproject(args.pyproject.read_text(encoding="utf-8"), version)
    changelog = bump_changelog(args.changelog.read_text(encoding="utf-8"), version)

    if args.check:
        print(f"would set pyproject.toml and changelog.rst to version {version}")
        return 0

    args.pyproject.write_text(pyproject, encoding="utf-8")
    args.changelog.write_text(changelog, encoding="utf-8")
    print(f"PASS  prepared version {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Render a changelog.rst version section as a GitHub release body.

The release notes published for the previous versions are plain Markdown:
a *Full Changelog* link, a *View on PyPI* link and a ``## What's Changed``
heading followed by the ``### Added`` / ``### Changed`` / ... sections of
the matching changelog entry, with every reST cross-reference flattened to
its bare name.  This script produces that Markdown from the single source
of truth (``docs/source/changelog.rst``).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

VERSION_RE = re.compile(r"^v(?P<version>\d+(?:\.\d+)*)\b")
SECTION_RE = re.compile(r"^\*\*(?P<title>[^*]+)\*\*$")
ITEM_RE = re.compile(r"^\*(?: +(?P<text>.*))?$")
CONT_RE = re.compile(r"^  +(?P<text>.*)$")

ROLE_RE = re.compile(r":(?P<role>[A-Za-z0-9_+-]+):`(?P<body>[^`]*)`")
CODE_RE = re.compile(r"``(?P<code>[^`]*)``")


def _strip_roles(text: str) -> str:
    """Flatten every reST role to plain text (no links survive)."""

    def replace(match: re.Match[str]) -> str:
        role = match.group("role")
        body = match.group("body").strip()
        if role.startswith("bdg-"):
            return ""
        if role == "math":
            return body
        if "<" in body and body.endswith(">"):
            display, target = body[:-1].split("<", 1)
            display = display.strip()
            target = target.strip().lstrip("~")
            return display or target.rsplit(".", 1)[-1]
        return body.lstrip("~").rsplit(".", 1)[-1]

    return ROLE_RE.sub(replace, text)


def _inline(text: str) -> str:
    """Convert one reST line to Markdown text with no links."""
    text = _strip_roles(text)
    text = CODE_RE.sub(lambda m: "`" + m.group("code") + "`", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def _section(lines: list[str], version: str) -> list[str] | None:
    """Return the lines of the ``version`` section, title included."""
    for index, line in enumerate(lines):
        match = VERSION_RE.match(line)
        if match and match.group("version") == version:
            for stop in range(index + 1, len(lines)):
                if VERSION_RE.match(lines[stop]):
                    return lines[index:stop]
            return lines[index:]
    return None


def render(section: list[str]) -> str:
    """Render a changelog section as Markdown (relative heading level 3)."""
    body = section[2:]  # drop the "vX.Y.Z :badge:" line and its underline
    out: list[str] = []
    pending: list[str] | None = None

    def flush() -> None:
        nonlocal pending
        if pending is not None:
            out.append("- " + _inline(" ".join(pending)))
            pending = None

    for raw in body:
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped:
            flush()
            continue
        heading = SECTION_RE.match(stripped)
        if heading:
            flush()
            out.extend(["", "### " + heading.group("title").strip(), ""])
            continue
        item = ITEM_RE.match(stripped)
        if item:
            flush()
            pending = [(item.group("text") or "").strip()]
            continue
        continuation = CONT_RE.match(line)
        if continuation and pending is not None:
            pending.append(continuation.group("text").strip())
            continue
        flush()
        out.append(_inline(stripped))

    flush()

    # Collapse the blank lines the section headings introduced.
    rendered: list[str] = []
    for entry in out:
        if entry == "" and rendered and rendered[-1] == "":
            continue
        rendered.append(entry)
    while rendered and rendered[0] == "":
        rendered.pop(0)
    while rendered and rendered[-1] == "":
        rendered.pop()
    return "\n".join(rendered) + "\n"


def render_release(version: str, changelog: Path, previous: str | None) -> str:
    """Render the complete GitHub release body for ``version``."""
    lines = changelog.read_text(encoding="utf-8").splitlines()
    section = _section(lines, version)
    if section is None:
        raise SystemExit(f"changelog.rst has no section for version {version}")
    tag = f"v{version}"
    repo = "https://github.com/ExploreMaths/manim_extensions"
    if previous:
        compare = f"{repo}/compare/v{previous}...{tag}"
    else:
        compare = f"{repo}/commits/{tag}"
    pypi = f"https://pypi.org/project/manim-extensions/{version}/"
    header = (
        f"**Full Changelog**: {compare}\n\n"
        f"**View on PyPI**: {pypi}\n\n"
        "## What's Changed\n\n"
    )
    return header + render(section)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--changelog",
        type=Path,
        default=Path("docs/source/changelog.rst"),
        help="path to the changelog (default: docs/source/changelog.rst)",
    )
    parser.add_argument("--version", help="version to render, without a leading v")
    parser.add_argument("--previous", help="previous version, for the compare link")
    parser.add_argument("--out", type=Path, help="write the release body to this file")
    parser.add_argument(
        "--check", action="store_true", help="only check that the section exists"
    )
    parser.add_argument("--list", action="store_true", help="list the documented versions")
    args = parser.parse_args()

    lines = args.changelog.read_text(encoding="utf-8").splitlines()

    if args.list:
        for line in lines:
            match = VERSION_RE.match(line)
            if match:
                print(match.group("version"))
        return 0

    if not args.version:
        parser.error("--version is required unless --list is given")

    if _section(lines, args.version) is None:
        print(
            f"FAIL  no changelog section for version {args.version}",
            file=sys.stderr,
        )
        return 1
    if args.check:
        print(f"PASS  changelog section for version {args.version} exists")
        return 0

    text = render_release(args.version, args.changelog, args.previous)
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Validate and normalize the SPDX header block of every Python file.

The canonical header is a single contiguous comment block at the very top
of the file (after an optional shebang) with this order:

    # SPDX-FileCopyrightText: <upstream authors>
    # SPDX-FileCopyrightText: 2026 ExploreMaths
    # SPDX-License-Identifier: MIT
    # patched: <reason>

Rules enforced here:

* one copyright line per holder, with no repeated year;
* exactly one license line, placed after the copyright lines;
* ``# patched:`` lines only after the license line;
* no blank comment (``#``) lines and no non-SPDX comments inside the block.

``--fix`` rewrites offending headers; a file without any header gets the
project default (``2026 ExploreMaths``, ``MIT``).

Usage:
    python workflow/validate_headers.py
    python workflow/validate_headers.py --fix
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# REUSE-IgnoreStart
COPYRIGHT_RE = re.compile(r"^#\s*SPDX-FileCopyrightText:\s*(.*)$")
LICENSE_RE = re.compile(r"^#\s*SPDX-License-Identifier:\s*(.*)$")
PATCHED_RE = re.compile(r"^#\s*patched:\s*(.*)$")
# REUSE-IgnoreEnd
REPEATED_YEAR_RE = re.compile(r"^(\d{4})(?:[,\s]+\1)+(\s.*)?$")

PROJECT_HOLDER = "ExploreMaths"
PROJECT_COPYRIGHT = "2026 ExploreMaths"
DEFAULT_LICENSE = "MIT"


@dataclass
class Header:
    """Parsed (and possibly malformed) leading comment block."""

    start: int
    end: int
    copyrights: list[str] = field(default_factory=list)
    licenses: list[str] = field(default_factory=list)
    patched: list[str] = field(default_factory=list)
    extras: list[str] = field(default_factory=list)

    @property
    def exists(self) -> bool:
        return bool(self.copyrights or self.licenses or self.patched)


def _is_spdx_line(line: str) -> bool:
    stripped = line.strip()
    return bool(
        COPYRIGHT_RE.match(stripped)
        or LICENSE_RE.match(stripped)
        or PATCHED_RE.match(stripped)
    )


def _split_header(lines: list[str]) -> Header:
    """Locate the leading SPDX region.

    The region may contain blank or bare ``#`` separators; they are part of
    the header only when the next meaningful line is another SPDX line.  A
    plain comment (for example a vendored-upstream note) ends the region.
    """
    start = 1 if lines and lines[0].startswith("#!") else 0
    end = start
    index = start
    while index < len(lines):
        stripped = lines[index].strip()
        if stripped.startswith("#") and stripped != "#":
            if _is_spdx_line(lines[index]):
                end = index + 1
                index += 1
                continue
            break
        if stripped in ("", "#"):
            lookahead = index
            while lookahead < len(lines) and lines[lookahead].strip() in ("", "#"):
                lookahead += 1
            if lookahead < len(lines) and _is_spdx_line(lines[lookahead]):
                end = lookahead
                index = lookahead
                continue
            break
        break
    return Header(start, end)


def _parse(lines: list[str]) -> Header:
    header = _split_header(lines)
    for line in lines[header.start:header.end]:
        stripped = line.strip()
        copyright_match = COPYRIGHT_RE.match(stripped)
        license_match = LICENSE_RE.match(stripped)
        patched_match = PATCHED_RE.match(stripped)
        if copyright_match:
            header.copyrights.append(" ".join(copyright_match.group(1).split()))
        elif license_match:
            header.licenses.append(" ".join(license_match.group(1).split()))
        elif patched_match:
            header.patched.append(" ".join(patched_match.group(1).split()))
        elif stripped not in ("", "#"):
            header.extras.append(line)
    return header


def _normalize_copyright(text: str) -> str:
    match = REPEATED_YEAR_RE.match(text)
    if match:
        rest = (match.group(2) or "").strip()
        return f"{match.group(1)} {rest}".strip() if rest else match.group(1)
    return text


def _canonical_copyrights(copyrights: list[str]) -> list[str]:
    ordered: list[str] = []
    project: list[str] = []
    for entry in copyrights:
        normalized = _normalize_copyright(entry)
        target = project if PROJECT_HOLDER in normalized else ordered
        if normalized not in target:
            target.append(normalized)
    return ordered + project


def _build_header(header: Header) -> list[str]:
    copyrights = _canonical_copyrights(header.copyrights) or [PROJECT_COPYRIGHT]
    license_id = header.licenses[0] if header.licenses else DEFAULT_LICENSE
    # REUSE-IgnoreStart
    lines = [f"# SPDX-FileCopyrightText: {entry}" for entry in copyrights]
    lines.append(f"# SPDX-License-Identifier: {license_id}")
    lines.extend(f"# patched: {reason}" for reason in dict.fromkeys(header.patched))
    # REUSE-IgnoreEnd
    lines.extend(header.extras)
    return lines


def _issues(header: Header, lines: list[str]) -> list[str]:
    issues: list[str] = []
    if not header.exists:
        has_spdx = any(
            "SPDX-" in line for line in lines[:20]
        )
        return ["header-not-at-top"] if has_spdx else ["missing-header"]
    if not header.copyrights:
        issues.append("missing-copyright")
    if not header.licenses:
        issues.append("missing-license")
    if len(header.licenses) > 1:
        if len(set(header.licenses)) > 1:
            issues.append("conflicting-license")
        else:
            issues.append("duplicate-license")

    raw_block = lines[header.start:header.end]
    if any(line.strip() == "#" for line in raw_block):
        issues.append("blank-comment-in-header")

    normalized = [_normalize_copyright(entry) for entry in header.copyrights]
    if len(normalized) != len(set(normalized)):
        issues.append("duplicate-copyright")
    if any(REPEATED_YEAR_RE.match(entry) for entry in header.copyrights):
        issues.append("copyright-year-repeated")

    license_index = next(
        (i for i, line in enumerate(raw_block) if LICENSE_RE.match(line.strip())),
        None,
    )
    patched_indices = [
        i for i, line in enumerate(raw_block) if PATCHED_RE.match(line.strip())
    ]
    if license_index is not None and patched_indices:
        if min(patched_indices) < license_index:
            issues.append("patched-before-license")
    if header.end < len(lines) and lines[header.end].strip():
        issues.append("missing-blank-after-header")
    elif (
        header.end + 1 < len(lines)
        and not lines[header.end + 1].strip()
    ):
        issues.append("extra-blank-after-header")
    return issues


def _python_files() -> list[Path]:
    try:
        listed = subprocess.run(
            ["git", "ls-files", "*.py"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.split()
    except (OSError, subprocess.CalledProcessError):
        listed = []
    if listed:
        return [ROOT / name for name in listed]
    return sorted(ROOT.rglob("*.py"))


def _read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def _apply_fix(path: Path, lines: list[str], header: Header) -> bool:
    prefix = lines[:header.start]
    rest = lines[header.end:]
    while rest and not rest[0].strip():
        rest.pop(0)
    new_lines = prefix + _build_header(header)
    if rest:
        new_lines.append("")
        new_lines.extend(rest)
    if new_lines == lines:
        return False
    path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fix", action="store_true", help="rewrite headers in place")
    args = parser.parse_args()

    checked = 0
    failures: list[tuple[Path, list[str]]] = []
    fixed = 0

    for path in _python_files():
        lines = _read_lines(path)
        header = _parse(lines)
        issues = _issues(header, lines)
        checked += 1

        if issues and args.fix and "conflicting-license" not in issues:
            if _apply_fix(path, lines, header):
                fixed += 1
            lines = _read_lines(path)
            issues = _issues(_parse(lines), lines)

        if issues:
            failures.append((path, issues))

    if failures:
        print(f"FAIL  headers  {len(failures)} file(s) of {checked}\n")
        for path, issues in failures:
            rel = path.relative_to(ROOT)
            print(f"  {rel}: {', '.join(issues)}")
        print(f"\nTotal: {len(failures)} file(s) with header issues")
        return 1

    suffix = f" ({fixed} fixed)" if fixed else ""
    print(f"PASS  headers  {checked} files scanned{suffix}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

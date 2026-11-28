# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Require a documented reason for every explicit ``Any`` annotation.

Runs ``mypy --disallow-any-explicit`` and treats each finding as an error
unless the source line carries ``# explicit-any-ok: <reason>``.  This keeps
unavoidable dynamic boundaries auditable instead of hiding them in a
baseline: the exception is visible at the exact annotation it applies to.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ERROR_RE = re.compile(
    r'^(?P<path>.+?):(?P<line>\d+): error: Explicit "Any" is not allowed'
)
EXCUSE_RE = re.compile(r"#\s*explicit-any-ok:\s*\S+")


def _source_line(root: Path, path: str, line: int) -> str:
    """Read the source line a mypy finding points at."""
    source_path = Path(path)
    if not source_path.is_absolute():
        source_path = root / source_path
    return source_path.read_text(encoding="utf-8").splitlines()[line - 1]


def _source_lines(root: Path, path: str) -> list[str]:
    """Read all lines of a finding's source file."""
    source_path = Path(path)
    if not source_path.is_absolute():
        source_path = root / source_path
    return source_path.read_text(encoding="utf-8").splitlines()


def _statement_block(lines: list[str], line: int) -> list[str]:
    """Collect the logical statement starting at ``line``.

    Multi-line signatures put ``**kwargs: Any`` on an inner line while mypy
    reports the ``def`` line.  Scanning to the closing colon lets the documented
    reason sit on the annotation it explains rather than on the ``def``.
    """
    block: list[str] = []
    depth = 0
    for index in range(line - 1, min(line + 40, len(lines))):
        current = lines[index]
        block.append(current)
        depth += current.count("(") + current.count("[") + current.count("{")
        depth -= current.count(")") + current.count("]") + current.count("}")
        if depth <= 0 and current.rstrip().endswith(":"):
            break
    return block


def _block_is_excused(block: list[str]) -> bool:
    """Accept one documented reason for a multi-line statement.

    Black may move a trailing comment from the ``def`` line to the closing
    parenthesis, so the reason is attached to the logical statement rather
    than to a fixed line.
    """
    any_lines = [entry for entry in block if re.search(r"\bAny\b", entry)]
    return bool(any_lines) and any(EXCUSE_RE.search(entry) for entry in block)


def parse_output(root: Path, output: str) -> tuple[list[str], list[str]]:
    """Split explicit-``Any`` findings into violations and documented lines."""
    violations: list[str] = []
    excused: list[str] = []
    seen: set[tuple[str, int]] = set()
    cache: dict[str, list[str]] = {}
    for line in output.splitlines():
        match = ERROR_RE.match(line)
        if match is None:
            continue
        path = match.group("path")
        number = int(match.group("line"))
        if (path, number) in seen:
            continue
        seen.add((path, number))
        lines = cache.setdefault(path, _source_lines(root, path))
        block = _statement_block(lines, number)
        location = f"{path}:{number}"
        any_lines = [entry for entry in block if re.search(r"\bAny\b", entry)]
        if not any_lines:
            # mypy can report an inherited alias at the ``def`` line even though
            # the statement itself contains no explicit Any.
            excused.append(f"{location}: {lines[number - 1].strip()}")
        elif EXCUSE_RE.search(lines[number - 1]) or _block_is_excused(block):
            excused.append(f"{location}: {lines[number - 1].strip()}")
        else:
            violations.append(f"{location}: {lines[number - 1].strip()}")
    return violations, excused


def run_mypy(root: Path, package: Path) -> tuple[int, str]:
    """Run the strict explicit-``Any`` pass from the project root."""
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "mypy",
            "--disallow-any-explicit",
            str(package),
        ],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.returncode, completed.stdout + completed.stderr


def main(argv: list[str] | None = None) -> int:
    """Fail when any explicit ``Any`` lacks a documented reason."""
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--package", type=Path)
    args = parser.parse_args(argv)

    root = args.root.resolve()
    package = args.package or root / "manim_extensions"
    exit_code, output = run_mypy(root, package)
    if exit_code not in (0, 1):
        print(output, end="")
        return exit_code

    violations, excused = parse_output(root, output)
    if violations:
        print("Explicit Any without `# explicit-any-ok: <reason>`:\n")
        for entry in violations:
            print(entry)
        print(f"\n{len(violations)} undocumented explicit Any finding(s).")
        return 1

    print(
        f"PASS explicit Any policy: {len(excused)} documented exception(s), "
        "no undocumented Any."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

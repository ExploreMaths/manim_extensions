# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Check class and function naming across the package code.

Rules:

* classes are PascalCase (``^[A-Z][A-Za-z0-9]*$``) with no underscore;
* functions and methods are snake_case (``^_*[a-z][a-z0-9_]*$``), which
  permits private and dunder names;
* names in every package file are checked, including vendored packages.

Usage:
    python workflow/validate_naming.py
    python workflow/validate_naming.py --root .
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path

from _context import ROOT

sys.path.insert(0, str(Path(__file__).resolve().parent))

CLASS_RE = re.compile(r"[A-Z][A-Za-z0-9]*$")
FUNCTION_RE = re.compile(r"_*[a-z][a-z0-9_]*$")


def scan_file(path: Path) -> list[tuple[int, str, str]]:
    """Return ``(line, kind, name)`` for every invalid definition."""
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    problems: list[tuple[int, str, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if not CLASS_RE.fullmatch(node.name):
                problems.append((node.lineno, "class", node.name))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not FUNCTION_RE.fullmatch(node.name):
                problems.append((node.lineno, "function", node.name))
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="repository root (default: the checkout containing this script)",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    package_dir = root / "manim_extensions"

    problems: list[tuple[Path, int, str, str]] = []
    class_count = function_count = 0
    for path in sorted(package_dir.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        source_tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(source_tree):
            if isinstance(node, ast.ClassDef):
                class_count += 1
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                function_count += 1
        for line, kind, name in scan_file(path):
            problems.append((path, line, kind, name))

    if problems:
        print(f"FAIL  naming  {len(problems)} invalid name(s)")
        for path, line, kind, name in problems:
            print(f"  {path.relative_to(root)}:{line}: {kind} {name!r}")
        return 1

    print(
        "PASS  naming  " f"{class_count} classes and {function_count} functions checked"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

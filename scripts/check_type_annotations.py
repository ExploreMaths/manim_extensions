#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Check that all function parameters in the codebase have type annotations.

This script is designed to be run in CI. It scans all Python files in the
``manim_extensions`` package (excluding ``__init__.py`` and vendored assets)
and reports any function or method parameter that lacks a type annotation.

Usage::

    python scripts/check_type_annotations.py

Exit code 0 means all parameters are annotated; exit code 1 means at least
one parameter is missing an annotation.

Excluded by default (conventionally left unannotated):
  - ``self`` and ``cls`` (first parameter of methods / classmethods)
  - ``*args`` and ``**kwargs`` (variadic parameters)
  - Files matching ``__init__.py`` (re-export modules)
  - Files under ``fontawesome/`` (vendored icon assets)
  - Test files (``test_*.py``, ``*_test.py``)
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

SKIP_FILENAMES = {"__init__.py"}
SKIP_DIR_PARTS = {"fontawesome", "__pycache__", "tests", "docs", "build"}


def should_skip(path: Path) -> bool:
    """Return *True* if *path* should be skipped during scanning."""
    if path.name in SKIP_FILENAMES:
        return True
    if "test" in path.name.lower():
        return True
    for part in path.parts:
        if part in SKIP_DIR_PARTS:
            return True
    return False


def get_unannotated_params(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    """Return names of parameters on *node* that lack a type annotation.

    ``self``, ``cls``, ``*args`` and ``**kwargs`` are never reported.
    """
    unannotated: list[str] = []

    all_args: list[ast.arg] = []
    all_args.extend(node.args.posonlyargs)
    all_args.extend(node.args.args)

    for arg in all_args:
        if arg.arg in ("self", "cls"):
            continue
        if arg.annotation is None:
            unannotated.append(arg.arg)

    # keyword-only args
    for arg in node.args.kwonlyargs:
        if arg.annotation is None:
            unannotated.append(arg.arg)

    # *args and **kwargs are conventionally left unannotated
    return unannotated


def scan_file(path: Path) -> list[dict]:
    """Scan a single Python file. Return a list of violation dicts."""
    results: list[dict] = []
    try:
        source = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return results

    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return results

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            missing = get_unannotated_params(node)
            if missing:
                results.append(
                    {
                        "file": str(path.relative_to(REPO_ROOT)),
                        "line": node.lineno,
                        "function": node.name,
                        "params": missing,
                    }
                )
    return results


def main() -> int:
    package_dir = REPO_ROOT / "manim_extensions"
    all_violations: list[dict] = []
    files_scanned = 0

    for py_file in sorted(package_dir.rglob("*.py")):
        if should_skip(py_file):
            continue
        files_scanned += 1
        all_violations.extend(scan_file(py_file))

    if not all_violations:
        print(f"OK: all function parameters are annotated ({files_scanned} files scanned)")
        return 0

    print(f"FAIL: {len(all_violations)} function(s) with unannotated parameters "
          f"across {files_scanned} files:\n")
    for v in all_violations:
        params = ", ".join(v["params"])
        print(f"  {v['file']}:{v['line']}  {v['function']}({params})")

    print(f"\nTotal: {len(all_violations)} violation(s)")
    return 1


if __name__ == "__main__":
    sys.exit(main())

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Reject CJK characters inside Python docstrings.

The public documentation is written in English.  Vendored modules occasionally
carry translated prose, full-width punctuation or CJK comments promoted to
docstrings, which neither Sphinx nor downstream readers can consume consistently.
This check is AST-based: module, class, method and function docstrings are
scanned, while ordinary string literals and comments are left alone.

A violation reports the file, the qualified name and the first offending line.

Usage:
    python validate_english_docstrings.py
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

from _context import SRC

SKIP_DIRS = {"__pycache__", ".git", "build", "docs", "tests", "workflow"}

CJK_RE = re.compile(
    "[\u2e80-\u2eff\u3000-\u303f\u3040-\u30ff\u3100-\u312f"
    "\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff00-\uffef]"
)


def iter_docstrings(node, prefix=""):
    """Yield ``(qualname, lineno, docstring)`` for every documented node."""
    if isinstance(
        node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
    ):
        doc = ast.get_docstring(node, clean=False)
        if doc is not None:
            name = prefix.rstrip(".") or "<module>"
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                name = f"{prefix}{node.name}"
            yield name, getattr(node, "lineno", 1), doc
    for child in ast.iter_child_nodes(node):
        child_prefix = prefix
        if isinstance(node, ast.ClassDef):
            child_prefix = f"{prefix}{node.name}."
        yield from iter_docstrings(child, child_prefix)


def main() -> int:
    """Scan the package and fail on the first CJK docstring."""
    violations = []
    for path in sorted(SRC.rglob("*.py")):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError as exc:
            violations.append((path, 0, f"syntax error: {exc}"))
            continue
        for qualname, lineno, doc in iter_docstrings(tree):
            match = CJK_RE.search(doc)
            if match is None:
                continue
            line = match.group(0)
            violations.append(
                (path, lineno, f"{qualname}: non-English character {line!r}")
            )

    if not violations:
        print("PASS  english-docstrings")
        return 0

    rel = SRC.parent
    for path, lineno, message in violations:
        print(f"{path.relative_to(rel)}:{lineno}: {message}")
    print(f"\nFAIL  {len(violations)} CJK docstring violation(s)")
    return 1


if __name__ == "__main__":
    sys.exit(main())

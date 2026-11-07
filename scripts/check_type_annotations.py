# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Check that all function parameters in the codebase have type annotations.

This script is designed to be run in CI. It scans all Python files in the
``manim_extensions`` package (excluding vendored assets) and reports any
function or method parameter that lacks a type annotation, plus any type
annotation written as a string literal (``node: "Node"``). Quoted annotations
are rejected: importing the name (or adding ``from __future__ import
annotations`` for a genuine forward reference) keeps the type discoverable.
``Literal["a", "b"]`` payloads are string *values*, not annotations, and are
accepted.  Functions defined in ``__init__.py`` are checked too: a package
initialiser may expose public helpers of its own (re-exported imports are
not function definitions, so they are never flagged).

Usage::

    python scripts/check_type_annotations.py

Exit code 0 means all parameters are annotated; exit code 1 means at least
one parameter is missing an annotation.

Excluded by default (conventionally left unannotated):
  - ``self`` and ``cls`` (first parameter of methods / classmethods)
  - ``*args`` and ``**kwargs`` (variadic parameters)
  - Files under ``fontawesome/`` (vendored icon assets)
  - Test files (``test_*.py``, ``*_test.py``)
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

SKIP_DIR_PARTS = {"fontawesome", "__pycache__", "tests", "docs", "build"}


def should_skip(path: Path) -> bool:
    """Return *True* if ``path`` should be skipped during scanning."""
    if "test" in path.name.lower():
        return True
    for part in path.parts:
        if part in SKIP_DIR_PARTS:
            return True
    return False


def get_unannotated_params(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    """Return names of parameters on ``node`` that lack a type annotation.

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


def _quoted_parts(annotation: ast.expr) -> list[str]:
    """Return the string literals used inside ``annotation``.

    ``Literal["a", "b"]`` payloads are legitimate string values, so their
    subscript is not descended into.
    """
    if isinstance(annotation, ast.Constant):
        return [annotation.value] if isinstance(annotation.value, str) else []
    if isinstance(annotation, ast.Subscript):
        if isinstance(annotation.value, ast.Name) and annotation.value.id == "Literal":
            return []
        return _quoted_parts(annotation.slice)
    found: list[str] = []
    for child in ast.iter_child_nodes(annotation):
        if isinstance(child, ast.expr):
            found.extend(_quoted_parts(child))
    return found


def get_quoted_annotations(node) -> list[tuple[int, str, str]]:
    """Return ``(line, label, text)`` for every quoted annotation on ``node``.

    Quoted annotations such as ``def f(node: "Node")`` hide the real type
    from tooling and force readers to guess where the name lives; the
    project requires a real import instead.
    """
    findings: list[tuple[int, str, str]] = []
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        if node.returns is not None:
            for text in _quoted_parts(node.returns):
                findings.append((node.lineno, "return", text))
        for arg in (node.args.posonlyargs + node.args.args + node.args.kwonlyargs):
            if arg.annotation is not None:
                for text in _quoted_parts(arg.annotation):
                    findings.append((arg.lineno, arg.arg, text))
    elif isinstance(node, ast.AnnAssign) and node.annotation is not None:
        target = node.target.id if isinstance(node.target, ast.Name) else "<attribute>"
        for text in _quoted_parts(node.annotation):
            findings.append((node.lineno, target, text))
    return findings


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
                        "kind": "missing",
                        "file": str(path.relative_to(REPO_ROOT)),
                        "line": node.lineno,
                        "function": node.name,
                        "params": missing,
                    }
                )
        for line, label, text in get_quoted_annotations(node):
            results.append(
                {
                    "kind": "quoted",
                    "file": str(path.relative_to(REPO_ROOT)),
                    "line": line,
                    "label": label,
                    "text": text,
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
        print(f"OK: annotations are unquoted and all parameters annotated "
              f"({files_scanned} files scanned)")
        return 0

    print(f"FAIL: {len(all_violations)} violation(s) across {files_scanned} files:\n")
    for v in all_violations:
        if v["kind"] == "missing":
            params = ", ".join(v["params"])
            print(f"  {v['file']}:{v['line']}  unannotated {v['function']}({params})")
        else:
            print(f"  {v['file']}:{v['line']}  quoted annotation "
                  f"{v['label']}: \"{v['text']}\" (import the name instead)")

    print(f"\nTotal: {len(all_violations)} violation(s)")
    return 1


if __name__ == "__main__":
    sys.exit(main())

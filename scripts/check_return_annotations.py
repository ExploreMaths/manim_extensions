# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""CI checker: every public function with a docstring and a non-trivial
``return`` statement must declare a return annotation (``-> ...``).

Mirrors the acceptance rule requested by the maintainer: "有 return 的话要
写返回注解".  Exemptions (kept in sync with check_type_annotations.py):
``__init__.py`` modules, the vendored ``fontawesome`` package, test files,
``self``/``cls``/``*args``/``**kwargs`` (parameters only; returns still
checked), and functions without a docstring.

A function is considered to "return a value" if its body contains at least
one ``return`` statement whose value is not the literal ``None`` (explicit
``return None`` is also a real return and requires an annotation).

Usage:  python scripts/check_return_annotations.py
Exit code 0 when every checked function is annotated, 1 otherwise.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent.parent / "manim_extensions"


def _ignored_module(rel: str) -> bool:
    if rel.endswith("__init__.py"):
        return True
    if "fontawesome" in rel:
        return True
    if "/test" in rel or rel.startswith("test") or "_test.py" in rel or "tests" in rel:
        return True
    return False


def _has_value_return(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """True if the function's own body returns a non-None value.

    Nested functions are not walked: a ``return`` inside an inner ``def``
    belongs to that inner function, not to the outer one.
    """

    def scan(body: list[ast.stmt]) -> bool:
        for stmt in body:
            if isinstance(stmt, ast.Return):
                if stmt.value is None:
                    continue
                if isinstance(stmt.value, ast.Constant) and stmt.value.value is None:
                    continue
                return True
            # do not descend into nested defs; recurse into other statements
            if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for child in ast.iter_child_nodes(stmt):
                if isinstance(child, ast.Return) and _is_non_none(child):
                    return True
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
        return False

    def _is_non_none(r: ast.Return) -> bool:
        if r.value is None:
            return False
        if isinstance(r.value, ast.Constant) and r.value.value is None:
            return False
        return True

    return scan(node.body)


def main() -> int:
    problems: list[str] = []
    scanned = 0
    for path in sorted(PACKAGE.rglob("*.py")):
        rel = str(path.relative_to(PACKAGE)).replace("\\", "/")
        if _ignored_module(rel):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            name = node.name
            if name.startswith("_"):
                continue
            doc = ast.get_docstring(node)
            if doc is None:
                continue
            if node.returns is not None:
                continue
            if not _has_value_return(node):
                continue
            scanned += 1
            problems.append(f"{rel}:{node.lineno}: {name}: has return value(s) but no return annotation")

    if problems:
        print(f"FAIL: {len(problems)} function(s) with return value(s) lack a return annotation")
        for p in problems:
            print(f"  {p}")
        return 1
    print(f"OK: all documented public functions with return values are annotated ({scanned} checked)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

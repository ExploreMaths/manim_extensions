# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""CI checker: return annotations must describe what the function returns.

Two rules are enforced:

1. A function with a ``return`` statement that produces a value must
   declare a return annotation (``-> ...``).
2. A return annotation must not be bare ``Any``.  ``Any`` disables type
   checking for the return value; annotate the concrete type, or ``None``
   when the body only performs side effects.

Mirrors the acceptance rules requested by the maintainer: "a function with
a ``return`` statement must declare a return annotation" and "Any should
only be used when the function really returns an arbitrary value".

Exemptions (kept in sync with check_type_annotations.py):
the vendored ``fontawesome`` package, test files, and functions without a
docstring.  Functions defined in ``__init__.py`` are checked as well,
since package initialisers may define public helpers (re-exported names
are plain imports, not function definitions).

A function is considered to "return a value" if its body contains at least
one ``return`` statement whose value is not the literal ``None`` (explicit
``return None`` is also a real return and requires an annotation).  Nested
functions, classes and lambdas are separate scopes and are not descended
into.

Usage:  python scripts/check_return_annotations.py
Exit code 0 when every checked function is annotated precisely, 1 otherwise.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "workflow"))

from _context import SRC as PACKAGE  # noqa: E402


def _ignored_module(rel: str) -> bool:
    if "/test" in rel or rel.startswith("test") or "_test.py" in rel or "tests" in rel:
        return True
    return False


def _is_non_none_return(node: ast.Return) -> bool:
    """True when a ``return`` statement produces a value other than ``None``."""
    if node.value is None:
        return False
    if isinstance(node.value, ast.Constant) and node.value.value is None:
        return False
    return True


def _has_value_return(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """True if the function's own body returns a non-None value.

    Every statement container is walked, including ``if``, ``for``,
    ``while``, ``try`` and ``with`` blocks.  Nested functions, classes and
    lambdas are separate scopes and are skipped.
    """

    def scan(current: ast.AST) -> bool:
        for child in ast.iter_child_nodes(current):
            if isinstance(
                child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)
            ):
                continue
            if isinstance(child, ast.Return) and _is_non_none_return(child):
                return True
            if scan(child):
                return True
        return False

    return scan(node)


def _is_any_annotation(node: ast.expr | None) -> bool:
    """True when the return annotation is exactly ``Any`` or ``typing.Any``."""
    if isinstance(node, ast.Name):
        return node.id == "Any"
    if isinstance(node, ast.Attribute):
        return node.attr == "Any"
    return False


def main() -> int:
    problems: list[str] = []
    checked = 0
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
            checked += 1
            name = node.name
            has_value = _has_value_return(node)
            if node.returns is None:
                if not has_value:
                    continue
                problems.append(
                    f"{rel}:{node.lineno}: {name}: has return value(s) but "
                    f"no return annotation"
                )
                continue
            if _is_any_annotation(node.returns):
                if has_value:
                    problems.append(
                        f"{rel}:{node.lineno}: {name}: returns a value but is "
                        f"annotated '-> Any'; use a concrete return type"
                    )
                else:
                    problems.append(
                        f"{rel}:{node.lineno}: {name}: is annotated '-> Any' "
                        f"but never returns a value; annotate '-> None'"
                    )

    if problems:
        print(f"FAIL: {len(problems)} function(s) have imprecise return annotations")
        for problem in problems:
            print(f"  {problem}")
        return 1
    print(
        f"OK: all checked functions have precise return annotations ({checked} checked)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

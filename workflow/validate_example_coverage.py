# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Require rendered examples for every public function that returns visuals.

A public function whose return annotation mentions a Manim mobject, animation,
scene, or a group of those is part of the visual API.  Such a function must
document an ``Examples`` section containing at least one ``.. manim::``
directive.  Methods may rely on the same coverage in their enclosing class
docstring, because a class-level example normally exercises its methods.

Usage:
    python workflow/validate_example_coverage.py
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

from _context import PACKAGE_DIR, ROOT

VISUAL_NAMES = re.compile(
    r"\w*(?:"
    r"Mobject|VMobject|Animation|Scene|"
    r"VGroup|Group|Table|Axes|Surface|"
    r"Text|MarkupText|Tex|MathTex|"
    r"Arrow|Line|Circle|Square|Rectangle|"
    r"ImageMobject|OpenGL\w*"
    r")\b"
)


def is_public(name: str) -> bool:
    """Return whether *name* is part of the public API."""
    return not name.startswith("_")


def is_visual(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Return whether *node* has a visual return annotation."""
    if node.returns is None:
        return False
    return VISUAL_NAMES.search(ast.unparse(node.returns)) is not None


def has_rendered_example(node: ast.AST) -> bool:
    """Return whether *node* documents an example with a manim directive."""
    docstring = ast.get_docstring(node) or ""
    return "Examples" in docstring and ".. manim::" in docstring


def scan(path: Path) -> list[str]:
    """Return missing-example violations in one Python file."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    violations: list[str] = []

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if (
                is_public(node.name)
                and is_visual(node)
                and not has_rendered_example(node)
            ):
                violations.append(
                    f"{path.relative_to(ROOT)}:{node.lineno}: "
                    f"`{node.name}` returns a visual and needs Examples + .. manim::"
                )
        elif isinstance(node, ast.ClassDef):
            class_example = has_rendered_example(node)
            for method in node.body:
                if not isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                if not is_public(method.name) or not is_visual(method):
                    continue
                if has_rendered_example(method) or class_example:
                    continue
                violations.append(
                    f"{path.relative_to(ROOT)}:{method.lineno}: "
                    f"`{node.name}.{method.name}` returns a visual and needs "
                    "Examples + .. manim:: on the method or its class"
                )

    return violations


def iter_sources() -> list[Path]:
    """Collect package sources covered by the rule."""
    return sorted(PACKAGE_DIR.rglob("*.py"))


def main() -> int:
    violations: list[str] = []
    checked = 0
    for path in iter_sources():
        if "__pycache__" in path.parts:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if is_public(node.name) and is_visual(node):
                    checked += 1
            elif isinstance(node, ast.ClassDef):
                for method in node.body:
                    if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if is_public(method.name) and is_visual(method):
                            checked += 1
        violations.extend(scan(path))

    if violations:
        print(
            "Every public visual function needs an Examples section with a "
            ".. manim:: directive, on the function or its class.",
            file=sys.stderr,
        )
        for violation in violations:
            print(f"  {violation}", file=sys.stderr)
        print(f"Found {len(violations)} violation(s).", file=sys.stderr)
        return 1

    print(f"Visual functions with rendered examples: complete ({checked} checked).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

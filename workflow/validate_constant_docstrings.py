# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Validate that every public module and class constant carries a description.

The reference manual documents constants through ``autodoc_all``'s ``data``
classification under its ``Constants`` sections.  The project convention is
to document a constant with a ``#:`` comment block immediately above the
assignment; ``autodoc_all`` reads those ``#:`` lines as the entry
description, the same way a docstring documents a class or function.  A
bare string-literal statement trailing the assignment is also accepted as
the constant description.

Class-scope constants are checked too: every public all-uppercase class
assignment needs its own ``#:`` description.  Instance attributes and
configuration fields whose names are not all-uppercase remain documented by
the class docstring instead.

Exempt names:

* dunder and leading-underscore private names;
* ``__all__`` and other re-exported module names;
* type aliases (``Subscript``, ``X | Y``, ``TypeAlias`` /
  ``TypeAliasType`` calls) and TypeVar / ParamSpec / TypeVarTuple
  parameters;
* re-exported aliases whose value is a bare name or attribute;
* names the runtime classifies as a class, function, or type alias, and
  submodules bound at module level.

Usage:
    python validate_constant_docstrings.py
"""

import argparse
import ast
import importlib
import pkgutil
import sys
import types
from pathlib import Path

from _context import PACKAGE, ROOT, SRC

sys.path.insert(0, str(SRC.parent))
sys.path.insert(0, str(ROOT / "docs" / "source" / "_extensions"))

from autodoc_all import classify  # noqa: E402

DOCS_TOOLS = {"docbuild", "testing", "custom_mobjects", "__pycache__"}

# Calls that build a type alias or a type-parameter variable rather than a
# data constant.
ALIAS_CALL_NAMES = {
    "TypeAlias",
    "TypeAliasType",
    "TypeVar",
    "ParamSpec",
    "TypeVarTuple",
}


def is_alias_expression(value: ast.AST | None) -> bool:
    """Return whether an assignment value is a type alias or type variable."""
    if value is None:
        return True
    if isinstance(value, ast.Subscript):
        return True
    if isinstance(value, ast.BinOp) and isinstance(value.op, ast.BitOr):
        return True
    if isinstance(value, ast.Call):
        func = value.func
        if isinstance(func, ast.Name) and func.id in ALIAS_CALL_NAMES:
            return True
    return isinstance(value, (ast.Name, ast.Attribute))


def preceding_hashdoc(lines: list[str], lineno: int) -> bool:
    """Return whether the assignment at *lineno* has a ``#:`` description.

    The nearest non-blank line above the assignment must be a ``#:``
    comment carrying non-empty text.  A contiguous block of ``#:`` lines is
    accepted, matching :func:`autodoc_all.alias_definition`.
    """
    index = lineno - 2
    while index >= 0:
        stripped = lines[index].strip()
        if stripped == "":
            index -= 1
            continue
        if not stripped.startswith("#:"):
            return False
        return stripped[2:].strip() != ""
    return False


def trailing_docstring(body: list[ast.stmt], node: ast.stmt) -> bool:
    """Return whether *node* is followed by a bare string-literal docstring.

    Some constants document themselves with a trailing triple-quoted
    string statement instead of a ``#:`` comment; that bare string expression
    counts as the constant description.
    """
    try:
        index = body.index(node)
    except ValueError:
        return False
    if index + 1 >= len(body):
        return False
    nxt = body[index + 1]
    if not (isinstance(nxt, ast.Expr) and isinstance(nxt.value, ast.Constant)):
        return False
    return isinstance(nxt.value.value, str) and nxt.value.value.strip() != ""


def constant_assignments(
    tree: ast.Module,
) -> list[tuple[str, ast.AnnAssign | ast.Assign]]:
    """Return ``(name, node)`` for every public top-level assignment target."""
    found: list[tuple[str, ast.AnnAssign | ast.Assign]] = []
    for node in tree.body:
        targets: list[str] = []
        if isinstance(node, ast.Assign):
            targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            targets = [node.target.id]
        else:
            continue
        for name in targets:
            found.append((name, node))
    return found


def check_module(module: types.ModuleType) -> list[tuple[int, str]]:
    """Return ``(line, name)`` for constants in *module* missing a ``#:`` doc."""
    path = getattr(module, "__file__", None)
    if not path or not str(path).endswith(".py"):
        return []
    try:
        source = Path(path).read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (OSError, SyntaxError, UnicodeDecodeError):
        return []

    lines = source.splitlines()
    missing: list[tuple[int, str]] = []
    for name, node in constant_assignments(tree):
        if name.startswith("_"):
            continue
        if name == "__all__":
            continue
        value = node.value if isinstance(node, (ast.Assign, ast.AnnAssign)) else None
        if value is None:
            continue
        if is_alias_expression(value):
            continue
        obj = getattr(module, name, None)
        if isinstance(obj, types.ModuleType):
            continue
        if classify(obj) in {"class", "function", "typealias"}:
            continue
        documented = preceding_hashdoc(lines, node.lineno) or trailing_docstring(
            tree.body, node
        )
        if not documented:
            missing.append((node.lineno, name))
    missing.extend(check_class_constants(tree, lines))
    return missing


def check_class_constants(tree: ast.Module, lines: list[str]) -> list[tuple[int, str]]:
    """Return ``(line, name)`` for public uppercase class constants missing docs."""
    missing: list[tuple[int, str]] = []
    for cls in (node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)):
        for node in cls.body:
            targets: list[str] = []
            if isinstance(node, ast.Assign):
                targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                targets = [node.target.id]
            else:
                continue
            for name in targets:
                if name.startswith("_") or not name.isupper():
                    continue
                documented = preceding_hashdoc(
                    lines, node.lineno
                ) or trailing_docstring(cls.body, node)
                if not documented:
                    missing.append((node.lineno, f"{cls.name}.{name}"))
    return missing


def iter_modules():
    """Yield every importable submodule of the package, skipping tool dirs."""
    for info in pkgutil.walk_packages([str(SRC)], f"{PACKAGE}."):
        if any(part in DOCS_TOOLS for part in info.name.split(".")):
            continue
        if info.name.endswith(".__main__"):
            continue
        try:
            yield importlib.import_module(info.name)
        except Exception:
            continue


def main() -> int:
    """Main validation function."""
    argparse.ArgumentParser(description=__doc__).parse_args()

    failures: list[tuple[Path, int, str]] = []
    checked = 0
    for module in iter_modules():
        path = Path(getattr(module, "__file__", "") or "")
        if not str(path).endswith(".py"):
            continue
        checked += 1
        for lineno, name in check_module(module):
            failures.append((path, lineno, name))

    if failures:
        print(f"FAIL  constant-docstrings  {len(failures)} issue(s)\n")
        for path, lineno, name in sorted(failures, key=lambda f: (str(f[0]), f[1])):
            rel = path.relative_to(ROOT)
            print(
                f"  {rel}:{lineno}  missing-constant-docstring: "
                f"constant '{name}' has no '#:' description"
            )
        print(f"\nTotal: {len(failures)} issue(s)")
        return 1

    print(f"PASS  constant-docstrings  {checked} modules scanned")
    return 0


if __name__ == "__main__":
    sys.exit(main())

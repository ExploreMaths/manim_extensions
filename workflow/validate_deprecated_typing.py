# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Reject deprecated ``typing`` aliases in source and documentation code.

PEP 585 made the parametrised aliases in :mod:`typing` redundant: ``list``,
``dict``, ``tuple``, ``set`` and ``type`` are subscriptable at runtime, and
the collections counterparts live in :mod:`collections.abc`.  The aliases
still import successfully, so a normal test run does not catch new uses.

This checker walks the package, tests, repository scripts, workflow tools,
and Sphinx extensions with the AST and reports every deprecated name in a
``from typing import ...`` statement or a ``typing.List``-style attribute.
Strings and comments are not inspected, so prose may still mention the old
names while explaining the rule.

Usage:
    python workflow/validate_deprecated_typing.py
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

from _context import PACKAGE_DIR, ROOT

# PEP 585 aliases.  Keep this list in sync with
# https://docs.python.org/3/library/typing.html#deprecated-aliases
DEPRECATED = {
    "AbstractSet",
    "AsyncContextManager",
    "AsyncGenerator",
    "AsyncIterable",
    "AsyncIterator",
    "Awaitable",
    "ByteString",
    "Callable",
    "ChainMap",
    "Collection",
    "Container",
    "ContextManager",
    "Coroutine",
    "Counter",
    "DefaultDict",
    "Deque",
    "Dict",
    "FrozenSet",
    "Generator",
    "ItemsView",
    "Iterable",
    "Iterator",
    "KeysView",
    "List",
    "Mapping",
    "MappingView",
    "Match",
    "MutableMapping",
    "MutableSequence",
    "MutableSet",
    "OrderedDict",
    "Pattern",
    "Reversible",
    "Sequence",
    "Set",
    "Text",
    "Tuple",
    "Type",
    "ValuesView",
}

BUILTIN = {
    "Dict": "dict",
    "FrozenSet": "frozenset",
    "List": "list",
    "Set": "set",
    "Text": "str",
    "Tuple": "tuple",
    "Type": "type",
}

ABC = {
    "AbstractSet",
    "AsyncContextManager",
    "AsyncGenerator",
    "AsyncIterable",
    "AsyncIterator",
    "Awaitable",
    "ByteString",
    "Callable",
    "Collection",
    "Container",
    "ContextManager",
    "Coroutine",
    "Generator",
    "ItemsView",
    "Iterable",
    "Iterator",
    "KeysView",
    "Mapping",
    "MappingView",
    "MutableMapping",
    "MutableSequence",
    "MutableSet",
    "Reversible",
    "Sequence",
    "ValuesView",
}

COLLECTIONS = {
    "ChainMap": "collections.ChainMap",
    "Counter": "collections.Counter",
    "DefaultDict": "collections.defaultdict",
    "Deque": "collections.deque",
    "OrderedDict": "collections.OrderedDict",
}

OTHER = {"Match": "re.Match", "Pattern": "re.Pattern"}


def replacement(name: str) -> str:
    """Return the preferred annotation spelling for *name*."""
    if name in BUILTIN:
        return BUILTIN[name]
    if name in ABC:
        return f"collections.abc.{name}"
    if name in COLLECTIONS:
        return COLLECTIONS[name]
    return OTHER.get(name, "a built-in or collections.abc equivalent")


def _module_aliases(tree: ast.AST) -> set[str]:
    """Return the local names bound to ``typing``/``typing_extensions``."""
    aliases = {"typing", "typing_extensions"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in {"typing", "typing_extensions"}:
                    aliases.add(alias.asname or alias.name)
    return aliases


def _attribute_violations(expr: ast.AST, aliases: set[str], path: Path) -> list[str]:
    """Return deprecated ``typing.X`` attributes inside *expr*."""
    violations: list[str] = []
    for node in ast.walk(expr):
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id in aliases
            and node.attr in DEPRECATED
        ):
            violations.append(
                f"{path.relative_to(ROOT)}:{node.lineno}: "
                f"`{node.value.id}.{node.attr}`; use `{replacement(node.attr)}`"
            )
    return violations


def _string_annotation_violations(
    expr: ast.AST, aliases: set[str], path: Path
) -> list[str]:
    """Return violations hidden in a string forward annotation."""
    if not isinstance(expr, ast.Constant) or not isinstance(expr.value, str):
        return []
    try:
        parsed = ast.parse(expr.value, mode="eval")
    except SyntaxError:
        return []
    for node in ast.walk(parsed):
        node.lineno = expr.lineno
    return _attribute_violations(parsed, aliases, path)


def scan(path: Path) -> list[str]:
    """Return human-readable violations found in one Python file."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    aliases = _module_aliases(tree)
    violations: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module in {
            "typing",
            "typing_extensions",
        }:
            if any(alias.name == "*" for alias in node.names):
                violations.append(
                    f"{path.relative_to(ROOT)}:{node.lineno}: "
                    f"`from {node.module} import *`; import names explicitly"
                )
            for alias in node.names:
                if alias.name in DEPRECATED:
                    violations.append(
                        f"{path.relative_to(ROOT)}:{node.lineno}: "
                        f"`from {node.module} import {alias.name}`; "
                        f"use `{replacement(alias.name)}`"
                    )
        elif (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id in aliases
            and node.attr in DEPRECATED
        ):
            violations.append(
                f"{path.relative_to(ROOT)}:{node.lineno}: "
                f"`{node.value.id}.{node.attr}`; use `{replacement(node.attr)}`"
            )
        elif isinstance(node, ast.arg) and node.annotation is not None:
            violations.extend(
                _string_annotation_violations(node.annotation, aliases, path)
            )
        elif isinstance(node, ast.AnnAssign) and node.annotation is not None:
            violations.extend(
                _string_annotation_violations(node.annotation, aliases, path)
            )
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.returns is not None:
                violations.extend(
                    _string_annotation_violations(node.returns, aliases, path)
                )
    return violations


def iter_sources() -> list[Path]:
    """Collect Python sources covered by the repository conventions."""
    paths: list[Path] = []
    for base in (PACKAGE_DIR, ROOT / "tests", ROOT / "scripts", ROOT / "workflow"):
        if base.exists():
            paths.extend(sorted(base.rglob("*.py")))
    docs_extensions = ROOT / "docs" / "source"
    if docs_extensions.exists():
        paths.extend(sorted(docs_extensions.rglob("*.py")))
    return paths


def main() -> int:
    violations: list[str] = []
    for path in iter_sources():
        if "__pycache__" in path.parts:
            continue
        violations.extend(scan(path))

    if violations:
        print(
            "Deprecated `typing` aliases are not allowed. "
            "Use built-in generics or `collections.abc`.",
            file=sys.stderr,
        )
        for violation in violations:
            print(f"  {violation}", file=sys.stderr)
        print(f"Found {len(violations)} violation(s).", file=sys.stderr)
        return 1

    print(f"Deprecated `typing` aliases: clean ({len(iter_sources())} files).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

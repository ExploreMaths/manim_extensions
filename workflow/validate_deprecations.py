# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Reject deprecated Python APIs and project symbols at the AST level.

Deprecation is not a ``typing``-only problem: modules, classes, functions and
aliases can all be deprecated.  Hand-maintaining a list of names would drift
from the interpreter and the packages we import, so this checker discovers
deprecations from their runtime metadata:

* PEP 585 aliases in :mod:`typing` and :mod:`typing_extensions` are found by
  inspecting the alias objects themselves (their origin and parameter count),
  not from a checked-in name list.
* Imported standard-library objects are flagged when they expose a
  non-empty ``__deprecated__`` attribute, when their type is a private
  ``_Deprecated*`` wrapper, or when accessing the attribute emits a
  :class:`DeprecationWarning`.
* Public functions and classes decorated with the project's ``@deprecated``
  decorator are discovered from the package AST.  Library code must not use
  them; tests are exempt because they exercise the deprecation itself.

The checker walks the package, tests, repository scripts, workflow tools and
Sphinx extensions.  String forward annotations are parsed as annotations.
Docstrings and comments are not inspected, so prose may explain an old name.

Usage:
    python workflow/validate_deprecations.py
"""

from __future__ import annotations

import ast
import builtins
import importlib
import sys
import warnings
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from _context import PACKAGE_DIR, ROOT

TYPING_MODULES = frozenset({"typing", "typing_extensions"})
STDLIB_MODULES = frozenset(sys.stdlib_module_names) | TYPING_MODULES
BUILTIN_TYPES = frozenset(
    value for value in vars(builtins).values() if isinstance(value, type)
)


def _typing_replacement(origin: Any, name: str) -> str | None:
    """Return the modern spelling for a deprecated typing alias."""
    if origin is None:
        return name or None
    module = getattr(origin, "__module__", "")
    origin_name = getattr(origin, "__name__", "")
    if not module or not origin_name:
        return None
    if module == "builtins":
        return origin_name
    return f"{module}.{origin_name}"


def _typing_alias_replacement(name: str, obj: Any) -> str | None:
    """Return a replacement if *obj* is a deprecated typing alias."""
    origin = getattr(obj, "__origin__", None)
    if origin is None:
        try:
            origin = __import__("typing").get_origin(obj)
        except Exception:
            origin = None
    type_name = type(obj).__name__
    # ByteString and the historical ``typing.io``/``typing.re`` modules are
    # explicit deprecated wrappers.  Do not hard-code their names.
    if type_name.startswith("_Deprecated"):
        return _typing_replacement(origin, getattr(obj, "__name__", ""))
    parameter_count = getattr(obj, "_nparams", 0) or 0
    # Generic aliases such as List/Sequence/Callable are the PEP 585
    # aliases.  Zero-parameter aliases (Hashable, Sized) are still legal and
    # must not be rejected.
    if origin is not None and parameter_count > 0:
        return _typing_replacement(origin, getattr(obj, "_name", "") or "")
    # ``Text`` is literally ``str``; catch any public typing name that is a
    # builtin class under a different name without naming the alias.
    if isinstance(obj, type) and obj in BUILTIN_TYPES and obj.__name__ != name:
        return obj.__name__
    return None


def _typing_aliases(module_name: str) -> dict[str, str]:
    """Map every deprecated alias in a typing module to its replacement."""
    module = importlib.import_module(module_name)
    aliases: dict[str, str] = {}
    for name, obj in vars(module).items():
        if name.startswith("_"):
            continue
        replacement = _typing_alias_replacement(name, obj)
        if replacement:
            aliases[name] = replacement
    return aliases


def _warning_message(caught: Iterable[warnings.WarningMessage]) -> str | None:
    """Return the first deprecation warning message in *caught*."""
    for warning in caught:
        if issubclass(warning.category, DeprecationWarning):
            return str(warning.message)
    return None


def _deprecated_metadata(obj: Any) -> str | None:
    """Return the object's deprecation message, if it exposes one."""
    message = getattr(obj, "__deprecated__", None)
    if message:
        return str(message)
    if type(obj).__name__.startswith("_Deprecated"):
        return "provider marks this wrapper as deprecated"
    return None


def _module_deprecation(module_name: str) -> str | None:
    """Return the deprecation message emitted by importing *module_name*."""
    root = module_name.split(".", 1)[0]
    if root not in STDLIB_MODULES:
        return None
    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            module = importlib.import_module(module_name)
    except Exception:
        return None
    return _warning_message(caught) or _deprecated_metadata(module)


def _attribute_deprecation(
    module_name: str, attribute_path: tuple[str, ...]
) -> str | None:
    """Return the deprecation message for ``module.attributes``."""
    if not attribute_path:
        return None
    if module_name in TYPING_MODULES:
        replacement = _typing_aliases(module_name).get(attribute_path[0])
        if replacement is None:
            return None
        return f"use `{replacement}`"
    root = module_name.split(".", 1)[0]
    if root not in STDLIB_MODULES:
        return None
    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            obj: Any = importlib.import_module(module_name)
            for part in attribute_path:
                obj = getattr(obj, part)
    except Exception:
        return None
    message = _warning_message(caught) or _deprecated_metadata(obj)
    return message


def _module_path(path: Path) -> str:
    """Return the dotted module name for a source file."""
    relative = path.relative_to(PACKAGE_DIR).with_suffix("")
    parts = list(relative.parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join([PACKAGE_DIR.name, *parts])


def _decorator_name(node: ast.AST) -> str:
    """Return the final component of a decorator expression."""
    target = node.func if isinstance(node, ast.Call) else node
    if isinstance(target, ast.Name):
        return target.id
    if isinstance(target, ast.Attribute):
        return target.attr
    return ""


def _decorator_message(node: ast.Call) -> str:
    """Return the literal message of a ``@deprecated(...)`` call."""
    if node.args and isinstance(node.args[0], ast.Constant):
        value = node.args[0].value
        if isinstance(value, str):
            return value
    return "deprecated API"


def project_deprecations() -> dict[str, str]:
    """Discover public ``@deprecated`` functions and classes in the package."""
    found: dict[str, str] = {}
    for path in sorted(PACKAGE_DIR.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        module = _module_path(path)
        for node in tree.body:
            if not isinstance(
                node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
            ):
                continue
            for decorator in node.decorator_list:
                if _decorator_name(decorator) != "deprecated":
                    continue
                message = (
                    _decorator_message(decorator)
                    if isinstance(decorator, ast.Call)
                    else "deprecated API"
                )
                found[f"{module}.{node.name}"] = message
                break
    return found


def _import_aliases(tree: ast.AST) -> tuple[dict[str, str], dict[str, str]]:
    """Return module aliases and imported-symbol aliases."""
    modules: dict[str, str] = {
        "typing": "typing",
        "typing_extensions": "typing_extensions",
    }
    symbols: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                local = alias.asname or alias.name
                modules[local] = alias.name
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            for alias in node.names:
                if alias.name == "*":
                    continue
                local = alias.asname or alias.name
                symbols[local] = f"{node.module}.{alias.name}"
    return modules, symbols


def _resolve_name(
    node: ast.AST, modules: dict[str, str], symbols: dict[str, str]
) -> str | None:
    """Resolve an attribute/name expression to a dotted name."""
    if isinstance(node, ast.Name):
        return symbols.get(node.id) or modules.get(node.id) or node.id
    if isinstance(node, ast.Attribute):
        base = _resolve_name(node.value, modules, symbols)
        return f"{base}.{node.attr}" if base else None
    return None


def _attribute_parts(
    full: str, modules: dict[str, str]
) -> tuple[str, tuple[str, ...]] | None:
    """Split a resolved name into its imported module and remaining attributes."""
    candidates = sorted(
        (
            (key, module)
            for alias, module in modules.items()
            for key in (alias, module)
            if full == key or full.startswith(f"{key}.")
        ),
        key=lambda item: len(item[0]),
        reverse=True,
    )
    if not candidates:
        return None
    alias, module = candidates[0]
    rest = full[len(alias) :].lstrip(".")
    return module, tuple(part for part in rest.split(".") if part)


def _string_annotation_violations(
    expr: ast.AST,
    path: Path,
    modules: dict[str, str],
    symbols: dict[str, str],
    deprecated: dict[str, str],
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
    return _expression_violations(parsed, path, modules, symbols, deprecated)


def _expression_violations(
    root: ast.AST,
    path: Path,
    modules: dict[str, str],
    symbols: dict[str, str],
    deprecated: dict[str, str],
) -> list[str]:
    """Return deprecation violations in one expression tree."""
    violations: list[str] = []
    for node in ast.walk(root):
        if not isinstance(node, (ast.Name, ast.Attribute)):
            continue
        full = _resolve_name(node, modules, symbols)
        if full is None:
            continue
        location = f"{path.relative_to(ROOT)}:{node.lineno}"
        if full in deprecated:
            violations.append(f"{location}: `{full}` is deprecated; {deprecated[full]}")
            continue
        parts = _attribute_parts(full, modules)
        if parts is None:
            continue
        module_name, attribute_path = parts
        message = _attribute_deprecation(module_name, attribute_path)
        if message:
            violations.append(f"{location}: `{full}` is deprecated ({message})")
    return violations


def scan(path: Path, deprecated: dict[str, str] | None = None) -> list[str]:
    """Return human-readable violations found in one Python file."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules, symbols = _import_aliases(tree)
    project = deprecated if deprecated is not None else project_deprecations()
    violations: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                message = _module_deprecation(alias.name)
                if message:
                    violations.append(
                        f"{path.relative_to(ROOT)}:{node.lineno}: "
                        f"`import {alias.name}` imports a deprecated module "
                        f"({message})"
                    )
        elif isinstance(node, ast.ImportFrom) and node.module:
            message = _module_deprecation(node.module)
            if message:
                violations.append(
                    f"{path.relative_to(ROOT)}:{node.lineno}: "
                    f"`from {node.module}` imports a deprecated module ({message})"
                )
            if node.module in TYPING_MODULES and any(
                alias.name == "*" for alias in node.names
            ):
                violations.append(
                    f"{path.relative_to(ROOT)}:{node.lineno}: "
                    f"`from {node.module} import *`; import names explicitly"
                )
            for alias in node.names:
                if alias.name == "*":
                    continue
                full = f"{node.module}.{alias.name}"
                if full in project:
                    violations.append(
                        f"{path.relative_to(ROOT)}:{node.lineno}: "
                        f"`{full}` is deprecated; {project[full]}"
                    )
                    continue
                typed = _attribute_deprecation(node.module, (alias.name,))
                if typed:
                    violations.append(
                        f"{path.relative_to(ROOT)}:{node.lineno}: "
                        f"`from {node.module} import {alias.name}` is deprecated "
                        f"({typed})"
                    )
        elif isinstance(node, ast.arg) and node.annotation is not None:
            violations.extend(
                _string_annotation_violations(
                    node.annotation, path, modules, symbols, project
                )
            )
        elif isinstance(node, ast.AnnAssign) and node.annotation is not None:
            violations.extend(
                _string_annotation_violations(
                    node.annotation, path, modules, symbols, project
                )
            )
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.returns is not None:
                violations.extend(
                    _string_annotation_violations(
                        node.returns, path, modules, symbols, project
                    )
                )

    # Project decorators are also reachable through the local module name and
    # through attributes rather than direct imports; check every expression.
    violations.extend(_expression_violations(tree, path, modules, symbols, project))
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


def _is_test_source(path: Path) -> bool:
    """Return whether *path* belongs to the test suite."""
    try:
        path.relative_to(ROOT / "tests")
    except ValueError:
        return False
    return True


def main() -> int:
    """Run the checker over all covered sources."""
    files = iter_sources()
    deprecated = project_deprecations()
    violations: list[str] = []
    for path in files:
        if "__pycache__" in path.parts:
            continue
        file_deprecated = {} if _is_test_source(path) else deprecated
        violations.extend(scan(path, file_deprecated))

    if violations:
        print(
            "Deprecated APIs and typing aliases are not allowed in source code.",
            file=sys.stderr,
        )
        for violation in violations:
            print(f"  {violation}", file=sys.stderr)
        print(f"Found {len(violations)} violation(s).", file=sys.stderr)
        return 1

    print(f"Deprecated APIs: clean ({len(files)} files).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

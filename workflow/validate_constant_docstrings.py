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

Class-scope constants are checked too.  A public class assignment is a
constant when it is all-uppercase, annotated as ``ClassVar``, or an annotated
literal default on a non-dataclass class (for example ``style = "classic"``).
Dataclass / NamedTuple fields are instance data and stay documented by the
class docstring.  Every such constant needs its own ``#:`` description.

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
import re
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


def hashdoc_text(lines: list[str], lineno: int) -> str | None:
    """Return the text of the ``#:`` block above *lineno*, if any."""
    index = lineno - 2
    while index >= 0 and not lines[index].strip():
        index -= 1
    if index < 0 or not lines[index].lstrip().startswith("#:"):
        return None
    first = index
    while first > 0 and lines[first - 1].lstrip().startswith("#:"):
        first -= 1
    return lines[first].split("#:", 1)[1].strip()


def hashdoc_starts_upper(lines: list[str], lineno: int) -> bool:
    """Return whether a ``#:`` description starts with a capital letter."""
    text = hashdoc_text(lines, lineno)
    if text is None:
        return True
    return not text[:1].islower()


def hashdoc_ends_period(lines: list[str], lineno: int) -> bool:
    """Return whether the ``#:`` block above *lineno* ends like a sentence."""
    index = lineno - 2
    while index >= 0 and not lines[index].strip():
        index -= 1
    if index < 0 or not lines[index].lstrip().startswith("#:"):
        return True
    text = lines[index].split("#:", 1)[1].strip()
    return bool(re.search(r"[.!?][`'\")\]}]*$", text))


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
        elif preceding_hashdoc(lines, node.lineno) and not hashdoc_starts_upper(
            lines, node.lineno
        ):
            missing.append((node.lineno, f"{name}: description must start uppercase"))
        elif preceding_hashdoc(lines, node.lineno) and not hashdoc_ends_period(
            lines, node.lineno
        ):
            missing.append((node.lineno, f"{name}: description must end with a period"))
    missing.extend(check_class_constants(tree, lines))
    return missing


def _decorator_name(node: ast.AST) -> str:
    """Return the bare name of a decorator, including ``@x(...)`` calls."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Call):
        return _decorator_name(node.func)
    return ""


def _is_instance_data_class(cls: ast.ClassDef) -> bool:
    """Return whether *cls* declares fields through a runtime data decorator."""
    return any(
        _decorator_name(d) in {"dataclass", "define", "attrs", "NamedTuple"}
        for d in cls.decorator_list
    )


def _is_class_constant(name: str, node: ast.stmt, cls: ast.ClassDef) -> bool:
    """Return whether a class assignment is a shared constant, not instance data."""
    if name.isupper():
        return True
    if isinstance(node, ast.AnnAssign):
        annotation = node.annotation
        while isinstance(annotation, ast.Subscript):
            annotation = annotation.value
        if isinstance(annotation, ast.Name) and annotation.id == "ClassVar":
            return True
        if isinstance(annotation, ast.Attribute) and annotation.attr == "ClassVar":
            return True
        if _is_instance_data_class(cls):
            # A public dataclass/NamedTuple field is user-facing instance data:
            # it is rendered as documentation just like a class constant, but
            # autodoc cannot describe it without its own ``#:`` block.
            return True
        return isinstance(
            node.value,
            (ast.Constant, ast.UnaryOp, ast.List, ast.Tuple, ast.Dict, ast.Set),
        )
    if isinstance(node, ast.Assign):
        return isinstance(
            node.value,
            (ast.Constant, ast.UnaryOp, ast.List, ast.Tuple, ast.Dict, ast.Set),
        )
    return False


def class_docstring_documents(cls: ast.ClassDef, name: str) -> bool:
    """Return whether the class docstring lists *name* as a public attribute.

    Dataclass fields are often documented in a numpydoc ``Parameters`` or
    ``Attributes`` section.  That prose is what autodoc displays, so a field
    with such an entry does not need a duplicate ``#:`` block.
    """
    doc = ast.get_docstring(cls) or ""
    lines = doc.splitlines()
    in_section = False
    underline_next = False
    for index, line in enumerate(lines):
        stripped = line.strip()
        if underline_next:
            underline_next = False
            if set(stripped) == {"-"} and len(stripped) >= 3:
                continue
            in_section = False
        if stripped in {"Parameters", "Attributes", "Other Parameters"}:
            in_section = True
            underline_next = True
            continue
        if (
            in_section
            and stripped
            and re.match(rf"{re.escape(name)}\s*(?::|$)", stripped)
        ):
            return True
        if in_section and stripped and set(stripped) == {"-"} and len(stripped) >= 3:
            # An underlined header ends the previous section.
            in_section = False
    return False


def check_class_constants(tree: ast.Module, lines: list[str]) -> list[tuple[int, str]]:
    """Return ``(line, name)`` for public class constants missing docs."""
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
                if name.startswith("_"):
                    continue
                # Any public class field with a ``#:`` description must use
                # sentence case, including dataclass fields that are not
                # class constants.
                if preceding_hashdoc(lines, node.lineno) and not hashdoc_starts_upper(
                    lines, node.lineno
                ):
                    missing.append(
                        (
                            node.lineno,
                            f"{cls.name}.{name}: description must start uppercase",
                        )
                    )
                    continue
                if not _is_class_constant(name, node, cls):
                    continue
                documented = (
                    preceding_hashdoc(lines, node.lineno)
                    or trailing_docstring(cls.body, node)
                    or (
                        _is_instance_data_class(cls)
                        and class_docstring_documents(cls, name)
                    )
                )
                if not documented:
                    missing.append((node.lineno, f"{cls.name}.{name}"))
                elif preceding_hashdoc(lines, node.lineno) and not hashdoc_starts_upper(
                    lines, node.lineno
                ):
                    missing.append(
                        (
                            node.lineno,
                            f"{cls.name}.{name}: description must start uppercase",
                        )
                    )
                elif preceding_hashdoc(lines, node.lineno) and not hashdoc_ends_period(
                    lines, node.lineno
                ):
                    missing.append(
                        (
                            node.lineno,
                            f"{cls.name}.{name}: description must end with a period",
                        )
                    )
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
            if "description must start uppercase" in name:
                print(
                    f"  {rel}:{lineno}  constant-description-style: "
                    f"'{name.split(':')[0]}' must start with a capital letter"
                )
            else:
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

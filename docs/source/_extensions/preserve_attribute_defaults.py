# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Render documented attribute defaults with their source spelling.

``autodoc_preserve_defaults`` only affects callable signatures: attribute
directives fall back to ``repr(value)``, so a mapping of direction vectors
is rendered as ``{'down': array([0., -1., 0.]), ...}`` even though the
source reads ``"down": DOWN``.  This extension recovers the assignment
expression from the defining module with :mod:`ast` and swaps it into the
signature, so constants stay recognisable (and, because the value is
emitted as an inline ``default_value`` node, ``default_value_links`` can
turn those names into cross-references).
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

from docutils import nodes
from sphinx import addnodes

_ASSIGNMENT_CACHE: dict[tuple[str, str], dict[str, str]] = {}


def _body_for_class(tree: ast.Module, class_name: str) -> list[ast.stmt]:
    body: list[ast.stmt] = tree.body
    for part in filter(None, class_name.split(".")):
        for node in body:
            if isinstance(node, ast.ClassDef) and node.name == part:
                body = node.body
                break
        else:
            return []
    return body


def _assignments(module: str, class_name: str) -> dict[str, str]:
    """Return ``{attribute: source expression}`` for a module or class body."""
    key = (module, class_name)
    if key in _ASSIGNMENT_CACHE:
        return _ASSIGNMENT_CACHE[key]

    result: dict[str, str] = {}
    module_object = sys.modules.get(module)
    source_file = getattr(module_object, "__file__", None)
    if not source_file:
        _ASSIGNMENT_CACHE[key] = result
        return result
    try:
        tree = ast.parse(Path(source_file).read_text(encoding="utf-8"))
    except (OSError, SyntaxError, UnicodeDecodeError):
        _ASSIGNMENT_CACHE[key] = result
        return result

    for node in _body_for_class(tree, class_name):
        target = value = None
        if isinstance(node, ast.AnnAssign):
            target, value = node.target, node.value
        elif isinstance(node, ast.Assign) and len(node.targets) == 1:
            target, value = node.targets[0], node.value
        if isinstance(target, ast.Name) and value is not None:
            result[target.id] = ast.unparse(value)

    _ASSIGNMENT_CACHE[key] = result
    return result


def _replace_value(annotation: nodes.Element, source: str) -> None:
    """Swap the trailing repr text of `` = <value>`` for ``source``."""
    for index, child in enumerate(annotation.children):
        if not isinstance(child, nodes.Text):
            continue
        # Everything after `` = `` is the value; keep the prefix nodes.
        del annotation[index:]
        inline = nodes.inline(classes=["default_value"])
        inline += nodes.Text(source)
        annotation += inline
        return


def _collapse_attribute_defaults(app, doctree, docname) -> None:
    for signature in doctree.findall(addnodes.desc_signature):
        class_name = signature.get("class") or ""
        module = signature.get("module") or ""
        fullname = signature.get("fullname") or ""
        if not class_name or not fullname:
            # Only class attributes are rewritten; module-level data keeps
            # its evaluated representation (``.. autodata::``).
            continue
        attribute = fullname.rsplit(".", 1)[-1]
        source = _assignments(module, class_name).get(attribute)
        if source is None:
            continue
        for annotation in signature.children:
            if not isinstance(annotation, addnodes.desc_annotation):
                continue
            if annotation.astext().startswith(" = "):
                _replace_value(annotation, source)
                break


def setup(app):
    # Run before ``default_value_links`` (priority 500) so the recovered
    # source spelling is still processed into constant references.
    app.connect("doctree-resolved", _collapse_attribute_defaults, priority=400)
    return {"version": "1.0", "parallel_read_safe": True, "parallel_write_safe": True}

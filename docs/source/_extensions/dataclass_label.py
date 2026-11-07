# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Label documented dataclasses as ``dataclass`` instead of ``class``.

Sphinx's Python domain always renders the object-kind annotation of a class
as ``class``.  For classes decorated with :func:`dataclasses.dataclass` the
generated signature reads much better as ``dataclass``, so this extension
records which documented classes are dataclasses while autodoc is running
and rewrites the annotation node before the page is written.
"""

from __future__ import annotations

import dataclasses

from docutils import nodes
from sphinx import addnodes


def _record_dataclass(app, what, name, obj, options, signature,
                      return_annotation) -> None:
    if what != "class" or not isinstance(obj, type):
        return
    try:
        is_dataclass = dataclasses.is_dataclass(obj)
    except Exception:  # pragma: no cover - defensive guard
        return
    if is_dataclass:
        app._dataclass_display_names.add(name)


def _label_dataclasses(app, doctree, docname) -> None:
    names = getattr(app, "_dataclass_display_names", set())
    if not names:
        return
    for signature in doctree.findall(addnodes.desc_signature):
        ids = signature.get("ids") or []
        if len(ids) != 1 or ids[0] not in names:
            continue
        for child in signature.children:
            if not isinstance(child, addnodes.desc_annotation):
                continue
            if child.astext().strip() != "class":
                continue
            del child[:]
            child += nodes.Text("dataclass ")
            break


def _init(app) -> None:
    app._dataclass_display_names = set()


def setup(app):
    app.connect("builder-inited", _init)
    app.connect("autodoc-process-signature", _record_dataclass)
    app.connect("doctree-resolved", _label_dataclasses)
    return {"version": "1.0", "parallel_read_safe": False, "parallel_write_safe": True}

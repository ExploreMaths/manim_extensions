# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Prepend a deprecation notice to the docstring of any object decorated
with :func:`~manim_extensions.utils.deprecation.deprecated`.

The decorator stores its (RST-formatted) message on the object as
``__deprecated__``; this extension reads that attribute during the
``autodoc-process-docstring`` event and inserts a custom directive that
renders the message like ``.. deprecated::`` does (a ``versionmodified``
block) while parsing the RST inline markup (``:func:`` roles, double
backtick code) into links/code.

``sphinx-autodoc-typehints`` also injects ``__deprecated__`` messages on
its own, but its directive renders the message as plain text and would
duplicate ours, so its injection is disabled here.
"""

from __future__ import annotations

from docutils import nodes
from sphinx import addnodes
from sphinx.locale import _
from sphinx.util.docutils import SphinxDirective


class ExtDeprecatedDirective(SphinxDirective):
    """Render a deprecation notice like ``.. deprecated::`` does, without
    requiring a version argument, and parse the message as RST."""

    has_content = True

    def run(self) -> list[nodes.Node]:
        label = nodes.inline("", _("Deprecated") + ": ", classes=["versionmodified", "deprecated"])
        node = addnodes.versionmodified(type="deprecated")
        para = nodes.paragraph("", "", label, translatable=False)
        inodes, _messages = self.state.inline_text("\n".join(self.content), self.lineno)
        para += inodes
        node.append(para)
        self.set_source_info(node)
        return [node]


def _prepend_deprecation_warning(app, what, name, obj, options, lines):
    """Insert a deprecation notice at the top of *lines* when applicable."""
    try:
        msg = getattr(obj, "__deprecated__", None)
    except Exception:
        # Objects with a custom __getattr__ (e.g. manim_fontawesome's module
        # __getattr__) may raise arbitrary exceptions (KeyError, ...) for
        # unknown names instead of AttributeError. Treat as "not deprecated".
        return
    if not msg:
        return

    block = [".. ext-deprecated::", ""]
    for msg_line in str(msg).splitlines() or [""]:
        block.append(f"   {msg_line}" if msg_line else "")
    block.append("")

    lines[0:0] = block


def _disable_typehints_deprecation_injection(app, *_args, **_kwargs):
    """Neutralise sphinx-autodoc-typehints' own ``__deprecated__``
    injection so its plain-text directive does not duplicate ours."""
    try:
        import sphinx_autodoc_typehints._docstring.handler as _handler

        def _noop(*_a, **_k):
            return None

        _handler.inject_deprecation = _noop
    except Exception:
        # Older/newer typehints layouts: our directive still renders, worst
        # case the typehints one appears too.
        pass


def setup(app):
    """Sphinx extension entry point."""
    app.add_directive("ext-deprecated", ExtDeprecatedDirective)
    app.connect(
        "builder-inited",
        _disable_typehints_deprecation_injection,
        priority=900,
    )
    app.connect(
        "autodoc-process-docstring",
        _prepend_deprecation_warning,
        priority=0,
    )
    return {"version": "1.0", "parallel_read_safe": True, "parallel_write_safe": True}

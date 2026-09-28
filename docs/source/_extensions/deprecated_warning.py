# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Prepend a DeprecationWarning admonition to the docstring of any object
decorated with :func:`~manim_extensions.utils.deprecation.deprecated`.

The decorator stores its (RST-formatted) message on the object as
``__deprecated__``; this extension reads that attribute during the
``autodoc-process-docstring`` event and inserts an
``.. admonition:: DeprecationWarning`` block (styled as a warning) at the
top of the docstring, rendering the message verbatim as RST.
"""

from __future__ import annotations


def _prepend_deprecation_warning(app, what, name, obj, options, lines):
    """Insert a deprecation warning at the top of *lines* when applicable."""
    try:
        msg = getattr(obj, "__deprecated__", None)
    except Exception:
        # Objects with a custom __getattr__ (e.g. manim_fontawesome's module
        # __getattr__) may raise arbitrary exceptions (KeyError, ...) for
        # unknown names instead of AttributeError. Treat as "not deprecated".
        return
    if not msg:
        return

    block = [".. admonition:: DeprecationWarning", "   :class: warning", ""]
    for msg_line in str(msg).splitlines() or [""]:
        block.append(f"   {msg_line}" if msg_line else "")
    block.append("")

    lines[0:0] = block


def setup(app):
    """Sphinx extension entry point."""
    app.connect(
        "autodoc-process-docstring",
        _prepend_deprecation_warning,
        priority=0,
    )
    return {"version": "1.0", "parallel_read_safe": True, "parallel_write_safe": True}

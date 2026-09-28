# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Prepend a warning admonition to the docstring of any object decorated
with :func:`typing.deprecated` / :func:`typing_extensions.deprecated`.

The decorator stores its message on the object as ``__deprecated__``; this
extension reads that attribute during the ``autodoc-process-docstring``
event and inserts a ``.. warning::`` block at the top of the docstring.
"""

from __future__ import annotations


def _prepend_deprecation_warning(app, what, name, obj, options, lines):
    """Insert a deprecation warning at the top of *lines* when applicable."""
    msg = getattr(obj, "__deprecated__", None)
    if not msg:
        return

    block = [".. warning::", ""]
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

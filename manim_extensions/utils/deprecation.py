# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Patched :func:`deprecated` decorator.

Drop-in replacement for :func:`typing_extensions.deprecated` that accepts a
message written in **RST**. The RST markup is preserved on the decorated
object's ``__deprecated__`` attribute (used by the Sphinx
``deprecated_warning`` extension to render a styled admonition), while the
runtime :class:`DeprecationWarning` strips the inline markup so it stays
readable on the console.

Examples
--------
>>> from manim_extensions.utils.deprecation import deprecated
>>> @deprecated("``old`` is deprecated; use :func:`new` instead.")
... def old():
...     pass
"""

from __future__ import annotations

import re
from typing import Any

from typing_extensions import deprecated as _deprecated

# Matches RST inline roles (:role:`target`) and interpreted text / code
# (``...`` or `...`); captures the inner text so it can be recovered.
_RST_MARKUP_RE = re.compile(r":[\w:]+:`([^`]+)`|``([^`]+)``|`([^`]+)`")


def _strip_rst(text: str) -> str:
    """Return *text* with RST inline markup removed."""
    return _RST_MARKUP_RE.sub(
        lambda m: m.group(1) or m.group(2) or m.group(3), text
    )


def deprecated(msg: str, *args: Any, **kwargs: Any):
    """Mark *obj* as deprecated.

    Parameters
    ----------
    msg : str
        Deprecation message. May contain RST inline markup (``:func:``
        roles, double-backtick code, ...) which is kept for the docs but
        stripped from the runtime warning.
    *args, **kwargs
        Forwarded to :func:`typing_extensions.deprecated`
        (``category``, ``stacklevel``).
    """
    outer = _deprecated(_strip_rst(msg), *args, **kwargs)

    def wrapper(obj):
        decorated = outer(obj)
        # Restore the RST version for Sphinx (typing_extensions stored the
        # stripped one).
        try:
            decorated.__deprecated__ = msg
        except (AttributeError, TypeError):
            pass
        return decorated

    return wrapper

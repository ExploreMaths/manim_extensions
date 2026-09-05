# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Dynamically add ``:show-inheritance:`` to autoclass directives for classes
that have non-trivial base classes.

This extension hooks into the ``source-read`` event so it runs on every
Sphinx build without modifying the ``.rst`` source files on disk.
"""

from __future__ import annotations

import importlib
import re
import sys

_DIRECTIVE_RE = re.compile(r"^(\.\. autoclass::\s+)(\S+)\s*$")
_OPT_RE = re.compile(r"^\s+:\w")


def _has_nontrivial_bases(dotted_path: str) -> bool:
    """Return *True* if *dotted_path* refers to a class whose MRO includes
    something other than ``object``."""
    try:
        module_path, _, name = dotted_path.rpartition(".")
        if not module_path:
            return False
        module = importlib.import_module(module_path)
        cls = getattr(module, name, None)
        if cls is None or not isinstance(cls, type):
            return False
        return any(b is not object for b in cls.__bases__)
    except Exception:
        return False


def _inject_show_inheritance(text: str) -> str:
    """Process *text* and add/remove ``:show-inheritance:`` per class."""
    lines = text.split("\n")
    result: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = _DIRECTIVE_RE.match(line)
        if not m:
            result.append(line)
            i += 1
            continue

        # Found an autoclass directive — emit it, then collect options.
        result.append(line)
        dotted = m.group(2)
        want_si = _has_nontrivial_bases(dotted)
        i += 1

        # Collect the option block (indented lines starting with ':')
        opts: list[str] = []
        while i < len(lines) and _OPT_RE.match(lines[i]):
            opts.append(lines[i])
            i += 1

        # Determine current state
        has_si = any(":show-inheritance:" in o for o in opts)

        if want_si and not has_si:
            # Add :show-inheritance: to the option block
            opts.append("   :show-inheritance:")
        elif not want_si and has_si:
            # Remove existing :show-inheritance:
            opts = [o for o in opts if ":show-inheritance:" not in o]

        result.extend(opts)

    return "\n".join(result)


def setup(app):
    """Sphinx extension entry point."""
    def on_source_read(app, docname, source):
        source[0] = _inject_show_inheritance(source[0])

    app.connect("source-read", on_source_read)
    return {"version": "0.1", "parallel_read_safe": True}

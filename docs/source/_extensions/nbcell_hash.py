# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Shared nbcell content hashing (no third-party dependencies).

``workflow/execute_nbcell_examples.py`` imports this module so the cache
keys it stores match exactly what ``nbcell_directive`` computes at build
time, without pulling docutils/sphinx into the CI runner.
"""

import hashlib
import textwrap


def normalize_code(code: str) -> str:
    """Canonical hash of a cell's source.

    Trim trailing spaces, drop outer blank lines, dedent, and hash --
    mirroring how docutils hands directive content to ``self.content``.
    """
    lines = [ln.rstrip() for ln in code.split("\n")]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    if not lines:
        return ""
    body = textwrap.dedent("\n".join(lines))
    return hashlib.md5(body.encode()).hexdigest()

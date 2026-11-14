# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Resolve the project layout used by every checker.

Defaults preserve the layout of ``manim_extensions``.  A caller that vendors
these scripts into another repository sets the ``MANIM_DOC_CHECKS_*``
environment variables (``run_checks.py`` does this from its CLI flags or from
``[tool.manim-doc-checks]`` in the target ``pyproject.toml``).
"""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(
    os.environ.get("MANIM_DOC_CHECKS_ROOT", Path(__file__).resolve().parent.parent)
).resolve()
PACKAGE = os.environ.get("MANIM_DOC_CHECKS_PACKAGE", "manim_extensions")
DISTRIBUTION = os.environ.get("MANIM_DOC_CHECKS_DISTRIBUTION", PACKAGE)
PACKAGE_DIR = Path(
    os.environ.get("MANIM_DOC_CHECKS_PACKAGE_DIR", ROOT / PACKAGE)
).resolve()
DOCS = Path(os.environ.get("MANIM_DOC_CHECKS_DOCS", ROOT / "docs" / "source")).resolve()
EXAMPLES = Path(
    os.environ.get("MANIM_DOC_CHECKS_EXAMPLES", ROOT / "examples")
).resolve()

# Historical name used by most checker functions.
SRC = PACKAGE_DIR

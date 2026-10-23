# SPDX-FileCopyrightText: 2021 KingWampy
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


"""Rubik's Cube helpers and scene objects.

The module exposes the main cube model and related animation utilities for
visualising cube states in Manim scenes.

"""

from .cube import *
from .cube_animations import *


try:
    from importlib.metadata import version as _version
except ImportError:  # pragma: no cover
    from importlib_metadata import version as _version

try:
    __version__ = _version("manim_extensions.rubikscube")
except Exception:
    try:
        __version__ = _version("manim_extensions")
    except Exception:
        __version__ = "unknown"

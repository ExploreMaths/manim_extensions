# SPDX-FileCopyrightText: 2020 GarryBGoode
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
# patched: explicit public export list and rebinding of the utils submodule

""":class:`~manim_extensions.cad_drawing_utils` CAD drawing helpers.

This package exposes dimension, hatch, path, corner and Bezier helpers for
CAD-style diagrams in Manim scenes.
"""

from __future__ import annotations

from .dimensions import *
from .hatch import *
from .path_mapper import *
from .round_corners import *
from .utils import *

from importlib import import_module as _import_module

utils = _import_module(__name__ + ".utils")
del _import_module

__version__ = "0.0.5"

__all__ = [
    "AngleDimension3Point",
    "AngleDimensionMob",
    "BezierHandlebars",
    "CADArrowHead",
    "chamfer_corner_param",
    "chamfer_corners",
    "CurveWarp",
    "DashDotMobject",
    "DashedLineMobject",
    "HatchLines",
    "LinearDimension",
    "PathMapper",
    "PathOffsetMobject",
    "PointerLabelFree",
    "PointerToMob",
    "round_corner_param",
    "round_corners",
    "angle_between_vectors_signed",
    "curve_intersection",
    "utils",
    "__version__",
]

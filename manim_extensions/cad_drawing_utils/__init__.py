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
    "Angle_Dimension_3point",
    "Angle_Dimension_Mob",
    "Bezier_Handlebars",
    "CAD_ArrowHead",
    "Chamfer_Corner_Param",
    "Chamfer_Corners",
    "Curve_Warp",
    "DashDot_mobject",
    "Dashed_line_mobject",
    "Hatch_lines",
    "Linear_Dimension",
    "Path_mapper",
    "Path_Offset_Mobject",
    "Pointer_Label_Free",
    "Pointer_To_Mob",
    "Round_Corner_Param",
    "Round_Corners",
    "angle_between_vectors_signed",
    "curve_intersection",
    "utils",
    "__version__",
]

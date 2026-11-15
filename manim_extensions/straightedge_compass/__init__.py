# SPDX-FileCopyrightText: 2026 manim-straightedge-compass contributors
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""manim-straightedge-compass: animated straightedge-and-compass
constructions for Manim.

Public API
----------
Geometry
~~~~~~~~
P, distance, midpoint, angle_of, unit, point_on,
circle_circle_intersection, line_line_intersection,
circle_line_intersection, uppermost, lowermost, leftmost, rightmost, other

Tools
~~~~~
:class:`~manim_extensions.straightedge_compass.compass.Compass`, :class:`~manim_extensions.straightedge_compass.compass.CompassDrawArc`, :class:`~manim_extensions.straightedge_compass.straightedge.Straightedge`, :class:`~manim_extensions.straightedge_compass.straightedge.PencilTip`, :class:`~manim_extensions.straightedge_compass.straightedge.RulerDraw`, :class:`~manim_extensions.straightedge_compass.marks.MarkedPoint`

Scene base class
~~~~~~~~~~~~~~~~
:class:`~manim_extensions.straightedge_compass.scene.EuclidScene`, with helpers mark_point / draw_circle / draw_arc / draw_segment.
"""

from __future__ import annotations
from .geometry import (
    P,
    distance,
    midpoint,
    angle_of,
    unit,
    rotate_vec,
    point_on,
    circle_circle_intersection,
    line_line_intersection,
    circle_line_intersection,
    uppermost,
    lowermost,
    leftmost,
    rightmost,
    other,
)
from .compass import Compass, CompassDrawArc
from .straightedge import Straightedge, PencilTip, RulerDraw
from .marks import MarkedPoint, POINT_COLOR
from .scene import (
    EuclidScene,
    CONSTRUCTION_COLOR,
    CONSTRUCTION_GREEN,
    RESULT_COLOR,
    RESULT_RED,
)

__all__ = [
    "P",
    "distance",
    "midpoint",
    "angle_of",
    "unit",
    "rotate_vec",
    "point_on",
    "circle_circle_intersection",
    "line_line_intersection",
    "circle_line_intersection",
    "uppermost",
    "lowermost",
    "leftmost",
    "rightmost",
    "other",
    "Compass",
    "CompassDrawArc",
    "Straightedge",
    "PencilTip",
    "RulerDraw",
    "MarkedPoint",
    "POINT_COLOR",
    "EuclidScene",
    "CONSTRUCTION_COLOR",
    "CONSTRUCTION_GREEN",
    "RESULT_COLOR",
    "RESULT_RED",
]

__version__ = "0.1.1"

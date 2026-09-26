# SPDX-FileCopyrightText: 2026 jj-math
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Geometry methods for compass.

This module provides geometry utility functions for compass operations.

"""

from typing import Any

from manim import Arc, PURE_YELLOW, RIGHT
from manim.typing import Point3D, Vector3D
from manim.utils.color import ParsableManimColor

__all__ = [
    "get_arc",
]
import numpy as np


def get_arc(
    niddle_pos: Point3D,
    pen_pos: Point3D,
    angle: float,
    color: ParsableManimColor = PURE_YELLOW,
    **kwargs: Any,
) -> Arc:
    """

    Construct an arc from its centre and starting point.

    Parameters
    ----------
    niddle_pos : np.ndarray
        Centre of the arc.
    pen_pos : np.ndarray
        Starting point of the arc.
    angle : float
        Central angle of the arc.
    color
        Colour of the arc.
    kwargs
        Other keyword arguments for the arc.

    Returns
    -------
    Arc
        The constructed :class:`~manim.mobject.geometry.arc.Arc` instance,
        centred at ``niddle_pos`` and starting at ``pen_pos``.


    Examples
    ----------

    .. manim:: GetArcDocExample
       :save_last_frame:

       from manim import *
       from manim_extensions.compass import get_arc

       class GetArcDocExample(Scene):
           def construct(self):
               arc = get_arc(ORIGIN, 2 * RIGHT, PI / 2)
               self.add(
                   Dot(ORIGIN, color=RED),
                   Dot(2 * RIGHT, color=PURE_YELLOW),
                   arc,
               )
        """
    arc_radius = get_distance(niddle_pos, pen_pos)
    vec_s = pen_pos - niddle_pos
    return Arc(
        arc_center=niddle_pos,
        radius=arc_radius,
        start_angle=get_vecs_angle(RIGHT, vec_s),
        angle=angle,
        color=color,
        **kwargs,
    )


def get_distance(
    point_start: Point3D,
    point_end: Point3D,
) -> float:
    """Compute the distance between two points.

    Parameters
    ----------
    point_start : np.ndarray
        The point used by the operation.
    point_end : np.ndarray
        The point used by the operation.

    Returns
    -------
    float
        The Euclidean distance between ``point_start`` and ``point_end``.
        """
    return float(np.linalg.norm(point_start - point_end))


def is_counter_clockwise(
    vector_start: Vector3D,
    vector_end: Vector3D,
) -> bool:
    """Return whether vector_end is counter-clockwise from vector_start.

    Parameters
    ----------
    vector_start : np.ndarray
        Starting vector used as the reference direction for the orientation test.
    vector_end : np.ndarray
        Ending vector whose orientation relative to the starting vector is evaluated.

    Returns
    -------
    bool
        ``True`` if ``vector_end`` is counter-clockwise from ``vector_start``,
        otherwise ``False``.
    """
    return bool(np.cross(vector_start, vector_end)[-1] > 0)


def get_vecs_angle(
    vec_s: Vector3D,
    vec_e: Vector3D,
) -> float:
    """Compute the signed angle from *vec_s* to *vec_e*.

    The sign is determined by the cross product
    :math:`\\text{sign} = x_1 y_2 - x_2 y_1`:

    * ``> 0``: *vec_e* is counter-clockwise from *vec_s*.
    * ``< 0``: clockwise.
    * ``= 0``: collinear.

    Parameters
    ----------
    vec_s : np.ndarray
        Source vector ``(x1, y1)``.
    vec_e : np.ndarray
        Target vector ``(x2, y2)``.

    Returns
    -------
    float
        Signed angle in radians (positive counter-clockwise).
    """
    angle = np.arccos(
        np.true_divide(
            np.dot(vec_s, vec_e), np.linalg.norm(vec_s) * np.linalg.norm(vec_e)
        )
    )
    return float(angle) if is_counter_clockwise(vec_s, vec_e) else float(-angle)
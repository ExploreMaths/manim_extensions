# SPDX-FileCopyrightText: 2020 GarryBGoode
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Small vector and construction helpers shared by the CAD drawing utilities."""

from __future__ import annotations
import numpy as np
from manim.typing import Vector3D
from manim import (
    Circle,
    Line,
    TEAL,
    VDict,
    VGroup,
    VMobject,
)

__all__ = ["angle_between_vectors_signed", "BezierHandlebars"]


def angle_between_vectors_signed(v1: Vector3D, v2: Vector3D) -> float:
    """Return the signed angle between two vectors.

    Parameters
    ----------
    v1
        First vector.
    v2
        Second vector.

    Returns
    -------
        The rotation angle that aligns ``v1`` with ``v2``, in the range
        minus pi to pi.
    """
    cval = np.dot(v1, v2)
    sval = (np.cross(v1, v2))[2]
    return np.arctan2(sval, cval)


class BezierHandlebars(VDict):
    """
    Creates circles (dots) and lines on the points of another mobject.
    Used for visualizing bezier control points and handles, helps debugging.

    Parameters
    ----------
    target_mobject
        Mobject whose control points and handles are visualised.
    **kwargs
        Keyword arguments forwarded to the vector dictionary.
    """

    def __init__(self, target_mobject: VMobject, **kwargs) -> None:
        super().__init__(**kwargs)
        self.target = target_mobject
        self.generate_circles(0.03)
        self.generate_lines()

    def generate_circles(self, r: float) -> None:
        """Create a dot at every control point.

        Parameters
        ----------
        r
            Radius of the dots.

        Returns
        -------
            ``None``; the dots are stored under the ``"dots"`` key.
        """
        DotGroup = VGroup(
            *[
                Circle(
                    radius=r,
                    arc_center=p,
                    color=TEAL,
                    fill_opacity=1,
                    stroke_opacity=0,
                    num_components=4,
                )
                for p in self.target.points
            ]
        )
        self["dots"] = DotGroup

    def move_circles(self) -> None:
        """Move the dots onto the current control points.

        Returns
        -------
            ``None``; the dots are moved in place.
        """
        for zipthing in zip(self["dots"], self.target.points):
            zipthing[0].move_to(zipthing[1])

    def generate_lines(self) -> None:
        """Draw the two Bezier handles for every curve.

        Returns
        -------
            ``None``; the handles are stored under the ``"lines"`` key.
        """
        pointlist = zip(
            self.target.points[0::4, :],
            self.target.points[1::4, :],
            self.target.points[2::4, :],
            self.target.points[3::4, :],
        )
        LineGroup = VGroup(
            *[
                VGroup(
                    *[
                        Line(p[0], p[1], color=TEAL, stroke_width=2),
                        Line(p[2], p[3], color=TEAL, stroke_width=2),
                    ]
                )
                for p in pointlist
            ]
        )
        self["lines"] = LineGroup

    def move_lines(self) -> None:
        """Update the handle lines to match the current control points.

        Returns
        -------
            ``None``; the lines are repositioned in place.
        """
        pointlist = zip(
            self.target.points[0::4, :],
            self.target.points[1::4, :],
            self.target.points[2::4, :],
            self.target.points[3::4, :],
        )
        for zipthing in zip(self["lines"], pointlist):
            # Line.put_start_and_end_on()
            zipthing[0][0].put_start_and_end_on(zipthing[1][0], zipthing[1][1])
            zipthing[0][1].put_start_and_end_on(zipthing[1][2], zipthing[1][3])

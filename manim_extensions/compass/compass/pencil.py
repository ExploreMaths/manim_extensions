# SPDX-FileCopyrightText: 2026 jj-math
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Pencil class for Manim.

This module provides pencil visualization for geometry.

"""

from pathlib import Path

import numpy as np

from manim import Line, ORIGIN, PI, SVGMobject
from manim.typing import Point3D, Vector3D

__all__ = [
    "Pencil",
]


class Pencil(SVGMobject):
    """Pencil mobject.

    Parameters
    ----------
    height : float, optional
        Height of the pencil SVG. Defaults to ``2``.
    angle : float, optional
        Rotation angle of the pencil (in radians). Defaults to ``PI/4``.

    Examples
    --------
    .. manim:: PencilDocExample
       :save_last_frame:

       from manim import *
       from manim_extensions.compass import Pencil

       class PencilDocExample(Scene):
           def construct(self):
               pencil = Pencil(height=3.2)
               self.add(pencil, Dot(pencil.get_nib(), color=RED).scale(1.5))
    """

    def __init__(self, height: float = 2, angle: float = PI / 4) -> None:
        """Initialize the Pencil instance."""
        super().__init__(
            file_name=Path(__file__).resolve().parent / "assets/pencil.svg",
            height=height,
        )
        self.rotate(angle=-angle)
        self._nib = self.submobjects[3]

    def get_nib(self) -> Point3D:
        """Return the position of the nib.

        Returns
        -------
        numpy.ndarray
            The coordinates of the pencil nib (its writing tip).
        """
        return np.asarray(self._nib.get_all_points()[7])

    def get_nid_vector(self) -> Vector3D:
        """Return the direction of the pencil body.

        Returns
        -------
        numpy.ndarray
            Unit vector pointing from the nib towards the pencil body.
        """
        return Line(self.get_nib(), self.submobjects[1].get_center()).get_unit_vector()

    def move_nid_to(self, point: Point3D = ORIGIN) -> "Pencil":
        """Translate the pencil so that the nib moves to point.

        Parameters
        ----------
        point
            The point used by the operation.

        Returns
        -------
        Pencil
            The translated self.

        Examples
        --------
        .. manim:: MoveNidToDocExample
           :save_last_frame:

           from manim import *
           from manim_extensions.compass import Pencil

           class MoveNidToDocExample(Scene):
               def construct(self):
                   target = Dot(ORIGIN, color=RED).scale(1.5)
                   pencil = Pencil(height=3.2).move_nid_to(ORIGIN)
                   self.add(target, pencil)
        """
        self.shift(point - self.get_nib())
        return self
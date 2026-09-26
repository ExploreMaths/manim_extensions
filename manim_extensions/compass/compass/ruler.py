# SPDX-FileCopyrightText: 2026 jj-math
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Ruler class for Manim.

This module provides ruler visualization for geometry.

"""

from typing import Any

from manim import LEFT, Line, RIGHT, Rectangle, VGroup, WHITE
from manim.typing import Point3D, Vector3D
from manim.utils.color import ParsableManimColor

__all__ = [
    "Ruler",
]
import numpy as np

from ..utils.geometry_method import get_vecs_angle


class Ruler(VGroup):
    """Ruler mobject.

    Parameters
    ----------
    length : float, optional
        Length of the ruler. Defaults to ``12``.
    width : float, optional
        Width (height) of the ruler. Defaults to ``0.8``.
    ruler_color : ManimColor, optional
        Fill color of the ruler. Defaults to ``WHITE``.
    stroke_width : float, optional
        Stroke width of the ruler border. Defaults to ``2``.
    fill_opacity : float, optional
        Fill opacity of the ruler. Defaults to ``0.4``.
    **kwargs
        Forwarded to the parent :class:`~manim.mobject.types.vectorized_mobject.VGroup`.

    Examples
    --------
    .. manim:: RulerExample
       :save_last_frame:

       from manim import *
       from manim_extensions.compass import Ruler

       class RulerExample(Scene):
           def construct(self):
               ruler = Ruler()
               start, end = ruler.get_start_and_end()
               self.add(ruler, Dot(start, color=RED), Dot(end, color=RED))
    """

    def __init__(
        self,
        length: float = 12,
        width: float = 0.8,
        ruler_color: ParsableManimColor = WHITE,
        stroke_width: float = 2,
        fill_opacity: float = 0.4,
        **kwargs: Any,
    ) -> None:
        """Initialize the Ruler instance."""
        super().__init__(**kwargs)
        self.ruler_length = length
        self.ruler_width = width
        self.ruler_color = ruler_color
        self.ruler = Rectangle(
            height=self.ruler_width,
            width=self.ruler_length,
            color=self.ruler_color,
            stroke_width=stroke_width,
            fill_opacity=fill_opacity,
        )
        self.add(self.ruler)

    def get_vecs_of_ruler(self) -> tuple[Vector3D, Vector3D]:
        """Return the extension and width directions of the ruler.

        Returns
        -------
        tuple of numpy.ndarray
            Unit vector along the ruler's length and unit vector along the
            ruler's width.
        """
        A, B, C, _ = self.ruler.get_vertices()
        return Line(B, A).get_unit_vector(), Line(B, C).get_unit_vector()

    def get_direction_vector_of_ruler(self) -> Vector3D:
        """Return the extension direction of the ruler.

        Returns
        -------
        numpy.ndarray
            Unit vector along the ruler's length, pointing from its end
            towards its start.
        """
        s, e, *_ = self.ruler.get_vertices()
        return Line(e, s).get_unit_vector()

    def get_width_vector_of_ruler(self) -> Vector3D:
        """Return the width direction of the ruler.

        Returns
        -------
        numpy.ndarray
            Unit vector along the ruler's width.
        """
        _, s, e, _ = self.ruler.get_vertices()
        return Line(e, s).get_unit_vector()

    def get_start_and_end(self) -> tuple[Point3D, Point3D]:
        """Return the start and end points of the ruler.

        Returns
        -------
        tuple of numpy.ndarray
            The start point and end point of the ruler's length axis.
        """
        E, S, *_ = self.ruler.get_vertices()
        return S, E

    def get_middle_point(self) -> Point3D:
        """Return the midpoint of the ruler.

        Returns
        -------
        numpy.ndarray
            The midpoint between the ruler's start and end points.
        """
        S, E = self.get_start_and_end()
        return (S + E) / 2

    def get_length_of_ruler(self) -> float:
        """Return the length of the ruler.

        Returns
        -------
        float
            The distance between the ruler's start and end points.
        """
        S, E = self.get_start_and_end()
        return float(np.linalg.norm(E - S))

    def set_ruler(self, start: Point3D = LEFT, end: Point3D = RIGHT) -> "Ruler":
        """

        Place the ruler so that one of its edges aligns with start and end.
        Parameters
        ----------
        start
            Start point of the ruler placement.
        end
            End point of the ruler placement.
        
        Returns
        -------
        Ruler
            The repositioned self.
        
        Examples
        ----------

        .. manim:: SetRulerDocExample
           :save_last_frame:

           from manim import *
           from manim_extensions.compass import Ruler

           class SetRulerDocExample(Scene):
               def construct(self):
                   start, end = LEFT * 2 + DOWN, RIGHT * 2 + UP
                   self.add(Dot(start, color=RED), Dot(end, color=RED))
                   ruler = Ruler().set_ruler(start, end)
                   self.add(ruler)

        """
        direction = end - start
        current_pos = self.get_middle_point()
        target_pos = (start + end) / 2

        self.rotate(
            angle=get_vecs_angle(self.get_direction_vector_of_ruler(), direction),
            about_point=current_pos,
        ).shift(target_pos - current_pos)
        return self

    def put_ruler_flat(self) -> "Ruler":
        """Lay the ruler flat.

        Returns
        -------
        Ruler
            The flattened self.

        Examples
        --------
        .. manim:: PutRulerFlatDocExample
           :save_last_frame:

           from manim import *
           from manim_extensions.compass import Ruler

           class PutRulerFlatDocExample(Scene):
               def construct(self):
                   tilted = Ruler().rotate(PI / 5)
                   flat = Ruler().rotate(PI / 5).put_ruler_flat()
                   content = VGroup(tilted, flat)
                   content.arrange(DOWN, buff=0.8)
                   content.scale_to_fit_height(7).move_to(ORIGIN)
                   self.add(content)
        """
        self.rotate(angle=get_vecs_angle(self.get_direction_vector_of_ruler(), RIGHT))
        return self
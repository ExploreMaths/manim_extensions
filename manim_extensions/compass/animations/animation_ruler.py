# SPDX-FileCopyrightText: 2026 jj-math
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Ruler animations for Manim.

This module provides animations for ruler manipulations.

"""

__all__ = ["PutRuler", "PutRulerAway"]

from typing import Any

from manim import ApplyMethod, DOWN, LEFT, RIGHT, UP
from manim.typing import Point3D

from ..compass.ruler import Ruler


class PutRuler(ApplyMethod):
    """Compass-and-straightedge animation: rotate the ruler so that one of its edges aligns with start-end.

    .. manim:: PutRulerDocExample

       from manim import *
       from manim_extensions.compass import PutRuler, Ruler

       class PutRulerDocExample(Scene):
           def construct(self):
               ruler = Ruler().to_edge(DOWN)
               start, end = LEFT * 2, RIGHT * 2
               self.add(Dot(start, color=RED), Dot(end, color=RED))
               self.play(PutRuler(ruler, start, end))
               self.wait()

    Parameters
    ----------
        ruler : Ruler
            The ruler.
        start : Point
            The start point.
        end : Point
            The end point.
        **kwargs
            Additional keyword arguments forwarded to :class:`~.ApplyMethod`."""

    def __init__(
        self,
        ruler: Ruler,
        start: Point3D | None = None,
        end: Point3D | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize PutRuler."""
        super().__init__(ruler.set_ruler, start, end, **kwargs)


class PutRulerAway(PutRuler):
    """Put the ruler away: move the ruler to point.

    .. manim:: PutRulerAwayDocExample

       from manim import *
       from manim_extensions.compass import PutRuler, PutRulerAway, Ruler

       class PutRulerAwayDocExample(Scene):
           def construct(self):
               ruler = Ruler().to_edge(DOWN)
               self.play(PutRuler(ruler, LEFT * 2, RIGHT * 2))
               self.play(PutRulerAway(ruler, 3 * UP))
               self.wait()

    Parameters
    ----------
        ruler : Ruler
            The ruler.
        point : Point
            The placement position.
        is_flat : bool
            Whether to place it horizontally (or vertically).
        **kwargs
            Additional keyword arguments forwarded to :class:`~.ApplyMethod`."""

    def __init__(
        self,
        ruler: Ruler,
        point: Point3D | None = None,
        is_flat: bool = True,
        **kwargs: Any,
    ) -> None:
        """Initialize PutRulerAway."""
        assert point is not None
        if is_flat:
            start = point + LEFT
            end = point + RIGHT
        else:
            start = point + UP
            end = point + DOWN
        super().__init__(ruler, start, end, **kwargs)
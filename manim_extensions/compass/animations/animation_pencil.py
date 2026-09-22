# SPDX-FileCopyrightText: 2026 jj-math
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Pencil animations for Manim.

This module provides animations for pencil manipulations.

"""

from typing import Any

from manim import AnimationGroup, ApplyMethod, Create, MoveAlongPath, VMobject
from manim.typing import Point3D

__all__ = ["MovePencilAlongPath", "MovePencilTipTo", "DrawPath", "PutPencilAway"]

from ..compass.pencil import Pencil


class MovePencilAlongPath(MoveAlongPath):
    """Animation of the pencil nib moving along a given path.

    .. manim:: MovePencilAlongPathDocExample

       from manim import *
       from manim_extensions.compass import MovePencilAlongPath, Pencil

       class MovePencilAlongPathDocExample(Scene):
           def construct(self):
               pencil = Pencil().to_edge(LEFT)
               path = Line(LEFT * 2, RIGHT * 2, color=GREY)
               self.add(path)
               self.play(MovePencilAlongPath(pencil, path))
               self.wait()

    Parameters
    ----------
        mobject : Pencil
            The pencil.
        path : VMobject
            The target path.
        suspend_mobject_updating : Union[bool, None]
            Whether to suspend mobject updating.
        **kwargs
            Additional keyword arguments forwarded to :class:`~.MoveAlongPath`."""

    def __init__(
        self,
        mobject: Pencil,
        path: VMobject | None = None,
        suspend_mobject_updating: bool = False,
        **kwargs: Any,
    ) -> None:
        """Initialize MovePencilAlongPath."""
        assert path is not None
        start = path.get_start()
        path = path.copy().shift(mobject.get_center() - start)
        super().__init__(mobject, path, suspend_mobject_updating, **kwargs)


class MovePencilTipTo(ApplyMethod):
    """Move the pencil so that its nib is placed at point.

    .. manim:: MovePencilTipToDocExample

       from manim import *
       from manim_extensions.compass import MovePencilTipTo, Pencil

       class MovePencilTipToDocExample(Scene):
           def construct(self):
               pencil = Pencil().to_edge(LEFT)
               target = Dot(ORIGIN, color=RED)
               self.add(target)
               self.play(MovePencilTipTo(pencil, ORIGIN))
               self.wait()

    Parameters
    ----------
        pencil : Pencil
            The pencil.
        point : Point
            The target point.
        **kwargs
            Additional keyword arguments forwarded to :class:`~.ApplyMethod`."""

    def __init__(
        self, pencil: Pencil, point: Point3D | None = None, **kwargs: Any
    ) -> None:
        """Initialize MovePencilTipTo."""
        super().__init__(pencil.move_nid_to, point, **kwargs)


class DrawPath(AnimationGroup):
    """Animation of the pencil nib moving along the path while drawing it.

    .. manim:: DrawPathDocExample

       from manim import *
       from manim_extensions.compass import DrawPath, Pencil

       class DrawPathDocExample(Scene):
           def construct(self):
               pencil = Pencil().to_edge(LEFT)
               path = Square(side_length=2.5)
               self.play(DrawPath(pencil, path))
               self.wait()

    Parameters
    ----------
        pencil : Pencil
            The pencil.
        path : VMobject
            The path.
        **kwargs
            Additional keyword arguments forwarded to :class:`~.AnimationGroup`."""

    def __init__(
        self, pencil: Pencil, path: VMobject | None = None, **kwargs: Any
    ) -> None:
        """Initialize DrawPath."""
        assert path is not None
        super().__init__(Create(path), MovePencilAlongPath(pencil, path), **kwargs)


class PutPencilAway(MovePencilTipTo):
    """Put the pencil away: move the pencil to point.

    .. manim:: PutPencilAwayDocExample

       from manim import *
       from manim_extensions.compass import DrawPath, Pencil, PutPencilAway

       class PutPencilAwayDocExample(Scene):
           def construct(self):
               pencil = Pencil().to_edge(LEFT)
               line = Line(LEFT, RIGHT)
               self.play(DrawPath(pencil, line))
               self.play(PutPencilAway(pencil, 3 * DOWN))
               self.wait()

    Parameters
    ----------
        pencil : Pencil
            The pencil.
        point : Point
            The placement position.
        **kwargs
            Additional keyword arguments forwarded to :class:`~.ApplyMethod`."""

    def __init__(
        self, pencil: Pencil, point: Point3D | None = None, **kwargs: Any
    ) -> None:
        """Initialize PutPencilAway."""
        super().__init__(pencil, point, **kwargs)
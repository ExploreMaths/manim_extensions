# SPDX-FileCopyrightText: 2026 jj-math
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

""":class:`~manim_extensions.compass.compass.pencil.Pencil` animations for Manim.

This module provides animations for pencil manipulations.

"""

from typing import Any

from manim import AnimationGroup, ApplyMethod, Create, MoveAlongPath, VMobject
from manim.typing import Point3D

__all__ = ["MovePencilAlongPath", "MovePencilTipTo", "DrawPath", "PutPencilAway"]

from ..compass.pencil import Pencil


class MovePencilAlongPath(MoveAlongPath):
    """Animation of the pencil nib moving along a given path.

    Parameters
    ----------
        mobject
            The pencil.
        path
            The target path.
        suspend_mobject_updating
            Whether to suspend mobject updating.
        **kwargs
            Additional keyword arguments forwarded to :class:`~manim.animation.movement.MoveAlongPath`.

    Examples
    --------
    .. manim:: MovePencilAlongPathScene

       from manim import *
       from manim_extensions.compass import MovePencilAlongPath, Pencil

       class MovePencilAlongPathScene(Scene):
           def construct(self):
               pencil = Pencil().to_edge(LEFT)
               path = Line(LEFT * 2, RIGHT * 2, color=GREY)
               self.add(path)
               self.play(MovePencilAlongPath(pencil, path))
               self.wait()
    """

    def __init__(
        self,
        mobject: Pencil,
        path: VMobject | None = None,
        suspend_mobject_updating: bool = False,
        **kwargs: Any,
    ):
        assert path is not None
        start = path.get_start()
        path = path.copy().shift(mobject.get_center() - start)
        super().__init__(mobject, path, suspend_mobject_updating, **kwargs)


class MovePencilTipTo(ApplyMethod):
    """Move the pencil so that its nib is placed at point.

    Parameters
    ----------
        pencil
            The pencil.
        point
            The target point.
        **kwargs
            Additional keyword arguments forwarded to :class:`~manim.animation.transform.ApplyMethod`.

    Examples
    --------
    .. manim:: MovePencilTip

       from manim import *
       from manim_extensions.compass import MovePencilTipTo, Pencil

       class MovePencilTip(Scene):
           def construct(self):
               pencil = Pencil().to_edge(LEFT)
               target = Dot(ORIGIN, color=RED)
               self.play(MovePencilTipTo(pencil, ORIGIN))
               self.wait()
               content = VGroup(pencil, target)
               content.scale_to_fit_height(5).move_to(ORIGIN)
    """

    def __init__(self, pencil: Pencil, point: Point3D | None = None, **kwargs: Any):
        super().__init__(pencil.move_nid_to, point, **kwargs)


class DrawPath(AnimationGroup):
    """Animation of the pencil nib moving along the path while drawing it.

    Parameters
    ----------
        pencil
            The pencil.
        path
            The path.
        **kwargs
            Additional keyword arguments forwarded to :class:`~manim.animation.composition.AnimationGroup`.

    Examples
    --------
    .. manim:: DrawPathScene

       from manim import *
       from manim_extensions.compass import DrawPath, Pencil

       class DrawPathScene(Scene):
           def construct(self):
               pencil = Pencil().to_edge(LEFT)
               path = Square(side_length=2.5)
               self.play(DrawPath(pencil, path))
               self.wait()
    """

    def __init__(self, pencil: Pencil, path: VMobject | None = None, **kwargs: Any):
        assert path is not None
        super().__init__(Create(path), MovePencilAlongPath(pencil, path), **kwargs)


class PutPencilAway(MovePencilTipTo):
    """Put the pencil away: move the pencil to point.

    Parameters
    ----------
        pencil
            The pencil.
        point
            The placement position.
        **kwargs
            Additional keyword arguments forwarded to :class:`~manim.animation.transform.ApplyMethod`.

    Examples
    --------
    .. manim:: PutPencilAwayScene

       from manim import *
       from manim_extensions.compass import DrawPath, Pencil, PutPencilAway

       class PutPencilAwayScene(Scene):
           def construct(self):
               pencil = Pencil().to_edge(LEFT)
               line = Line(LEFT, RIGHT)
               self.play(DrawPath(pencil, line))
               self.play(PutPencilAway(pencil, 3 * DOWN))
               self.wait()
    """

    def __init__(self, pencil: Pencil, point: Point3D | None = None, **kwargs: Any):
        super().__init__(pencil, point, **kwargs)

__all__ = [
    'MovePencilAlongPath',
    'MovePencilTipTo',
    'DrawPath',
    'PutPencilAway'
]
from typing import Union
from manim.mobject.types.vectorized_mobject import VMobject
from manim.mobject.types.point_cloud_mobject import Point
from manim.animation.movement import MoveAlongPath
from manim.animation.composition import AnimationGroup
from manim.animation.creation import Create
from manim.animation.transform import ApplyMethod

from ..compass.pencil import Pencil

class MovePencilAlongPath(MoveAlongPath):
    """Animation of the pencil nib moving along a given path.

    .. manim:: MovePencilAlongPathDocExample

       from manim import *
       from manim_extensions.compass import Pencil, MovePencilAlongPath

       class MovePencilAlongPathDocExample(Scene):
           def construct(self):
               pencil = Pencil().to_edge(LEFT)
               path = Line(LEFT, RIGHT)
               self.play(MovePencilAlongPath(pencil, path))
               self.wait()

    Parameters
    ----------
        mobject : Pencil
            The pencil.
        path : VMobject
            The target path.
        suspend_mobject_updating : Union[bool, None]
            Whether to suspend mobject updating."""
    def __init__(
        self,
        mobject: Pencil,
        path: VMobject = None,
        suspend_mobject_updating: Union[bool, None] = False,
        **kwargs
    ) -> None:
        """Initialize MovePencilAlongPath."""
        start = path.get_start()
        path = path.copy().shift(mobject.get_center() - start)
        super().__init__(mobject, path, suspend_mobject_updating, **kwargs)

class MovePencilTipTo(ApplyMethod):
    """Move the pencil so that its nib is placed at point.

    .. manim:: MovePencilTipToDocExample

       from manim import *
       from manim_extensions.compass import Pencil, MovePencilTipTo

       class MovePencilTipToDocExample(Scene):
           def construct(self):
               pencil = Pencil().to_edge(LEFT)
               self.play(MovePencilTipTo(pencil, ORIGIN))
               self.wait()

    Parameters
    ----------
        pencil : Pencil
            The pencil.
        point : Point
            The target point."""
    def __init__(
        self,
        pencil: Pencil,
        point:Point = None,
        **kwargs
    ):
        """Initialize MovePencilTipTo."""
        super().__init__(
            pencil.move_nid_to,
            point,
            **kwargs
        )

class DrawPath(AnimationGroup):
    """Animation of the pencil nib moving along the path while drawing it.

    .. manim:: DrawPathDocExample

       from manim import *
       from manim_extensions.compass import Pencil, DrawPath

       class DrawPathDocExample(Scene):
           def construct(self):
               pencil = Pencil().to_edge(LEFT)
               path = Line(LEFT, RIGHT)
               self.play(DrawPath(pencil, path))
               self.wait()

    Parameters
    ----------
        pencil : Pencil
            The pencil.
        path : VMobject
            The path."""
    def __init__(
        self,
        pencil:Pencil,
        path: VMobject = None,
        **kwargs
    ):
        """Initialize DrawPath."""
        super().__init__(
            Create(path),
            MovePencilAlongPath(pencil,path),
            **kwargs
        )

class PutPencilAway(MovePencilTipTo):
    """Put the pencil away: move the pencil to point.

    .. manim:: PutPencilAwayDocExample

       from manim import *
       from manim_extensions.compass import Pencil, PutPencilAway

       class PutPencilAwayDocExample(Scene):
           def construct(self):
               pencil = Pencil().to_edge(LEFT)
               self.play(PutPencilAway(pencil, 2 * DOWN))
               self.wait()

    Parameters
    ----------
        pencil : Pencil
            The pencil.
        point : Point
            The placement position."""
    def __init__(
        self,
        pencil:Pencil,
        point:Point = None,
        **kwargs
    ):
        """Initialize PutPencilAway."""
        super().__init__(pencil,point,**kwargs)
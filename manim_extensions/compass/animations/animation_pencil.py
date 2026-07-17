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
    '''Animation of the pencil nib moving along a given path.'''
    def __init__(
        self,
        mobject: Pencil,
        path: VMobject = None,
        suspend_mobject_updating: Union[bool, None] = False,
        **kwargs
    ) -> None:
        '''
        Move the pencil along the given path, using the nib as the reference point.

        Args:
            mobject: The pencil.
            path: The target path.
            suspend_mobject_updating: Whether to suspend mobject updating.
        '''
        start = path.get_start()
        path = path.copy().shift(mobject.get_center() - start)
        super().__init__(mobject, path, suspend_mobject_updating, **kwargs)

class MovePencilTipTo(ApplyMethod):
    def __init__(
        self,
        pencil: Pencil,
        point:Point = None,
        **kwargs
    ):
        '''
        Move the pencil so that its nib is placed at point.

        Args:
            pencil: The pencil.
            point: The target point.
        '''
        super().__init__(
            pencil.move_nid_to,
            point,
            **kwargs
        )

class DrawPath(AnimationGroup):
    def __init__(
        self,
        pencil:Pencil,
        path: VMobject = None,
        **kwargs
    ):
        '''
        Animation of the pencil nib moving along the path while drawing it.
        
        Args:
            pencil: The pencil.
            path: The path.
        '''
        super().__init__(
            Create(path),
            MovePencilAlongPath(pencil,path),
            **kwargs
        )

class PutPencilAway(MovePencilTipTo):
    def __init__(
        self,
        pencil:Pencil,
        point:Point = None,
        **kwargs
    ):
        '''
        Put the pencil away: move the pencil to point.

        Args:
            pencil: The pencil.
            point: The placement position.
        '''
        super().__init__(pencil,point,**kwargs)
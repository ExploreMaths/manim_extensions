__all__ = [
    'DrawArc',
    'MoveNiddleTipTo',
    'RotateCompass',
    'SplitCompass',
    'PutCompass',
    'PutCompassAway'
]
# from manim import *
import numpy as np
from manim.mobject.geometry.arc import Arc
from manim.mobject.geometry.line import Line
from manim.mobject.types.point_cloud_mobject import Point
from manim.animation.composition import AnimationGroup
from manim.animation.transform import ApplyMethod
from manim.animation.rotation import Rotate
from manim.animation.creation import Create
from manim.constants import RIGHT, LEFT, UP, DOWN

from ..compass import Compass
from ..utils.geometry_method import (
    get_vecs_angle,
    get_distance,
    is_counter_clockwise
)

class DrawArc(AnimationGroup):
    def __init__(
        self,
        compass:Compass,
        arc:Arc,
        **kwargs
    ):
        '''
        Compass-and-straightedge animation: draw an arc.
        Note: before this animation, move the compass needle tip (niddle_tip)
        to the centre of the arc, and move the compass pen tip to the start
        of the arc.
        
        Args:
            compass: The compass.
            arc: The arc to draw.
        '''
        super().__init__(
            Create(arc),
            RotateCompass(compass,arc.angle),
            **kwargs
        )

class SplitCompass(AnimationGroup):
    def __init__(
        self,
        compass:Compass,
        span:float = None,
        **kwargs
    ):
        '''
        Compass-and-straightedge animation: rotate the two legs of the compass
        uniformly outward (or inward) so that the distance between the tips is span.
        The niddle_tip stays fixed.
        
        Args:
            compass: The compass.
            span: The distance between the two compass tips.
        '''
        theta_new, theta_old = np.arcsin(span/2/compass.leg_length), compass.theta
        compass.theta = theta_new
        rotate_angle = theta_old - theta_new
        if is_counter_clockwise(
            compass.get_niddle_tip() - compass.c.get_center(),
            compass.get_pen_tip() - compass.c.get_center()
        ):
            rotate_angle = -rotate_angle
        super().__init__(
            Rotate(
                compass.head,
                about_point = compass.c.get_center(),
                angle = rotate_angle
            ),
            Rotate(
                compass.pen_tip,
                about_point = compass.c.get_center(),
                angle = 2*rotate_angle
            ),
            **kwargs
        )

class RotateCompass(Rotate):
    def __init__(
        self,
        compass:Compass,
        angle:float = None,
        **kwargs
    ):
        '''
        Compass-and-straightedge animation: rotate the compass around its needle tip by angle.

        Args:
            compass: The compass.
            angle: The rotation angle.
        '''
        super().__init__(
            compass,
            about_point = compass.get_niddle_tip(),
            angle = angle,
            **kwargs
        )

class MoveNiddleTipTo(ApplyMethod):
    def __init__(
        self,
        compass:Compass,
        point:Point = None,
        **kwargs
    ):
        '''
        Compass-and-straightedge animation: move the compass so that its needle tip is placed at point.

        Args:
            compass: The compass.
            point: The target point.
        '''
        super().__init__(
            compass.move_niddle_tip_to,
            point,
            **kwargs
        )

class PutCompass(ApplyMethod):
    def __init__(
        self,
        compass:Compass,
        niddle_pos:Point = None,
        pen_pos:Point = None,
        **kwargs
    ):
        '''
        Compass-and-straightedge animation: place the compass's niddle_tip and pen_tip at the given positions.

        Args:
            compass: The compass.
            niddle_pos: Position for niddle_tip.
            pen_pos: Position for pen_tip.
        '''
        arc_radius = get_distance(niddle_pos,pen_pos)
        if arc_radius > compass.leg_length*2:
            raise ValueError("The span exceeds the compass drawing range.")
            
        span_angle = compass.get_compass_rotate_angle_with_span(arc_radius)
        rotate_angle = get_vecs_angle(
            compass.get_niddle2pen_vec(),
            Line(niddle_pos,pen_pos).get_unit_vector()
        )
        super().__init__(
            compass.set_compass,
            span_angle/2,
            rotate_angle,
            niddle_pos,
            **kwargs
        )

class PutCompassAway(PutCompass):
    def __init__(
        self,
        compass:Compass,
        point:Point = RIGHT,
        span_buff:float = 0.1,
        **kwargs
    ):
        '''
        Compass-and-straightedge animation: put the compass aside at point, with the two tips separated by span_buff.

        Args:
            compass: The compass.
            point: Position to place the compass.
            span_buff: Distance between the two tips when placed aside.
        '''
        r = 0.5*compass.leg_length
        vec = r*DOWN if compass.get_compass_rotate_angle_direction() else r*UP
        super().__init__(
            compass,
            niddle_pos = point + span_buff*LEFT + vec,
            pen_pos = point + span_buff*RIGHT + vec,
            **kwargs
        )
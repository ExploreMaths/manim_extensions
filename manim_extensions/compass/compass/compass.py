__all__ =[
    'Compass',
]
# from manim import *
import numpy as np
from manim.mobject.geometry.line import Line
from manim.mobject.geometry.arc import Circle
from manim.mobject.geometry.polygram import Polygon,Rectangle
from manim.mobject.types.point_cloud_mobject import Point
from manim.mobject.types.vectorized_mobject import VGroup
from manim.utils.color import *
from manim.constants import *

from ..utils.geometry_method import (
    get_distance,
    is_counter_clockwise
)

class Compass(VGroup):
    '''Compass mobject.

    .. manim:: CompassExample
        :save_last_frame:

        from manim_extensions.compass import Compass

        class CompassExample(Scene):
            def construct(self):
                compass = Compass().to_edge(LEFT)
                self.add(compass)
    '''
    def __init__(
        self,
        span = 1.5,
        head_color = WHITE,
        niddle_color = RED,
        pen_color = YELLOW,
        stroke_width = 2,
        leg_length = 3.1,
        leg_width = 0.12,
        r = 0.2,
        **kwargs
    ):
        super().__init__(
            stroke_width = stroke_width,
            **kwargs
        )
        self.head_color = head_color
        self.niddle_color = niddle_color
        self.pen_color = pen_color
        self.span = span
        self.leg_length = leg_length
        self.r = r
        self.leg_width = leg_width
        self._init_compass()

    def _init_compass(self):
        s, l, r, w = self.span, self.leg_length, self.r, self.leg_width
        self.theta = np.arcsin(s/2/l)

        self.c = Circle(
            radius = r,
            color = self.head_color,
            fill_opacity = 1
        )
        c2 = Circle(
            radius = 1.25*r,
            color = self.head_color,
            stroke_width = self.stroke_width
        )

        self.niddle_tip = Polygon(
            ORIGIN, l * RIGHT, (l - w*np.sqrt(3)) * RIGHT + w * DOWN, w * DOWN,
            stroke_width = 0,
            fill_color = self.niddle_color,
            fill_opacity = 0.75
        ).rotate(-PI/2 - self.theta, about_point = self.c.get_center())
        self.pen_tip = Polygon(
            ORIGIN, l * RIGHT, (l - w*np.sqrt(3)) * RIGHT + w * UP, w * UP,
            stroke_width = 0,
            fill_color = self.pen_color,
            fill_opacity = 0.75
        ).rotate(-PI/2 + self.theta, about_point = self.c.get_center())

        h = Rectangle(
            width = 0.5*r,
            height = 1.8*r,
            color = self.head_color,
            fill_opacity = 1
        ).next_to(self.c,UP,buff = 0)
        self.head = VGroup(h, self.c, c2)
        self.add(self.niddle_tip, self.pen_tip, self.head)
        self.move_to(ORIGIN)
        return self

    def get_niddle_tip(self):
        '''Return the coordinates of the needle tip.
        '''
        return self.niddle_tip.get_vertices()[1]

    def get_pen_tip(self):
        '''Return the coordinates of the pen tip.
        '''
        return self.pen_tip.get_vertices()[1]
    
    def get_niddle2pen_vec(self):
        '''Return the vector from the needle tip to the pen tip.
        '''
        return Line(
            self.get_niddle_tip(),
            self.get_pen_tip()
        ).get_unit_vector()
    
    def get_span(self):
        '''Return the compass span: distance between pen tip and needle tip.
        '''
        return get_distance(
            self.get_pen_tip(),
            self.get_niddle_tip()
        )

    def move_niddle_tip_to(self, pos:Point):
        '''Move the compass as a whole so that the needle tip is at pos.

        .. manim:: CompassMoveNiddleTipToDocExample
            :save_last_frame:

            from manim import *
            from manim_extensions.compass import Compass

            class CompassMoveNiddleTipToDocExample(Scene):
                def construct(self):
                    compass = Compass().move_niddle_tip_to(ORIGIN)
                    self.add(compass)
        '''
        self.shift(pos - self.get_niddle_tip())
        return self

    def rotate_about_niddle_tip(self, angle = PI/2):
        '''Rotate the compass as a whole around the needle tip by angle.

        .. manim:: RotateAboutNiddleTipDocExample
            :save_last_frame:

            from manim import *
            from manim_extensions.compass import Compass

            class RotateAboutNiddleTipDocExample(Scene):
                def construct(self):
                    compass = Compass().rotate_about_niddle_tip(PI / 4)
                    self.add(compass)
        '''
        self.rotate(
            angle = angle,
            about_point = self.get_niddle_tip()
        )
        return self

    def reverse_tip(self):
        '''Mirror-flip the needle tip and pen tip.

        .. manim:: ReverseTipDocExample
            :save_last_frame:

            from manim import *
            from manim_extensions.compass import Compass

            class ReverseTipDocExample(Scene):
                def construct(self):
                    compass = Compass().reverse_tip()
                    self.add(compass)
        '''
        self.flip(
            axis = self.head[0].get_end() - self.head[0].get_start(),
            about_point = self.c.get_center()
        )
        return self

    def split_copass_with_gain_angle(self,angle:float):
        '''Open the two compass legs by an additional angle.

        .. manim:: SplitCompassWithGainAngleDocExample
            :save_last_frame:

            from manim import *
            from manim_extensions.compass import Compass

            class SplitCompassWithGainAngleDocExample(Scene):
                def construct(self):
                    compass = Compass().split_copass_with_gain_angle(PI / 6)
                    self.add(compass)
        '''
        self.niddle_tip.rotate(
            angle = -angle,
            about_point = self.c.get_center()
        )
        self.pen_tip.rotate(
            angle = angle,
            about_point = self.c.get_center()
        )
        return self

    def split_compass_with_niddle_tip_fixed(
        self,
        angle:float,
        niddle_tip_pos:Point
    ):
        '''Keep the needle tip fixed and open the two compass legs by angle.

        .. manim:: SplitCompassWithNiddleTipFixedDocExample
            :save_last_frame:

            from manim import *
            from manim_extensions.compass import Compass

            class SplitCompassWithNiddleTipFixedDocExample(Scene):
                def construct(self):
                    compass = Compass().split_compass_with_niddle_tip_fixed(PI / 6, ORIGIN)
                    self.add(compass)
        '''
        self.split_copass_with_gain_angle(angle = angle)
        self.move_niddle_tip_to(niddle_tip_pos)
        return self
    
    def get_compass_rotate_angle_direction(self)->bool:
        '''Return whether the two compass legs are counter-clockwise from each other.
        '''
        return is_counter_clockwise(
            self.get_niddle_tip() - self.c.get_center(),
            self.get_pen_tip() - self.c.get_center()
        )

    def get_compass_rotate_angle_with_span(self,span:float)->float:
        '''Return the angle between the two legs when the compass is opened to span.
        '''
        L = self.leg_length
        distance = self.get_span()
        span_start = 2*L if distance > 2*L else distance
        span_res = np.arccos(1 - span_start*span_start/L/L/2) - np.arccos(1 - span*span/L/L/2)
        if self.get_compass_rotate_angle_direction():
            span_res = -span_res
        return span_res

    def set_compass(
        self,
        span_angle:float,
        rotate_angle:float,
        niddle_tip_pos:Point
    ):
        '''Set the compass span, rotation angle, and needle tip position.

        .. manim:: SetCompassDocExample
            :save_last_frame:

            from manim import *
            from manim_extensions.compass import Compass

            class SetCompassDocExample(Scene):
                def construct(self):
                    compass = Compass().set_compass(PI / 6, PI / 4, ORIGIN)
                    self.add(compass)
        '''
        self.split_compass_with_niddle_tip_fixed(span_angle,niddle_tip_pos)
        self.rotate(
            angle = rotate_angle,
            about_point = niddle_tip_pos
        )
        return self
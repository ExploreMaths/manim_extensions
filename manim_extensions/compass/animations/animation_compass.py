# SPDX-FileCopyrightText: 2026 jj-math
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


from manim import *

__all__ = [
    "DrawArc",
    "MoveNiddleTipTo",
    "RotateCompass",
    "SplitCompass",
    "PutCompass",
    "PutCompassAway",
]
import numpy as np

from ..compass import Compass
from ..utils.geometry_method import get_vecs_angle, get_distance, is_counter_clockwise


class DrawArc(AnimationGroup):
    """Compass-and-straightedge animation: draw an arc.

    .. manim:: DrawArcDocExample

       from manim import *
       from manim_extensions.compass import Compass, DrawArc
       from manim.mobject.geometry.arc import Arc

       class DrawArcDocExample(Scene):
           def construct(self):
               compass = Compass().to_edge(LEFT)
               arc = Arc(arc_center=ORIGIN, radius=1, angle=PI / 2)
               self.play(DrawArc(compass, arc))
               self.wait()

    Parameters
    ----------
        compass : Compass
            The compass.
        arc : Arc
            The arc to draw."""

    def __init__(self, compass: Compass, arc: Arc, **kwargs):
        """Initialize DrawArc."""
        super().__init__(Create(arc), RotateCompass(compass, arc.angle), **kwargs)


class SplitCompass(AnimationGroup):
    """Compass-and-straightedge animation: rotate the two legs of the compass

    .. manim:: SplitCompassDocExample

       from manim import *
       from manim_extensions.compass import Compass, SplitCompass

       class SplitCompassDocExample(Scene):
           def construct(self):
               compass = Compass().to_edge(LEFT)
               self.play(SplitCompass(compass, 2))
               self.wait()

    Parameters
    ----------
        compass : Compass
            The compass.
        span : float
            The distance between the two compass tips."""

    def __init__(self, compass: Compass, span: float = None, **kwargs):
        """Initialize SplitCompass."""
        theta_new, theta_old = np.arcsin(span / 2 / compass.leg_length), compass.theta
        compass.theta = theta_new
        rotate_angle = theta_old - theta_new
        if is_counter_clockwise(
            compass.get_niddle_tip() - compass.c.get_center(),
            compass.get_pen_tip() - compass.c.get_center(),
        ):
            rotate_angle = -rotate_angle
        super().__init__(
            Rotate(
                compass.head, about_point=compass.c.get_center(), angle=rotate_angle
            ),
            Rotate(
                compass.pen_tip,
                about_point=compass.c.get_center(),
                angle=2 * rotate_angle,
            ),
            **kwargs,
        )


class RotateCompass(Rotate):
    """Compass-and-straightedge animation: rotate the compass around its needle tip by angle.

    .. manim:: RotateCompassDocExample

       from manim import *
       from manim_extensions.compass import Compass, RotateCompass

       class RotateCompassDocExample(Scene):
           def construct(self):
               compass = Compass().to_edge(LEFT)
               self.play(RotateCompass(compass, PI / 2))
               self.wait()

    Parameters
    ----------
        compass : Compass
            The compass.
        angle : float
            The rotation angle."""

    def __init__(self, compass: Compass, angle: float = None, **kwargs):
        """Initialize RotateCompass."""
        super().__init__(
            compass, about_point=compass.get_niddle_tip(), angle=angle, **kwargs
        )


class MoveNiddleTipTo(ApplyMethod):
    """Compass-and-straightedge animation: move the compass so that its needle tip is placed at point.

    .. manim:: MoveNiddleTipToDocExample

       from manim import *
       from manim_extensions.compass import Compass, MoveNiddleTipTo

       class MoveNiddleTipToDocExample(Scene):
           def construct(self):
               compass = Compass().to_edge(LEFT)
               self.play(MoveNiddleTipTo(compass, ORIGIN))
               self.wait()

    Parameters
    ----------
        compass : Compass
            The compass.
        point : Point
            The target point."""

    def __init__(self, compass: Compass, point: Point = None, **kwargs):
        """Initialize MoveNiddleTipTo."""
        super().__init__(compass.move_niddle_tip_to, point, **kwargs)


class PutCompass(ApplyMethod):
    """Compass-and-straightedge animation: place the compass's niddle_tip and pen_tip at the given positions.

    .. manim:: PutCompassDocExample

       from manim import *
       from manim_extensions.compass import Compass, PutCompass

       class PutCompassDocExample(Scene):
           def construct(self):
               compass = Compass().to_edge(LEFT)
               self.play(PutCompass(compass, ORIGIN, 2 * RIGHT))
               self.wait()

    Parameters
    ----------
        compass : Compass
            The compass.
        niddle_pos : Point
            Position for niddle_tip.
        pen_pos : Point
            Position for pen_tip."""

    def __init__(
        self,
        compass: Compass,
        niddle_pos: Point = None,
        pen_pos: Point = None,
        **kwargs,
    ):
        """Initialize PutCompass."""
        arc_radius = get_distance(niddle_pos, pen_pos)
        if arc_radius > compass.leg_length * 2:
            raise ValueError("The span exceeds the compass drawing range.")

        span_angle = compass.get_compass_rotate_angle_with_span(arc_radius)
        rotate_angle = get_vecs_angle(
            compass.get_niddle2pen_vec(), Line(niddle_pos, pen_pos).get_unit_vector()
        )
        super().__init__(
            compass.set_compass, span_angle / 2, rotate_angle, niddle_pos, **kwargs
        )


class PutCompassAway(PutCompass):
    """Compass-and-straightedge animation: put the compass aside at point, with the two tips separated by span_buff.

    .. manim:: PutCompassAwayDocExample

       from manim import *
       from manim_extensions.compass import Compass, PutCompassAway

       class PutCompassAwayDocExample(Scene):
           def construct(self):
               compass = Compass().to_edge(LEFT)
               self.play(PutCompassAway(compass, 2 * RIGHT))
               self.wait()

    Parameters
    ----------
        compass : Compass
            The compass.
        point : Point
            Position to place the compass.
        span_buff : float
            Distance between the two tips when placed aside."""

    def __init__(
        self, compass: Compass, point: Point = RIGHT, span_buff: float = 0.1, **kwargs
    ):
        """Initialize PutCompassAway."""
        r = 0.5 * compass.leg_length
        vec = r * DOWN if compass.get_compass_rotate_angle_direction() else r * UP
        super().__init__(
            compass,
            niddle_pos=point + span_buff * LEFT + vec,
            pen_pos=point + span_buff * RIGHT + vec,
            **kwargs,
        )

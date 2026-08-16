# SPDX-FileCopyrightText: 2026 jj-math
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


__all__ = [
    'CompassScene'
]
# from manim import *
from typing import List

from manim.mobject.geometry.line import Line
from manim.mobject.geometry.arc import Arc
from manim.mobject.types.point_cloud_mobject import Point
from manim.animation.animation import Animation
from manim.animation.composition import AnimationGroup
from manim.animation.rotation import Rotate
from manim.animation.creation import Create
from manim.scene.moving_camera_scene import MovingCameraScene
from manim.utils.rate_functions import linear
from manim.utils.color.manim_colors import YELLOW
from manim.constants import *

from ..compass import Compass,Ruler,Pencil
from ..animations import *
from ..utils.geometry_method import (
    get_distance,
    get_vecs_angle
)

class CompassScene(MovingCameraScene):
    """A scene equipped with a compass, ruler, and pencil. Mainly implements
    compass placement, arc drawing, and ruler/pencil animations.

    Examples
    --------
    .. manim:: CompassSceneExample
       :save_last_frame:

       from manim import *
       from manim_extensions.compass import CompassScene

       class CompassSceneExample(CompassScene):
           def construct(self):
               self.compass_move_niddle_tip_to(ORIGIN)
               self.compass_split_span(2)
    """

    def setup(self) -> None:
        """CompassScene.setup example.
        """
        self.compass = Compass(span = 0.5).to_edge(LEFT)
        self.ruler = Ruler().to_edge(DOWN)
        self.pencil = Pencil().to_corner(UR)

    def compass_move_niddle_tip_to(self, pos: Point = ORIGIN, run_time: float = 1) -> None:
        """Move the compass needle tip to a target position.

        Parameters
        ----------
        pos
            Target position for the needle tip.
        run_time
            Duration of the animation.
        """
        self.play(
            self.compass.animate.move_niddle_tip_to(pos),
            # MoveNiddleTipTo(self.compass,pos),
            run_time = run_time
        )

    def rotate_compass_about_niddle_tip(
        self,
        angle_or_arc: float | Arc,
        arc: Arc | None = None,
        added_anims: List[Animation] | None = None,
        **kwargs: object,
    ) -> None:
        """Rotate the compass about its needle tip.

        Parameters
        ----------
        angle_or_arc : float or Arc
            Angle to rotate by, or an arc whose angle should be used.
        arc : Arc, optional
            Arc to draw as part of the rotation animation.
        added_anims : list[Animation], optional
            Additional animations to combine with the rotation.
        """
        anims = [
            Rotate(
                self.compass,
                about_point = self.compass.get_niddle_tip(),
                angle = angle_or_arc.angle if isinstance(angle_or_arc,Arc) else angle_or_arc
            ),
            # RotateCompass(self.compass,angle = angle_or_arc.angle if isinstance(angle_or_arc,Arc) else angle_or_arc)
        ]
        if added_anims is not None:
            anims.extend(added_anims)
        if isinstance(angle_or_arc,Arc):
            anims.append(Create(angle_or_arc))
        self.play(*anims, **kwargs)

    def compass_split_span(self, span: float = 3, run_time: float = 1) -> None:
        """Open both compass legs so the distance between tips equals ``span``.

        Parameters
        ----------
        span
            Target distance between the compass tips.
        run_time
            Duration of the opening animation.
        """
        self.play(
            SplitCompass(self.compass,span = span),
            run_time = run_time,
            rate_func = linear
        )

    def split_cmpass_span(self, span: float = 1, run_time: float = 1) -> None:
        """Adjust the pen tip while holding the needle fixed to reach a span.

        Parameters
        ----------
        span
            Desired distance between the compass tips.
        run_time
            Duration of the animation.
        """
        angle = self.compass.get_compass_rotate_angle_with_span(span)
        self.play(
            self.compass.animate.split_compass_with_niddle_tip_fixed(
                angle/2,
                self.compass.get_niddle_tip()
            ),
            run_time = run_time
        )

    def set_compass(
        self,
        niddle_pos: Point | None = None,
        pen_pos: Point | None = None,
        run_time: float = 1.0,
    ) -> None:
        """
        Place the compass at the specified positions: move niddle_tip to niddle_pos and pen_tip to pen_pos.

        Parameters
        ----------
        niddle_pos : Point
            target position for the compass needle tip (niddle_tip)
        pen_pos : Point
            target position for the compass pen tip (pen_tip)
        """
        self.play(
            PutCompass(
                self.compass,
                niddle_pos = niddle_pos,
                pen_pos = pen_pos,
            ),
            run_time = run_time
        )

    def draw_arc(
        self,
        niddle_point: Point = ORIGIN,
        pen_point: Point = RIGHT,
        angle: float = PI / 3,
        move_time: float = 1.0,
        wait_time: float = 1.0,
        run_time: float = 1.0,
        arc_color: object | None = None,
        **kwargs: object,
    ) -> Arc:
        """
        Draw an arc with the compass. The arc radius is computed from niddle_point and pen_point.

        Parameters
        ----------
        niddle_point
            centre of the arc
        pen_point
            starting point of the arc
        angle
            central angle of the arc
        move_time
            time to move the compass into position
        run_time
            time to draw the arc
        wait_time
            wait time between the two animations
        arc_color
            colour of the arc
        kwargs
            other keyword arguments for the arc
        return
            The drawn arc
        """
        self.set_compass(
            niddle_point,
            pen_point,
            run_time = move_time
        )
        if wait_time > 0:
            self.wait(wait_time)
        arc_radius = get_distance(niddle_point,pen_point)
        arc = Arc(
            arc_center = niddle_point,
            radius = arc_radius,
            start_angle = get_vecs_angle(RIGHT,self.compass.get_niddle2pen_vec()),
            angle = angle,
            color = self.compass.pen_tip.get_color() if arc_color is None else arc_color,
            **kwargs
        )
        self.play(
            DrawArc(
                self.compass,
                arc,
            ),
            run_time = run_time
        )
        return arc
    
    def flip_compass(self, run_time: float = 1) -> None:
        """Flip the compass, swapping the needle and pen tips.

        Parameters
        ----------
        run_time : float
            Duration of the flip animation in seconds.
        """
        self.play(
            self.compass.animate.reverse_tip(),
            run_time = run_time
        )

    def put_compass_aside(
        self,
        aside_pos: Point = RIGHT,
        span_buff: float = 0.1,
        run_time: float = 1.0,
    ) -> None:
        """
        Put the compass aside.

        Parameters
        ----------
        aside_pos : Point
            position to place the compass
        span_buff : float
            distance between the two compass tips when placed aside
        run_time : float
            time required to place the compass
        """
        r = 0.5*self.compass.leg_length
        vec = r*DOWN if self.compass.get_compass_rotate_angle_direction() else r*UP
        self.set_compass(
            niddle_pos = aside_pos + span_buff*LEFT + vec ,
            pen_pos = aside_pos + span_buff*RIGHT + vec,
            run_time = run_time
        )
    
    def set_ruler(
        self,
        start: Point | None = None,
        end: Point | None = None,
        lag_ratio: float = 0.5,
        run_time: float = 1.0,
        with_pencil: bool = True,
    ) -> None:
        """
        Place the ruler so that one of its edges aligns with start and end.

        Parameters
        ----------
        start : Point
            start point of the ruler placement
        end : Point
            end point of the ruler placement
        lag_ratio : float
            lag ratio between the ruler and pencil placement animations
        run_time : float
            time to place the ruler
        with_pencil : bool
            whether to place the pencil at the same time
        """
        if with_pencil:
            self.play(
                AnimationGroup(
                    PutRuler(self.ruler,start = start,end = end),
                    MovePencilTipTo(self.pencil,start),
                    lag_ratio = lag_ratio
                ),
                run_time = run_time
            )
        else:
            self.play(
                PutRuler(self.ruler,start = start,end = end),
                run_time = run_time
            )

    def set_pencil(self, pos: Point, run_time: float = 1.0) -> None:
        """Move the pencil nib to the specified position.

        Parameters
        ----------
        pos : Point
            Target position for the pencil nib.
        run_time : float
            Duration of the move animation in seconds.
        """
        self.play(
            self.pencil.animate.move_nid_to(pos),
            # MovePencilTipTo(self.pencil,pos),
            run_time = run_time
        )

    def draw_line(
        self,
        start: Point | None = None,
        end: Point | None = None,
        run_time: float = 1.0,
        with_pencil: bool = True,
        color: object = YELLOW,
        **kwargs: object,
    ) -> Line:
        """Draw a straight line using the ruler and pencil.

        Parameters
        ----------
        start : Point
            Start point of the line.
        end : Point
            End point of the line.
        run_time : float
            Duration of the drawing animation in seconds.
        with_pencil : bool
            If ``True``, animate the pencil tracing the line.  Otherwise
            the line is simply created with :class:`~manim.animation.creation.Create`.
        color : object
            Color of the drawn line.

        Returns
        -------
        Line
            The drawn line segment.
        """
        self.set_ruler(start = start,end = end,run_time = 0.5*run_time,with_pencil = with_pencil)
        line = Line(start,end,color = color,**kwargs)
        if with_pencil:
            self.play(
                DrawPath(self.pencil,line),
                run_time = 0.5*run_time
            )
        else:
            self.play(
                Create(line),
                run_time = 0.5*run_time
            )
        return line
    
    def put_pencil_away(self, pos: Point = 3 * DOWN, run_time: float = 1) -> None:
        """Translate the pencil as a whole to the specified position.

        Parameters
        ----------
        pos : Point
            Target position for the pencil.
        run_time : float
            Duration of the translation animation in seconds.
        """
        curr_pos = self.pencil.get_center()
        self.play(
            self.pencil.animate.shift(pos - curr_pos),
            run_time = run_time
        )

    def put_ruler_aside(
        self,
        aside_pos: Point = 3 * DOWN,
        horizontal_or_vertical: bool = True,
        run_time: float = 1.0,
    ) -> None:
        """Put the ruler aside at the specified position.

        The ruler is first rotated to a horizontal or vertical orientation
        (whichever aligns with *aside_pos*), then translated to that position.

        Parameters
        ----------
        aside_pos : Point
            Target position for the ruler.
        horizontal_or_vertical : bool
            If ``True``, align the ruler horizontally; otherwise vertically.
        run_time : float
            Total duration of the put-away animation in seconds.
        """
        vec_w = self.ruler.get_direction_vector_of_ruler()
        vec = RIGHT if horizontal_or_vertical else DOWN
        self.play(
            Rotate(
                self.ruler,
                about_point = self.ruler.get_center(),
                angle = get_vecs_angle(vec_w,vec)
            ),
            run_time = 0.35*run_time
        )
        self.play(
            self.ruler.animate.move_to(aside_pos),
            run_time = 0.65*run_time
        )
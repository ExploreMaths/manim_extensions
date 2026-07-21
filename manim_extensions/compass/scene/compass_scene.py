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
    '''
    A scene equipped with a compass, ruler, and pencil. Mainly implements
    compass placement, arc drawing, and ruler/pencil animations.

    .. manim:: CompassSceneDocExample

        from manim import *
        from manim_extensions.compass import CompassScene

        class CompassSceneDocExample(CompassScene):
            def construct(self):
                self.draw_arc(ORIGIN, RIGHT, PI / 2)
                self.wait()
    '''
    def setup(self):
        '''CompassScene.setup example.

        .. manim:: CompassSceneSetupDocExample
            :save_last_frame:

            from manim import *
            from manim_extensions.compass import CompassScene

            class CompassSceneSetupDocExample(CompassScene):
                def setup(self):
                    super().setup()
                    self.compass.move_to(ORIGIN)

                def construct(self):
                    self.wait()
        '''
        self.compass = Compass(span = 0.5).to_edge(LEFT)
        self.ruler = Ruler().to_edge(DOWN)
        self.pencil = Pencil().to_corner(UR)

    def compass_move_niddle_tip_to(self,pos = ORIGIN,run_time = 1):
        '''Move the compass needle tip to pos.

        .. manim:: CompassSceneMoveNiddleTipToDocExample

            from manim import *
            from manim_extensions.compass import CompassScene

            class CompassSceneMoveNiddleTipToDocExample(CompassScene):
                def construct(self):
                    self.compass_move_niddle_tip_to(ORIGIN)
                    self.wait()
        '''
        self.play(
            self.compass.animate.move_niddle_tip_to(pos),
            # MoveNiddleTipTo(self.compass,pos),
            run_time = run_time
        )

    def rotate_compass_about_niddle_tip(
        self,
        angle_or_arc:float | Arc,
        arc:Arc = None,
        added_anims:List[Animation] = None,
        **kwargs
    ):
        '''
        Rotate angle around the compass needle tip (niddle_tip).

        .. manim:: RotateCompassAboutNiddleTipDocExample

            from manim import *
            from manim_extensions.compass import CompassScene

            class RotateCompassAboutNiddleTipDocExample(CompassScene):
                def construct(self):
                    self.rotate_compass_about_niddle_tip(PI / 2)
                    self.wait()
        '''
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

    def compass_split_span(self,span = 3,run_time = 1):
        '''Rotate the two compass legs uniformly outward/inward so the opened distance equals span.

        .. manim:: CompassSplitSpanDocExample

            from manim import *
            from manim_extensions.compass import CompassScene

            class CompassSplitSpanDocExample(CompassScene):
                def construct(self):
                    self.compass_split_span(2)
                    self.wait()
        '''
        self.play(
            SplitCompass(self.compass,span = span),
            run_time = run_time,
            rate_func = linear
        )

    def split_cmpass_span(self,span = 1,run_time = 1):
        '''
        Fix niddle_tip, then move pen_tip along the line through niddle_tip and pen_tip to reach the given span.

        .. manim:: SplitCmpassSpanDocExample

            from manim import *
            from manim_extensions.compass import CompassScene

            class SplitCmpassSpanDocExample(CompassScene):
                def construct(self):
                    self.split_cmpass_span(2)
                    self.wait()
        '''
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
        niddle_pos:Point = None,
        pen_pos:Point = None,
        run_time:float = 1.0
    ):
        '''
        Place the compass at the specified positions: move niddle_tip to niddle_pos and pen_tip to pen_pos.

        args
            niddle_pos: target position for the compass needle tip (niddle_tip)
            pen_pos: target position for the compass pen tip (pen_tip)

        .. manim:: CompassSceneSetCompassDocExample

            from manim import *
            from manim_extensions.compass import CompassScene

            class CompassSceneSetCompassDocExample(CompassScene):
                def construct(self):
                    self.set_compass(ORIGIN, 2 * RIGHT)
                    self.wait()
        '''
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
        niddle_point = ORIGIN,
        pen_point = RIGHT,
        angle = PI/3,
        move_time = 1.0,
        wait_time = 1.0,
        run_time = 1.0,
        arc_color = None,
        **kwargs
    )-> Arc:
        '''
        Draw an arc with the compass. The arc radius is computed from niddle_point and pen_point.

        args
            niddle_point : centre of the arc
            pen_point : starting point of the arc
            angle : central angle of the arc
            move_time : time to move the compass into position
            run_time : time to draw the arc
            wait_time : wait time between the two animations
            arc_color : colour of the arc
            kwargs : other keyword arguments for the arc
        return
            The drawn arc

        .. manim:: CompassSceneDrawArcDocExample

            from manim import *
            from manim_extensions.compass import CompassScene

            class CompassSceneDrawArcDocExample(CompassScene):
                def construct(self):
                    self.draw_arc(ORIGIN, RIGHT, PI / 2)
                    self.wait()
        '''
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
    
    def flip_compass(self,run_time = 1):
        '''Flip the compass.

        .. manim:: FlipCompassDocExample

            from manim import *
            from manim_extensions.compass import CompassScene

            class FlipCompassDocExample(CompassScene):
                def construct(self):
                    self.flip_compass()
                    self.wait()
        '''
        self.play(
            self.compass.animate.reverse_tip(),
            run_time = run_time
        )

    def put_compass_aside(
        self,
        aside_pos:Point = RIGHT,
        span_buff:float = 0.1,
        run_time:float = 1.0
    ):
        '''
        Put the compass aside.

        args
            aside_pos: position to place the compass
            span_buff: distance between the two compass tips when placed aside
            run_time: time required to place the compass

        .. manim:: PutCompassAsideDocExample

            from manim import *
            from manim_extensions.compass import CompassScene

            class PutCompassAsideDocExample(CompassScene):
                def construct(self):
                    self.put_compass_aside(2 * RIGHT)
                    self.wait()
        '''
        r = 0.5*self.compass.leg_length
        vec = r*DOWN if self.compass.get_compass_rotate_angle_direction() else r*UP
        self.set_compass(
            niddle_pos = aside_pos + span_buff*LEFT + vec ,
            pen_pos = aside_pos + span_buff*RIGHT + vec,
            run_time = run_time
        )
    
    def set_ruler(
        self,
        start:Point = None,
        end:Point = None,
        lag_ratio:float = 0.5,
        run_time:float = 1.0,
        with_pencil:bool = True
    ):
        '''
        Place the ruler so that one of its edges aligns with start and end.

        args
            start: start point of the ruler placement
            end: end point of the ruler placement
            lag_ratio: lag ratio between the ruler and pencil placement animations
            run_time: time to place the ruler
            with_pencil: whether to place the pencil at the same time

        .. manim:: CompassSceneSetRulerDocExample

            from manim import *
            from manim_extensions.compass import CompassScene

            class CompassSceneSetRulerDocExample(CompassScene):
                def construct(self):
                    self.set_ruler(LEFT, RIGHT, with_pencil=False)
                    self.wait()
        '''
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

    def set_pencil(self,pos,run_time = 1.0):
        '''Move the pencil nib to the specified position.

        .. manim:: SetPencilDocExample

            from manim import *
            from manim_extensions.compass import CompassScene

            class SetPencilDocExample(CompassScene):
                def construct(self):
                    self.set_pencil(ORIGIN)
                    self.wait()
        '''
        self.play(
            self.pencil.animate.move_nid_to(pos),
            # MovePencilTipTo(self.pencil,pos),
            run_time = run_time
        )

    def draw_line(
        self,
        start:Point = None,
        end:Point = None,
        run_time:float = 1.0,
        with_pencil:bool = True,
        color = YELLOW,
        **kwargs
    )-> Line:
        '''Draw a straight line using the ruler.

        .. manim:: DrawLineDocExample

            from manim import *
            from manim_extensions.compass import CompassScene

            class DrawLineDocExample(CompassScene):
                def construct(self):
                    self.draw_line(LEFT, RIGHT)
                    self.wait()
        '''
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
    
    def put_pencil_away(self,pos = 3*DOWN,run_time = 1):
        '''Translate the pencil as a whole to the specified position.

        .. manim:: CompassScenePutPencilAwayDocExample

            from manim import *
            from manim_extensions.compass import CompassScene

            class CompassScenePutPencilAwayDocExample(CompassScene):
                def construct(self):
                    self.put_pencil_away(2 * DOWN)
                    self.wait()
        '''
        curr_pos = self.pencil.get_center()
        self.play(
            self.pencil.animate.shift(pos - curr_pos),
            run_time = run_time
        )

    def put_ruler_aside(
        self,
        aside_pos:Point = 3*DOWN,
        horizontal_or_vertical:bool = True,
        run_time:float = 1.0
    ):
        '''
        Put the ruler aside at aside_pos.

        args
            aside_pos: position where the ruler will be placed
            horizontal_or_vertical: whether to place it horizontally
            run_time: time required to place the ruler

        .. manim:: PutRulerAsideDocExample

            from manim import *
            from manim_extensions.compass import CompassScene

            class PutRulerAsideDocExample(CompassScene):
                def construct(self):
                    self.put_ruler_aside(2 * DOWN)
                    self.wait()
        '''
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
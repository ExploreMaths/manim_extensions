__all__ =[
    "get_arc",
]
import numpy as np
from manim.mobject.geometry.arc import Arc
from manim.constants import RIGHT
from manim.utils.color.manim_colors import YELLOW

def get_arc(
    niddle_pos:np.ndarray,
    pen_pos:np.ndarray,
    angle:float,
    color = YELLOW,
    **kwargs
)-> Arc:
    '''
    Construct an arc from its centre and starting point.

    Parameters
    ----------
    niddle_pos : np.ndarray
        centre of the arc
    pen_pos : np.ndarray
        starting point of the arc
    angle : float
        central angle of the arc
    color
        colour of the arc
    kwargs
        other keyword arguments for the arc

    Returns:
        The constructed Arc instance

    .. manim:: GetArcDocExample
        :save_last_frame:

        from manim import *
        from manim_extensions.compass import get_arc

        class GetArcDocExample(Scene):
            def construct(self):
                arc = get_arc(ORIGIN, RIGHT, PI / 2)
                self.add(arc)
    '''
    arc_radius = get_distance(niddle_pos,pen_pos)
    vec_s = pen_pos - niddle_pos
    return Arc(
        arc_center = niddle_pos,
        radius = arc_radius,
        start_angle = get_vecs_angle(RIGHT,vec_s),
        angle = angle,
        color = color,
        **kwargs
    )

def get_distance(
    point_start:np.ndarray,
    point_end:np.ndarray
)-> float:
    """Compute the distance between two points.

    .. manim:: GetDistanceDocExample
        :save_last_frame:

        from manim import *
        from manim_extensions.compass import get_distance

        class GetDistanceDocExample(Scene):
            def construct(self):
                d = get_distance(ORIGIN, RIGHT)
                label = Text(f"distance={d:.2f}")
                self.add(Dot(ORIGIN), Dot(RIGHT), Line(ORIGIN, RIGHT), label)
    """
    return np.linalg.norm(point_start - point_end)

def is_counter_clockwise(
    vector_start:np.ndarray,
    vector_end:np.ndarray
)-> bool:
    """Return whether vector_end is counter-clockwise from vector_start.

    .. manim:: IsCounterClockwiseDocExample
        :save_last_frame:

        from manim import *
        from manim_extensions.compass import is_counter_clockwise

        class IsCounterClockwiseDocExample(Scene):
            def construct(self):
                result = is_counter_clockwise(RIGHT, UP)
                label = Text(f"ccw={result}")
                self.add(Arrow(ORIGIN, RIGHT), Arrow(ORIGIN, UP), label)
    """
    return np.cross(vector_start,vector_end)[-1] > 0

def get_vecs_angle(
    vec_s:np.ndarray,
    vec_e:np.ndarray
)-> float:
    """
    Compute the angle from vector vec_s = (x1,y1) to vec_e = (x2,y2).

    Distinguishes clockwise vs counter-clockwise (sign = x1*y2 - x2*y1):
        sign > 0: vec_e is counter-clockwise from vec_s;
        sign < 0: clockwise;
        sign = 0: collinear

    .. manim:: GetVecsAngleDocExample
        :save_last_frame:

        from manim import *
        from manim_extensions.compass import get_vecs_angle

        class GetVecsAngleDocExample(Scene):
            def construct(self):
                angle = get_vecs_angle(RIGHT, UP)
                label = Text(f"angle={angle:.2f}")
                self.add(Arrow(ORIGIN, RIGHT), Arrow(ORIGIN, UP), label)
    """
    angle = np.arccos(
        np.true_divide(
            np.dot(vec_s,vec_e),
            np.linalg.norm(vec_s) * np.linalg.norm(vec_e)
        )
    )
    return angle if is_counter_clockwise(vec_s,vec_e) else -angle
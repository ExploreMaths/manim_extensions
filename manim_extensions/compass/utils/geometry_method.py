__all__ =[
    "get_arc",
]
import numpy as np
from manim.mobject.geometry.arc import Arc
from manim.constants import RIGHT
from manim.utils.color.manim_colors import YELLOW

def get_arc(
    niddle_pos: np.ndarray,
    pen_pos: np.ndarray,
    angle: float,
    color: object = YELLOW,
    **kwargs: object,
) -> Arc:
    """
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
    """
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
    point_start: np.ndarray,
    point_end: np.ndarray,
) -> float:
    """Compute the distance between two points.

    Parameters
    ----------
    point_start : np.ndarray
    The point used by the operation.
    point_end : np.ndarray
    The point used by the operation.
    """
    return np.linalg.norm(point_start - point_end)

def is_counter_clockwise(
    vector_start: np.ndarray,
    vector_end: np.ndarray,
) -> bool:
    """Return whether vector_end is counter-clockwise from vector_start.

    Parameters
    ----------
    vector_start : np.ndarray
        Starting vector used as the reference direction for the orientation test.
    vector_end : np.ndarray
        Ending vector whose orientation relative to the starting vector is evaluated.
    """
    return np.cross(vector_start,vector_end)[-1] > 0

def get_vecs_angle(
    vec_s: np.ndarray,
    vec_e: np.ndarray,
) -> float:
    """Compute the signed angle from *vec_s* to *vec_e*.

    The sign is determined by the cross product
    :math:`\\text{sign} = x_1 y_2 - x_2 y_1`:

    * ``> 0``: *vec_e* is counter-clockwise from *vec_s*.
    * ``< 0``: clockwise.
    * ``= 0``: collinear.

    Parameters
    ----------
    vec_s : np.ndarray
        Source vector ``(x1, y1)``.
    vec_e : np.ndarray
        Target vector ``(x2, y2)``.

    Returns
    -------
    float
        Signed angle in radians (positive counter-clockwise).
    """
    angle = np.arccos(
        np.true_divide(
            np.dot(vec_s,vec_e),
            np.linalg.norm(vec_s) * np.linalg.norm(vec_e)
        )
    )
    return angle if is_counter_clockwise(vec_s,vec_e) else -angle
from manim import *
import math
import numpy as np
from typing import Optional, Tuple, Union


def CircleInt(
    circle1: Circle, circle2: Circle
) -> Optional[Tuple[list[float], list[float]]]:
    """Compute the intersection points of two circles.

    Solves the geometric intersection of two circles in the XY‑plane.

    Parameters
    ----------
    circle1 : :class:`~manim.mobject.geometry.Circle`
        The first circle.
    circle2 : :class:`~manim.mobject.geometry.Circle`
        The second circle.

    Returns
    -------
    Optional[Tuple[list[float], list[float]]]
        A tuple ``(point1, point2)`` where each point is ``[x, y, 0]`` if the
        circles intersect; otherwise ``None``.

    Examples
    --------

    .. manim:: CircleIntDocExample
       :save_last_frame:

       from manim import *
       from manim_extensions import CircleInt, LabelDot

       class CircleIntDocExample(Scene):
           def construct(self):
               c1 = Circle(radius=2, color=BLUE).shift(LEFT)
               c2 = Circle(radius=2, color=GREEN).shift(RIGHT)
               pts = CircleInt(c1, c2)

               self.add(c1, c2)
               if pts:
                   for i, p in enumerate(pts):
                       self.add(LabelDot(f"P{i+1}", p, label_pos=UP, buff=0.1))
    """
    circle1_center = circle1.get_center()
    circle1_radius = circle1.radius
    circle2_center = circle2.get_center()
    circle2_radius = circle2.radius
    x1, y1, _ = circle1_center
    x2, y2, _ = circle2_center
    d = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    if d > circle1_radius + circle2_radius or d < abs(circle1_radius - circle2_radius):
        return None
    a = (circle1_radius**2 - circle2_radius**2 + d**2) / (2 * d)
    h = math.sqrt(circle1_radius**2 - a**2)
    xm = x1 + a * (x2 - x1) / d
    ym = y1 + a * (y2 - y1) / d
    xs1 = xm + h * (y2 - y1) / d
    xs2 = xm - h * (y2 - y1) / d
    ys1 = ym - h * (x2 - x1) / d
    ys2 = ym + h * (x2 - x1) / d
    return [xs1, ys1, 0], [xs2, ys2, 0]


def LineCircleInt(
    line: Line, circle: Circle
) -> Optional[Union[Tuple[np.ndarray, np.ndarray], np.ndarray]]:
    """Compute the intersection points of a line segment and a circle.

    Only points that lie within the segment parameter range ``[0, 1]``
    are returned.

    Parameters
    ----------
    line : :class:`~manim.mobject.geometry.Line`
        The line segment.
    circle : :class:`~manim.mobject.geometry.Circle`
        The circle.

    Returns
    -------
    Optional[Union[Tuple[numpy.ndarray, numpy.ndarray], numpy.ndarray]]
        * Two intersection points as a tuple if the segment cuts the circle
          twice.
        * A single :class:`numpy.ndarray` if the segment is tangent to the
          circle.
        * ``None`` if there is no intersection.

    Examples
    --------

    .. manim:: LineCircleIntDocExample
       :save_last_frame:

       from manim import *
       from manim_extensions import LineCircleInt, LabelDot

       class LineCircleIntDocExample(Scene):
           def construct(self):
               line = Line(LEFT * 3, RIGHT * 3)
               circle = Circle(radius=1, color=BLUE)
               pts = LineCircleInt(line, circle)

               self.add(line, circle)
               if pts:
                   for p in (pts if isinstance(pts, tuple) else [pts]):
                       self.add(LabelDot("P", p, label_pos=UP, buff=0.1))
    """
    p1 = line.get_start()
    p2 = line.get_end()
    c = circle.get_center()
    r = circle.radius
    dx, dy, _ = p2 - p1
    cx, cy, _ = p1 - c
    a = dx**2 + dy**2
    b = 2 * (dx * cx + dy * cy)
    c = cx**2 + cy**2 - r**2
    discriminant = b**2 - 4 * a * c
    if discriminant < 0:
        return None
    t1 = (-b + math.sqrt(discriminant)) / (2 * a)
    t2 = (-b - math.sqrt(discriminant)) / (2 * a)
    intersections = []
    for t in [t1, t2]:
        if 0 <= t <= 1:
            intersection = p1 + t * (p2 - p1)
            intersections.append(intersection)
    try:
        return intersections[0], intersections[1]
    except Exception:
        try:
            return intersections[0]
        except Exception:
            return None


def LineInt(line1: Line, line2: Line) -> Optional[list[float]]:
    """Compute the intersection of two (infinitely extended) lines.

    Calculates the intersection point in the 2‑D plane.  The result is
    **not** restricted to the segment endpoints.

    Parameters
    ----------
    line1 : :class:`~manim.mobject.geometry.Line`
        The first line.
    line2 : :class:`~manim.mobject.geometry.Line`
        The second line.

    Returns
    -------
    Optional[list[float]]
        The intersection point ``[x, y, 0]`` if the lines are not parallel;
        otherwise ``None``.

    Examples
    --------

    .. manim:: LineIntDocExample
       :save_last_frame:

       from manim import *
       from manim_extensions import LineInt, LabelDot

       class LineIntDocExample(Scene):
           def construct(self):
               l1 = Line(LEFT * 3, RIGHT * 3)
               l2 = Line(DOWN * 2, UP * 2)
               p = LineInt(l1, l2)

               self.add(l1, l2)
               if p is not None:
                   self.add(LabelDot("P", p, label_pos=UR, buff=0.1))
    """

    def det(a: tuple[float, float], b: tuple[float, float]) -> float:
        return a[0] * b[1] - a[1] * b[0]

    p1 = line1.get_start()[:2]
    p2 = line1.get_end()[:2]
    p3 = line2.get_start()[:2]
    p4 = line2.get_end()[:2]
    xdiff = (p1[0] - p2[0], p3[0] - p4[0])
    ydiff = (p1[1] - p2[1], p3[1] - p4[1])
    div = det(xdiff, ydiff)
    if div == 0:
        return None
    d = (det(p1, p2), det(p3, p4))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return [x, y, 0]


def LineArcInt(
    line: Line, arc: Arc
) -> Optional[Union[Tuple[list[float], list[float]], list[float]]]:
    """Compute the intersection points of a line segment and an arc.

    The function checks whether each candidate intersection point actually
    lies within the angular span of the arc.

    Parameters
    ----------
    line : :class:`~manim.mobject.geometry.Line`
        The line segment.
    arc : :class:`~manim.mobject.geometry.Arc`
        The arc.

    Returns
    -------
    Optional[Union[Tuple[list[float], list[float]], list[float]]]
        * A tuple of two points ``([x1, y1, 0], [x2, y2, 0])`` for two
          intersections.
        * A single point ``[x, y, 0]`` for one intersection.
        * ``None`` if there is no intersection.

    Examples
    --------

    .. manim:: LineArcIntDocExample
       :save_last_frame:

       from manim import *
       from manim_extensions import LineArcInt, LabelDot

       class LineArcIntDocExample(Scene):
           def construct(self):
               line = Line(LEFT * 2, RIGHT * 2)
               arc = Arc(start_angle=PI/4, angle=PI, radius=1.5, color=BLUE)
               pts = LineArcInt(line, arc)

               self.add(line, arc)
               if pts:
                   for p in (pts if isinstance(pts, tuple) else [pts]):
                       self.add(LabelDot("P", p, label_pos=UP, buff=0.1))
    """
    # Get line start and end (x,y only)
    p1 = line.start[:2]
    p2 = line.end[:2]

    # Handle degenerate line (a single point)
    direction = p2 - p1
    length = np.linalg.norm(direction)
    if length < 1e-8:
        return None

    # Get arc parameters (use ManimCE's correct attributes)
    center = arc.arc_center[:2]  # arc centre (x,y)
    radius = arc.radius  # radius
    start_angle = arc.start_angle  # start angle (radians)
    angle = arc.angle  # angular span (positive = counter-clockwise, negative = clockwise)

    # Shift line coordinates to the arc centre
    p1_centered = p1 - center
    p2_centered = p2 - center
    dx = p2_centered[0] - p1_centered[0]
    dy = p2_centered[1] - p1_centered[1]

    # Solve the line-circle intersection (quadratic equation)
    a = dx**2 + dy**2
    b = 2 * (p1_centered[0] * dx + p1_centered[1] * dy)
    c = p1_centered[0] ** 2 + p1_centered[1] ** 2 - radius**2
    discriminant = b**2 - 4 * a * c

    # No real roots (line and circle do not intersect)
    if discriminant < 0:
        return None

    # Compute t values (segment parameters)
    sqrt_d = np.sqrt(discriminant)
    t1 = (-b + sqrt_d) / (2 * a)
    t2 = (-b - sqrt_d) / (2 * a)
    t_values = []
    for t in [t1, t2]:
        if 0 <= t <= 1 and (len(t_values) == 0 or abs(t - t_values[0]) > 1e-8):
            t_values.append(t)

    # Check whether intersections lie within the arc's angular range (with tolerance)
    intersections = []
    TOLERANCE = 1e-6  # angular tolerance (radians)
    for t in t_values:
        # Compute intersection coordinates relative to the arc centre
        x = p1_centered[0] + t * dx
        y = p1_centered[1] + t * dy
        theta = np.arctan2(y, x) % (2 * np.pi)  # intersection angle (0..2π)

        # Arc angular range (modulo 2π)
        start_angle_mod = start_angle % (2 * np.pi)
        end_angle_mod = (start_angle + angle) % (2 * np.pi)

        # Decide whether theta lies on the arc (with tolerance)
        if angle > 0:  # counter-clockwise arc
            if start_angle_mod < end_angle_mod:
                valid = (
                    start_angle_mod - TOLERANCE
                    <= theta
                    <= end_angle_mod + TOLERANCE
                )
            else:
                valid = (theta >= start_angle_mod - TOLERANCE) or (
                    theta <= end_angle_mod + TOLERANCE
                )
        else:  # clockwise arc
            if end_angle_mod < start_angle_mod:
                valid = (
                    end_angle_mod - TOLERANCE
                    <= theta
                    <= start_angle_mod + TOLERANCE
                )
            else:
                valid = (theta <= start_angle_mod + TOLERANCE) or (
                    theta >= end_angle_mod - TOLERANCE
                )

        if valid:
            # Convert back to absolute coordinates (add z=0)
            intersection = [x + center[0], y + center[1], 0.0]
            intersections.append(intersection)
    try:
        return intersections[0], intersections[1]
    except Exception:
        try:
            return intersections[0]
        except Exception:
            return None


def MobjectInt(mob1: Mobject, mob2: Mobject) -> list:
    """Compute all intersection points between two mobjects.

    Exact formulas are used for ``Circle``, ``Line`` and ``Arc`` combinations.
    For arbitrary ``VMobject`` instances, the boundary is approximated by a
    polygonal chain and segment–segment intersections are reported.  Groups and
    ``VGroup`` instances are processed recursively over their submobjects.

    Parameters
    ----------
    mob1 : :class:`~manim.mobject.mobject.Mobject`
        First mobject.
    mob2 : :class:`~manim.mobject.mobject.Mobject`
        Second mobject.

    Returns
    -------
    list
        A list of all intersection points (each a 3-D point). Returns an empty
        list if the objects do not intersect.

    Examples
    --------

    .. manim:: MobjectIntDocExample
       :save_last_frame:

       from manim import *
       from manim_extensions import MobjectInt, LabelDot

       class MobjectIntDocExample(Scene):
           def construct(self):
               c1 = Circle(radius=1.5, color=BLUE).shift(LEFT)
               c2 = Circle(radius=1.5, color=GREEN).shift(RIGHT)
               line = Line(UP * 2, DOWN * 2, color=RED)

               pts = []
               pts.extend(MobjectInt(c1, c2))
               pts.extend(MobjectInt(c1, line))

               self.add(c1, c2, line)
               for i, p in enumerate(pts):
                   self.add(LabelDot(f"P{i+1}", p, label_pos=UP, buff=0.1))
    """

    def _to_list(result):
        if result is None:
            return []
        if isinstance(result, tuple):
            return [np.array(p) for p in result]
        if isinstance(result, list):
            return [np.array(p) for p in result]
        return [np.array(result)]

    # Exact analytic cases ----------------------------------------------------
    if isinstance(mob1, Circle) and isinstance(mob2, Circle):
        return _to_list(CircleInt(mob1, mob2))
    if isinstance(mob1, Line) and isinstance(mob2, Circle):
        return _to_list(LineCircleInt(mob1, mob2))
    if isinstance(mob1, Circle) and isinstance(mob2, Line):
        return _to_list(LineCircleInt(mob2, mob1))
    if isinstance(mob1, Line) and isinstance(mob2, Line):
        return _to_list(LineInt(mob1, mob2))
    if isinstance(mob1, Line) and isinstance(mob2, Arc):
        return _to_list(LineArcInt(mob1, mob2))
    if isinstance(mob1, Arc) and isinstance(mob2, Line):
        return _to_list(LineArcInt(mob2, mob1))

    # Generic VMobject sampling ----------------------------------------------
    def _segment_intersection(a1, a2, b1, b2):
        x1, y1 = a1[:2]
        x2, y2 = a2[:2]
        x3, y3 = b1[:2]
        x4, y4 = b2[:2]
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if abs(denom) < 1e-9:
            return None
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
        if 0 <= t <= 1 and 0 <= u <= 1:
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)
            return np.array([x, y, 0.0])
        return None

    def _sample_cubic_bezier(p0, p1, p2, p3, n=25):
        t = np.linspace(0, 1, n)
        return (
            (1 - t) ** 3 * p0[:, None]
            + 3 * (1 - t) ** 2 * t * p1[:, None]
            + 3 * (1 - t) * t**2 * p2[:, None]
            + t**3 * p3[:, None]
        ).T

    def _collect_segments(mob, samples=25):
        segments = []
        if hasattr(mob, "submobjects") and mob.submobjects:
            for sub in mob.submobjects:
                segments.extend(_collect_segments(sub, samples))
        if isinstance(mob, VMobject) and len(mob.points) >= 4:
            pts = mob.points
            i = 0
            while i + 3 < len(pts):
                if np.any(np.isnan(pts[i])):
                    i += 1
                    continue
                curve = _sample_cubic_bezier(pts[i], pts[i + 1], pts[i + 2], pts[i + 3], samples)
                for j in range(len(curve) - 1):
                    segments.append((curve[j], curve[j + 1]))
                i += 3
        return segments

    segs1 = _collect_segments(mob1)
    segs2 = _collect_segments(mob2)

    intersections = []
    for a1, a2 in segs1:
        for b1, b2 in segs2:
            p = _segment_intersection(a1, a2, b1, b2)
            if p is not None:
                # Deduplicate near-duplicate points (common at curve joins).
                if not any(np.linalg.norm(p - q) < 1e-6 for q in intersections):
                    intersections.append(p)

    return intersections


def TangentPoint(
    p1: Union[np.ndarray, tuple, list],
    p2: Union[np.ndarray, tuple, list],
    line_start: Union[np.ndarray, tuple, list],
    line_end: Union[np.ndarray, tuple, list],
) -> Optional[np.ndarray]:
    """Compute the tangent point of a circle through two points and a line.

    Given two points *p1* and *p2* that lie on a circle, and a line segment
    defined by *line_start* and *line_end*, this function finds the point
    on the line segment where the circle is tangent to the line.

    Parameters
    ----------
    p1 : Union[numpy.ndarray, tuple, list]
        First point on the circle, as ``(x, y)`` or ``(x, y, z)``.
    p2 : Union[numpy.ndarray, tuple, list]
        Second point on the circle, as ``(x, y)`` or ``(x, y, z)``.
    line_start : Union[numpy.ndarray, tuple, list]
        Start point of the line segment, as ``(x, y)`` or ``(x, y, z)``.
    line_end : Union[numpy.ndarray, tuple, list]
        End point of the line segment, as ``(x, y)`` or ``(x, y, z)``.

    Returns
    -------
    Optional[numpy.ndarray]
        The tangent point ``(x, y, 0)`` as a :class:`numpy.ndarray`, or
        ``None`` if no valid tangent point exists.

    Examples
    --------

    .. manim:: TangentPointDocExample
       :save_last_frame:

       from manim import *
       from manim_extensions import TangentPoint, LabelDot

       class TangentPointDocExample(Scene):
           def construct(self):
               p1 = Dot([1, 0, 0], color=BLUE)
               p2 = Dot([-1, 0, 0], color=BLUE)
               line = Line([0, -2, 0], [0, 2, 0])
               tangent = TangentPoint(
                   p1.get_center(), p2.get_center(),
                   line.get_start(), line.get_end(),
               )

               self.add(p1, p2, line)
               if tangent is not None:
                   self.add(LabelDot("T", tangent, label_pos=RIGHT, buff=0.1))
    """

    def to_3d(point: Union[np.ndarray, tuple, list]) -> np.ndarray:
        if len(point) == 2:
            return np.array([point[0], point[1], 0.0])
        return np.array(point[:3])

    p1 = to_3d(p1)
    p2 = to_3d(p2)
    line_start = to_3d(line_start)
    line_end = to_3d(line_end)

    # Compute the line direction vector
    line_direction = line_end - line_start
    line_length = np.linalg.norm(line_direction)

    # Handle degenerate line (a single point)
    if line_length < 1e-8:
        # Check whether the segment endpoint lies on the circle
        dist_p1 = np.linalg.norm(line_start - p1)
        dist_p2 = np.linalg.norm(line_start - p2)
        if abs(dist_p1 - dist_p2) < 1e-8:
            return line_start
        return None

    line_direction = line_direction / line_length

    # Compute the midpoint of segment p1-p2
    midpoint = (p1 + p2) / 2

    # Compute the direction vector of segment p1-p2
    p1p2_direction = p2 - p1
    p1p2_length = np.linalg.norm(p1p2_direction)

    if p1p2_length < 1e-8:
        # p1 and p2 coincide; a unique circle cannot be determined
        return None

    p1p2_direction = p1p2_direction / p1p2_length

    # Compute the perpendicular vector to segment p1-p2 (in 2D)
    perpendicular_dir = np.array([-p1p2_direction[1], p1p2_direction[0], 0.0])

    # Build a linear system to solve for centre c = midpoint + t * perpendicular_dir
    cross_perp_line = np.cross(perpendicular_dir, line_direction)
    cross_mid_line = np.cross(midpoint - line_start, line_direction)

    a = np.dot(perpendicular_dir, perpendicular_dir) - np.dot(
        cross_perp_line, cross_perp_line
    )
    b = 2 * (
        np.dot(midpoint - p1, perpendicular_dir)
        - np.dot(cross_mid_line, cross_perp_line)
    )
    c = np.dot(midpoint - p1, midpoint - p1) - np.dot(
        cross_mid_line, cross_mid_line
    )

    # Special case: a is near zero (degenerate linear equation)
    if abs(a) < 1e-8:
        if abs(b) < 1e-8:
            return None  # no solution or infinitely many solutions
        t = -c / b
        centers = [midpoint + t * perpendicular_dir]
    else:
        # Compute the discriminant
        discriminant = b**2 - 4 * a * c

        if discriminant < 0:
            # No real solution
            return None

        # Solve for t
        sqrt_d = np.sqrt(discriminant)
        t1 = (-b + sqrt_d) / (2 * a)
        t2 = (-b - sqrt_d) / (2 * a)

        # Compute candidate circle centres
        centers = [midpoint + t * perpendicular_dir for t in [t1, t2]]

    # Compute corresponding tangent points (on the line)
    valid_tangents = []
    for center in centers:
        # Project vector from line_start to center onto the line direction
        projection = np.dot(center - line_start, line_direction)

        # Check whether the projection lies within [0, line_length]
        if 0 <= projection <= line_length:
            # Compute the tangent point
            tangent_point = line_start + projection * line_direction

            # Verify that the distance from centre to tangent point equals the radius
            radius = np.linalg.norm(center - p1)
            dist_to_tangent = np.linalg.norm(center - tangent_point)

            if abs(radius - dist_to_tangent) < 1e-6:
                valid_tangents.append(tangent_point)

    # Choose the solution closest to p1 and p2
    if not valid_tangents:
        return None

    # If multiple solutions exist, return the first one
    return valid_tangents[0]

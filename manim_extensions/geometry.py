# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


"""Geometric helper functions for Manim scenes.

This module collects common intersection routines used to position and analyse
primitives such as circles, lines, and arcs within Manim visualisations.

Examples

--------

.. manim:: GeometryModuleDocExample
   :save_last_frame:

   from manim import *
   from manim_extensions import CircleInt, LineInt

   class GeometryModuleDocExample(Scene):
       def construct(self):
           c1 = Circle(radius=1.4, color=BLUE)
           c2 = Circle(radius=1.4, color=RED).shift(RIGHT * 1.2)
           self.add(c1, c2)
"""

from manim import *
import math
import numpy as np
from typing import Optional, Tuple, Union


def CircleInt(
    circle1: Circle, circle2: Circle
) -> Optional[Tuple[list[float], list[float]]]:
    """Compute the intersection points of two circles.

    Solves the geometric intersection of two circles (or spheres in 3-D).
    When both circles are coplanar (z‑coordinates match) the classic 2‑D
    circle–circle formula is used.  Otherwise the circles are treated as
    spheres and the two points on the resulting intersection circle closest
    to the line joining the sphere centres are returned.

    Parameters
    ----------
    circle1 : :class:`~manim.mobject.geometry.arc.Circle`
        The first circle.
    circle2 : :class:`~manim.mobject.geometry.arc.Circle`
        The second circle.

    Returns
    -------
    Optional[Tuple[list[float], list[float]]]
        A tuple ``(point1, point2)`` where each point is a 3‑D coordinate
        ``[x, y, z]`` if the circles intersect; otherwise ``None``.

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
    c1 = np.asarray(circle1.get_center(), dtype=float)
    r1 = circle1.radius
    c2 = np.asarray(circle2.get_center(), dtype=float)
    r2 = circle2.radius

    d_vec = c2 - c1
    d = np.linalg.norm(d_vec)
    if d > r1 + r2 + 1e-9 or d < abs(r1 - r2) - 1e-9:
        return None

    a = (r1**2 - r2**2 + d**2) / (2 * d)
    h_sq = r1**2 - a**2
    if h_sq < 0:
        return None
    h = math.sqrt(h_sq)

    mid = c1 + a * d_vec / d
    normal = d_vec / d

    if abs(normal[0]) < 0.9:
        u = np.array([1.0, 0.0, 0.0])
    else:
        u = np.array([0.0, 1.0, 0.0])
    v = np.cross(normal, u)
    v = v / np.linalg.norm(v)
    u = np.cross(v, normal)
    u = u / np.linalg.norm(u)

    pt1 = mid + h * u
    pt2 = mid - h * u

    return pt1.tolist(), pt2.tolist()


def LineCircleInt(
    line: Line, circle: Circle
) -> Optional[Union[Tuple[np.ndarray, np.ndarray], np.ndarray]]:
    """Compute the intersection points of a line segment and a circle (sphere in 3-D).

    Only points that lie within the segment parameter range ``[0, 1]``
    are returned.

    Parameters
    ----------
    line : :class:`~manim.mobject.geometry.line.Line`
        The line segment.
    circle : :class:`~manim.mobject.geometry.arc.Circle`
        The circle.

    Returns
    -------
    Optional[Union[Tuple[numpy.ndarray, numpy.ndarray], numpy.ndarray]]
        * Two intersection points as a tuple if the segment cuts the sphere
          twice.
        * A single :class:`numpy.ndarray` if the segment is tangent to the
          sphere.
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
               circle = Circle(radius=2, color=BLUE)
               pts = LineCircleInt(line, circle)

               self.add(line, circle)
               if pts:
                   for p in (pts if isinstance(pts, tuple) else [pts]):
                       self.add(LabelDot("P", p, label_pos=UP, buff=0.1))
    """
    p1 = np.asarray(line.get_start(), dtype=float)
    p2 = np.asarray(line.get_end(), dtype=float)
    c = np.asarray(circle.get_center(), dtype=float)
    r = circle.radius
    d = p2 - p1
    f = p1 - c
    a = np.dot(d, d)
    b = 2.0 * np.dot(f, d)
    c_ = np.dot(f, f) - r**2
    discriminant = b**2 - 4 * a * c_
    if discriminant < 0:
        return None
    sqrt_d = math.sqrt(discriminant)
    t1 = (-b + sqrt_d) / (2 * a)
    t2 = (-b - sqrt_d) / (2 * a)
    intersections = []
    for t in [t1, t2]:
        if 0 <= t <= 1:
            intersection = p1 + t * d
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

    Calculates the intersection point in 3‑D space.  Returns ``None``
    if the lines are parallel or skew.

    Parameters
    ----------
    line1 : :class:`~manim.mobject.geometry.line.Line`
        The first line.
    line2 : :class:`~manim.mobject.geometry.line.Line`
        The second line.

    Returns
    -------
    Optional[list[float]]
        The intersection point ``[x, y, z]`` if the lines intersect;
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
    p1 = np.asarray(line1.get_start(), dtype=float)
    p2 = np.asarray(line1.get_end(), dtype=float)
    p3 = np.asarray(line2.get_start(), dtype=float)
    p4 = np.asarray(line2.get_end(), dtype=float)

    d1 = p2 - p1
    d2 = p4 - p3

    normal = np.cross(d1, d2)
    norm_sq = np.dot(normal, normal)
    if norm_sq < 1e-18:
        return None

    if abs(np.dot(p3 - p1, normal)) > 1e-9:
        return None

    t = np.dot(np.cross(p3 - p1, d2), normal) / norm_sq
    return (p1 + t * d1).tolist()


def LineArcInt(
    line: Line, arc: Arc
) -> Optional[Union[Tuple[list[float], list[float]], list[float]]]:
    """Compute the intersection points of a line segment and an arc.

    The function checks whether each candidate intersection point actually
    lies within the angular span of the arc.  The circle containing the arc
    is treated as a sphere in 3‑D.

    Parameters
    ----------
    line : :class:`~manim.mobject.geometry.line.Line`
        The line segment.
    arc : :class:`~manim.mobject.geometry.arc.Arc`
        The arc.

    Returns
    -------
    Optional[Union[Tuple[list[float], list[float]], list[float]]]
        * A tuple of two points ``([x1, y1, z1], [x2, y2, z2])`` for two
          intersections.
        * A single point ``[x, y, z]`` for one intersection.
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
    p1 = np.asarray(line.get_start(), dtype=float)
    p2 = np.asarray(line.get_end(), dtype=float)

    direction = p2 - p1
    length = np.linalg.norm(direction)
    if length < 1e-8:
        return None

    center = np.asarray(arc.arc_center, dtype=float)
    radius = arc.radius
    start_angle = arc.start_angle
    angle = arc.angle

    p1_centered = p1 - center
    p2_centered = p2 - center
    dx = p2_centered - p1_centered

    a = np.dot(dx, dx)
    b = 2.0 * np.dot(p1_centered, dx)
    c_ = np.dot(p1_centered, p1_centered) - radius**2
    discriminant = b**2 - 4 * a * c_

    if discriminant < 0:
        return None

    sqrt_d = math.sqrt(discriminant)
    t1 = (-b + sqrt_d) / (2 * a)
    t2 = (-b - sqrt_d) / (2 * a)
    t_values = []
    for t in [t1, t2]:
        if 0 <= t <= 1 and (len(t_values) == 0 or abs(t - t_values[0]) > 1e-8):
            t_values.append(t)

    intersections = []
    TOLERANCE = 1e-6
    for t in t_values:
        pt = p1 + t * dx
        rel = pt - center
        x = rel[0]
        y = rel[1]
        theta = math.atan2(y, x) % (2 * math.pi)

        start_angle_mod = start_angle % (2 * math.pi)
        end_angle_mod = (start_angle + angle) % (2 * math.pi)

        if angle > 0:
            if start_angle_mod < end_angle_mod:
                valid = (
                    start_angle_mod - TOLERANCE <= theta <= end_angle_mod + TOLERANCE
                )
            else:
                valid = (theta >= start_angle_mod - TOLERANCE) or (
                    theta <= end_angle_mod + TOLERANCE
                )
        else:
            if end_angle_mod < start_angle_mod:
                valid = (
                    end_angle_mod - TOLERANCE <= theta <= start_angle_mod + TOLERANCE
                )
            else:
                valid = (theta <= start_angle_mod + TOLERANCE) or (
                    theta >= end_angle_mod - TOLERANCE
                )

        if valid:
            intersections.append(pt.tolist())

    try:
        return intersections[0], intersections[1]
    except Exception:
        try:
            return intersections[0]
        except Exception:
            return None


def _angle_in_arc(
    theta: float,
    start_angle: float,
    angle: float,
    tolerance: float = 1e-6,
) -> bool:
    """Check whether an angle lies within an arc's angular span.

    Parameters
    ----------
    theta : float
        The angle to test (radians, 0..2π).
    start_angle : float
        Start angle of the arc (radians).
    angle : float
        Angular span of the arc (positive = counter-clockwise,
        negative = clockwise).
    tolerance : float
        Angular tolerance in radians.

    Returns
    -------
    bool
        ``True`` if *theta* lies within the arc, ``False`` otherwise.
    """
    start_mod = start_angle % (2 * np.pi)
    end_mod = (start_angle + angle) % (2 * np.pi)
    if angle > 0:
        if start_mod < end_mod:
            return start_mod - tolerance <= theta <= end_mod + tolerance
        return theta >= start_mod - tolerance or theta <= end_mod + tolerance
    else:
        if end_mod < start_mod:
            return end_mod - tolerance <= theta <= start_mod + tolerance
        return theta <= start_mod + tolerance or theta >= end_mod - tolerance


def ArcInt(
    arc1: Arc, arc2: Arc
) -> Optional[Union[Tuple[list[float], list[float]], list[float]]]:
    """Compute the intersection points of two arcs.

    First computes the intersection points of the two full spheres defined by
    the arcs, then filters to keep only points that lie within the angular
    span of both arcs.

    Parameters
    ----------
    arc1 : :class:`~manim.mobject.geometry.arc.Arc`
        The first arc.
    arc2 : :class:`~manim.mobject.geometry.arc.Arc`
        The second arc.

    Returns
    -------
    Optional[Union[Tuple[list[float], list[float]], list[float]]]
        * A tuple of two points ``([x1, y1, z1], [x2, y2, z2])`` for two
          intersections.
        * A single point ``[x, y, z]`` for one intersection.
        * ``None`` if there is no intersection.

    Examples
    --------
    .. manim:: ArcIntDocExample
       :save_last_frame:

       from manim import *
       from manim_extensions import ArcInt, LabelDot

       class ArcIntDocExample(Scene):
           def construct(self):
               arc1 = Arc(radius=2, start_angle=PI*3/4, angle=PI/2, color=BLUE).shift(LEFT)
               arc2 = Arc(radius=2, start_angle=PI/4, angle=PI/2, color=GREEN).shift(RIGHT)
               pts = ArcInt(arc1, arc2)

               self.add(arc1, arc2)
               if pts:
                   for p in (pts if isinstance(pts, tuple) else [pts]):
                       self.add(LabelDot("P", p, label_pos=UP, buff=0.1))
    """
    c1 = np.asarray(arc1.arc_center, dtype=float)
    r1 = arc1.radius
    c2 = np.asarray(arc2.arc_center, dtype=float)
    r2 = arc2.radius

    d_vec = c2 - c1
    d = np.linalg.norm(d_vec)
    if d <= 1e-9 or d > r1 + r2 or d < abs(r1 - r2):
        return None

    a = (r1**2 - r2**2 + d**2) / (2 * d)
    h_sq = r1**2 - a**2
    if h_sq < 0:
        return None
    h = math.sqrt(h_sq)

    mid = c1 + a * d_vec / d
    normal = d_vec / d

    if abs(normal[0]) < 0.9:
        u = np.array([1.0, 0.0, 0.0])
    else:
        u = np.array([0.0, 1.0, 0.0])
    v = np.cross(normal, u)
    v = v / np.linalg.norm(v)
    u = np.cross(v, normal)
    u = u / np.linalg.norm(u)

    candidates = [mid + h * u, mid - h * u]

    start1 = arc1.start_angle
    angle1 = arc1.angle
    start2 = arc2.start_angle
    angle2 = arc2.angle

    TOL = 1e-6
    intersections = []
    for pt in candidates:
        dx1 = pt[0] - c1[0]
        dy1 = pt[1] - c1[1]
        theta1 = math.atan2(dy1, dx1) % (2 * math.pi)
        if not _angle_in_arc(theta1, start1, angle1, TOL):
            continue
        dx2 = pt[0] - c2[0]
        dy2 = pt[1] - c2[1]
        theta2 = math.atan2(dy2, dx2) % (2 * math.pi)
        if not _angle_in_arc(theta2, start2, angle2, TOL):
            continue
        intersections.append(pt.tolist())

    try:
        return intersections[0], intersections[1]
    except Exception:
        try:
            return intersections[0]
        except Exception:
            return None


def MobjectInt(mob1: Mobject, mob2: Mobject) -> list:
    """Compute all intersection points between two mobjects.

    Exact formulas are used for :class:`~manim.mobject.geometry.arc.Circle`, :class:`~manim.mobject.geometry.line.Line` and :class:`~manim.mobject.geometry.arc.Arc` combinations.
    For arbitrary :class:`~manim.mobject.types.vectorized_mobject.VMobject` instances, the boundary is approximated by a
    polygonal chain and segment–segment intersections are reported.  Groups and
    :class:`~manim.mobject.types.vectorized_mobject.VGroup` instances are processed recursively over their submobjects.

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

    @staticmethod
    def _to_list(result):
        """Normalise an intersection result into a list of numpy arrays.

        Parameters
        ----------
        result
            Raw intersection result — may be ``None``, a tuple/list of
            points, or a single point.

        Returns
        -------
        list of numpy.ndarray
            Intersection points as 3-D arrays.
        """
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
    if isinstance(mob1, Arc) and isinstance(mob2, Arc):
        return _to_list(ArcInt(mob1, mob2))

    # Generic VMobject sampling ----------------------------------------------
    @staticmethod
    def _segment_intersection(a1, a2, b1, b2):
        """Compute the intersection point of two 3-D line segments.

        Parameters
        ----------
        a1, a2 : numpy.ndarray
            Endpoints of the first segment.
        b1, b2 : numpy.ndarray
            Endpoints of the second segment.

        Returns
        -------
        numpy.ndarray or None
            The 3-D intersection point, or ``None`` if the segments do not
            intersect.
        """
        a1 = np.asarray(a1, dtype=float)
        a2 = np.asarray(a2, dtype=float)
        b1 = np.asarray(b1, dtype=float)
        b2 = np.asarray(b2, dtype=float)

        d1 = a2 - a1
        d2 = b2 - b1

        normal = np.cross(d1, d2)
        norm_sq = np.dot(normal, normal)
        if norm_sq < 1e-18:
            return None

        if abs(np.dot(b1 - a1, normal)) > 1e-9:
            return None

        t = np.dot(np.cross(b1 - a1, d2), normal) / norm_sq
        u = np.dot(np.cross(b1 - a1, d1), normal) / norm_sq

        if -1e-9 <= t <= 1 + 1e-9 and -1e-9 <= u <= 1 + 1e-9:
            t = max(0.0, min(1.0, t))
            u = max(0.0, min(1.0, u))
            return a1 + t * d1
        return None

    @staticmethod
    def _sample_cubic_bezier(p0, p1, p2, p3, n=25):
        """Sample points along a cubic Bezier curve defined by four control points.

        Parameters
        ----------
        p0, p1, p2, p3 : numpy.ndarray
            Control points of the cubic Bezier curve.
        n : int
            Number of sample points.

        Returns
        -------
        numpy.ndarray
            Array of shape ``(n, 3)`` with the sampled points.
        """
        t = np.linspace(0, 1, n)
        return (
            (1 - t) ** 3 * p0[:, None]
            + 3 * (1 - t) ** 2 * t * p1[:, None]
            + 3 * (1 - t) * t**2 * p2[:, None]
            + t**3 * p3[:, None]
        ).T

    @staticmethod
    def _collect_segments(mob, samples=25):
        """Recursively collect line segments from a VMobject's cubic Bezier curves.

        Parameters
        ----------
        mob : Mobject
            The mobject to sample.
        samples : int
            Number of sample points per cubic Bezier segment.

        Returns
        -------
        list of tuple
            Pairs of numpy arrays representing line segments.
        """
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
                curve = _sample_cubic_bezier(
                    pts[i], pts[i + 1], pts[i + 2], pts[i + 3], samples
                )
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

    @staticmethod
    def to_3d(point: Union[np.ndarray, tuple, list]) -> np.ndarray:
        """Convert a 2-D or 3-D point into a 3-D numpy array.

        Parameters
        ----------
        point : numpy.ndarray, tuple, or list
            Point coordinates (2-D or 3-D).

        Returns
        -------
        numpy.ndarray
            3-D point as a ``float64`` array.  If the input is 2-D the
            z-coordinate is set to ``0.0``.
        """
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

    if abs(p1p2_direction[2]) < 0.9:
        up = np.array([0.0, 0.0, 1.0])
    else:
        up = np.array([1.0, 0.0, 0.0])
    perpendicular_dir = np.cross(p1p2_direction, up)
    perpendicular_dir = perpendicular_dir / np.linalg.norm(perpendicular_dir)

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
    c = np.dot(midpoint - p1, midpoint - p1) - np.dot(cross_mid_line, cross_mid_line)

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

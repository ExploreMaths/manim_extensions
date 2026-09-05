# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


"""Geometric helper functions for Manim scenes.

This module provides intersection routines that operate directly on Manim
mobjects.  :func:`~manim_extensions.geometry.VMobjectInt` works with any two
:class:`~manim.mobject.types.vectorized_mobject.VMobject` instances (circles,
lines, arcs, polygons, parametric curves, text, groups, ...) by intersecting
their cubic Bézier outlines, so no type-specific cases are needed.
"""

from manim import *
import math
import numpy as np
from typing import Optional, Union


def VMobjectInt(
    vmob1: VMobject,
    vmob2: VMobject,
    tolerance: float = 1e-6,
    flatness: float = 1e-6,
    max_depth: int = 32,
) -> list:
    r"""Compute all intersection points of two arbitrary VMobjects.

    Every :class:`~manim.mobject.types.vectorized_mobject.VMobject` stores its
    outline as a sequence of cubic Bézier curves, so this function treats the
    two inputs uniformly as families of cubic Bézier curves and intersects
    them *without* any type-specific special cases.  The algorithm is:

    * the Bézier tree of each mobject (including submobjects) is collected,
      skipping ``NaN`` path-break markers;
    * each curve pair is recursively subdivided with de Casteljau's
      algorithm, always splitting the less flat curve;
    * pairs whose control-point bounding boxes do not overlap are pruned
      immediately — a Bézier curve is always contained in the convex hull
      (and hence the bounding box) of its control points, so this never
      discards a real intersection;
    * once both sub-curves deviate from their chords by less than
      *flatness*, they are treated as line segments and a closest-point
      test (with a distance tolerance accounting for the approximation
      error) decides whether the true curves meet;
    * coincident, overlapping curve pieces report the endpoints of their
      common interval instead of infinitely many points.

    Tangencies, crossings at curve joins and intersections in 3-D are all
    handled by the same subdivision loop.  When the same mobject is passed
    for both arguments the function reports its self-intersections (shared
    path-join anchors are filtered out).

    Parameters
    ----------
    vmob1 : :class:`~manim.mobject.types.vectorized_mobject.VMobject`
        The first vectorised mobject.
    vmob2 : :class:`~manim.mobject.types.vectorized_mobject.VMobject`
        The second vectorised mobject.
    tolerance : float
        Distance below which two points are considered the same
        intersection, and the base acceptance distance for the flat
        segment closest-point test.
    flatness : float
        Maximum allowed deviation of a Bézier sub-curve's control points
        from its chord before the sub-curve is treated as a straight
        segment.  Smaller values yield more accurate intersection points
        at the cost of more subdivision.
    max_depth : int
        Maximum number of recursive subdivision levels.  Guarantees
        termination for pathological configurations such as tangencies.

    Returns
    -------
    list of numpy.ndarray
        All intersection points as 3-D arrays.  An empty list is returned
        when the mobjects do not meet.  If the two outlines overlap along
        a curve segment, the endpoints of the overlapping region are
        returned.

    Examples
    --------
    .. manim:: VMobjectIntDocExample

       from manim import *
       from manim_extensions import VMobjectInt, LabelDot

       class VMobjectIntDocExample(Scene):
           def construct(self):
               circle = Circle(radius=1.5, color=BLUE)
               curve = ParametricFunction(
                   lambda t: [t, 0.5 * t**2 - 1.2, 0],
                   t_range=[-2.5, 2.5],
                   color=RED,
               )
               pts = VMobjectInt(circle, curve)

               self.play(Create(circle), Create(curve))
               self.play(
                   LaggedStart(
                       *[
                           GrowFromCenter(LabelDot(f"P{i+1}", p, label_pos=UP, buff=0.15))
                           for i, p in enumerate(pts)
                       ],
                       lag_ratio=0.4,
                   )
               )
               self.wait()
    """

    def _extract_beziers(mob):
        """Collect every cubic Bézier segment in a mobject tree.

        Each VMobject stores its outline as groups of four control points
        ``[anchor, handle, handle, anchor]`` per cubic Bézier curve; this
        helper reads them through Manim's own
        :meth:`~manim.mobject.types.vectorized_mobject.VMobject.get_cubic_bezier_tuples`
        API, so every mobject type (lines, circles, text, parametric
        curves, groups, ...) is treated identically.

        Parameters
        ----------
        mob : Mobject
            The mobject to traverse.

        Returns
        -------
        list of numpy.ndarray
            Arrays of shape ``(4, 3)`` holding the control points of each
            cubic Bézier segment.
        """
        beziers = []
        for sub in mob.submobjects:
            beziers.extend(_extract_beziers(sub))
        pts = getattr(mob, "points", None)
        if pts is not None and len(pts) >= 4:
            if hasattr(mob, "get_cubic_bezier_tuples"):
                tuples = mob.get_cubic_bezier_tuples()
            else:
                n_per_curve = 4
                trimmed = pts[: len(pts) - len(pts) % n_per_curve]
                tuples = [
                    trimmed[i:i + n_per_curve]
                    for i in range(0, len(trimmed), n_per_curve)
                ]
            for tup in tuples:
                if len(tup) >= 4 and not np.any(np.isnan(tup)):
                    beziers.append(np.array(tup[:4], dtype=float, copy=True))
        return beziers

    def _split_cubic(c, t=0.5):
        """Split a cubic Bézier curve at parameter *t* (de Casteljau).

        Parameters
        ----------
        c : numpy.ndarray
            Array of shape ``(4, 3)`` with the control points.
        t : float
            Split parameter in ``[0, 1]``.

        Returns
        -------
        tuple of numpy.ndarray
            The two sub-curves, each of shape ``(4, 3)``.
        """
        p0, p1, p2, p3 = c
        a0 = p0 + t * (p1 - p0)
        a1 = p1 + t * (p2 - p1)
        a2 = p2 + t * (p3 - p2)
        b0 = a0 + t * (a1 - a0)
        b1 = a1 + t * (a2 - a1)
        c0 = b0 + t * (b1 - b0)
        left = np.array([p0, a0, b0, c0], dtype=float)
        right = np.array([c0, b1, a2, p3], dtype=float)
        return left, right

    def _flatness_sq(c):
        """Squared maximum distance of the inner control points to the chord.

        Parameters
        ----------
        c : numpy.ndarray
            Array of shape ``(4, 3)`` with the control points.

        Returns
        -------
        float
            Squared flatness of the curve.
        """
        a, b = c[0], c[3]
        ab = b - a
        norm = float(np.dot(ab, ab))
        worst = 0.0
        for p in (c[1], c[2]):
            if norm < 1e-24:
                d = p - a
            else:
                t = float(np.dot(p - a, ab) / norm)
                t = 0.0 if t < 0.0 else (1.0 if t > 1.0 else t)
                d = p - (a + t * ab)
            dist_sq = float(np.dot(d, d))
            if dist_sq > worst:
                worst = dist_sq
        return worst

    def _bbox_overlap(c1, c2, eps):
        """Check whether the control-point bounding boxes of two curves meet.

        Parameters
        ----------
        c1, c2 : numpy.ndarray
            Arrays of shape ``(4, 3)`` with the control points.
        eps : float
            Absolute slack added to every axis interval.

        Returns
        -------
        bool
            ``True`` if the bounding boxes overlap (intersection possible),
            ``False`` otherwise.
        """
        for k in range(3):
            if c1[:, k].max() < c2[:, k].min() - eps:
                return False
            if c2[:, k].max() < c1[:, k].min() - eps:
                return False
        return True

    def _segment_meet(a0, a1, b0, b1, dist_tol):
        """Find where two (nearly flat) segments meet or overlap.

        Parameters
        ----------
        a0, a1 : numpy.ndarray
            Endpoints of the first segment.
        b0, b1 : numpy.ndarray
            Endpoints of the second segment.
        dist_tol : float
            Maximum distance for the segments to count as meeting.

        Returns
        -------
        list of numpy.ndarray
            One point for a crossing/touch, the two endpoints of the common
            interval for coincident overlapping segments, or an empty list.
        """
        da = a1 - a0
        db = b1 - b0
        r = b0 - a0
        A = float(np.dot(da, da))
        B = float(np.dot(da, db))
        C = float(np.dot(db, db))
        D = float(np.dot(da, r))
        E = float(np.dot(db, r))

        # Degenerate segments (single points) -------------------------------
        if A <= 1e-24 and C <= 1e-24:
            if np.linalg.norm(a0 - b0) <= dist_tol:
                return [(a0 + b0) / 2.0]
            return []
        if A <= 1e-24:
            t = min(1.0, max(0.0, float(np.dot(a0 - b0, db) / C)))
            pb = b0 + t * db
            if np.linalg.norm(a0 - pb) <= dist_tol:
                return [(a0 + pb) / 2.0]
            return []
        if C <= 1e-24:
            s = min(1.0, max(0.0, float(np.dot(b0 - a0, da) / A)))
            pa = a0 + s * da
            if np.linalg.norm(pa - b0) <= dist_tol:
                return [(pa + b0) / 2.0]
            return []

        det = A * C - B * B
        if abs(det) > 1e-14 * A * C:
            # General case: closest points of the supporting lines.
            # Solve [A, -B; B, -C] [s, t] = [D, E] (Cramer's rule).
            s = (C * D - B * E) / det
            t = (A * E - B * D) / -det
            s = min(1.0, max(0.0, s))
            t = min(1.0, max(0.0, t))
            pa = a0 + s * da
            pb = b0 + t * db
            if np.linalg.norm(pa - pb) <= dist_tol:
                return [(pa + pb) / 2.0]
            return []

        # Parallel supporting lines ----------------------------------------
        normal_offset = r - (float(np.dot(r, da)) / A) * da
        if np.linalg.norm(normal_offset) > dist_tol:
            return []
        # Coincident lines: overlap of the parameter intervals -------------
        s0 = float(np.dot(b0 - a0, da) / A)
        s1 = float(np.dot(b1 - a0, da) / A)
        lo = max(0.0, min(s0, s1))
        hi = min(1.0, max(s0, s1))
        if hi < lo - 1e-9:
            return []
        lo = max(lo, 0.0)
        hi = min(hi, 1.0)
        p_lo = a0 + lo * da
        p_hi = a0 + hi * da
        if np.linalg.norm(p_hi - p_lo) <= dist_tol:
            return [p_lo]
        return [p_lo, p_hi]

    curves1 = _extract_beziers(vmob1)
    curves2 = _extract_beziers(vmob2)
    same_object = vmob1 is vmob2

    found = []

    def _intersect_curves(c1, c2, depth):
        """Recursively intersect two cubic Bézier curves."""
        if not _bbox_overlap(c1, c2, tolerance):
            return
        f1 = _flatness_sq(c1)
        f2 = _flatness_sq(c2)
        flat_tol_sq = flatness * flatness

        if f1 <= flat_tol_sq and f2 <= flat_tol_sq:
            dist_tol = tolerance + 2.0 * math.sqrt(max(f1, f2))
            found.extend(_segment_meet(c1[0], c1[3], c2[0], c2[3], dist_tol))
            return

        if depth >= max_depth:
            # Last resort: accept contact within the remaining sub-curve
            # scale (at this depth the chords are vanishingly small).
            scale = max(
                float(np.linalg.norm(c1[3] - c1[0])),
                float(np.linalg.norm(c2[3] - c2[0])),
                tolerance,
            )
            found.extend(_segment_meet(c1[0], c1[3], c2[0], c2[3], scale))
            return

        # Always subdivide the less flat curve.
        if f1 >= f2:
            left, right = _split_cubic(c1)
            _intersect_curves(left, c2, depth + 1)
            _intersect_curves(right, c2, depth + 1)
        else:
            left, right = _split_cubic(c2)
            _intersect_curves(c1, left, depth + 1)
            _intersect_curves(c1, right, depth + 1)

    for i, c1 in enumerate(curves1):
        for j, c2 in enumerate(curves2):
            if same_object and j <= i:
                continue
            _intersect_curves(c1, c2, 0)

    # Self-intersection: discard points that are just shared path joins.
    if same_object:
        junctions = []
        for i, c1 in enumerate(curves1):
            for j in range(i + 1, len(curves1)):
                c2 = curves2[j]
                for ep1 in (c1[0], c1[3]):
                    for ep2 in (c2[0], c2[3]):
                        if np.linalg.norm(ep1 - ep2) <= tolerance:
                            junctions.append(ep1)
        found = [
            p
            for p in found
            if not any(np.linalg.norm(p - q) <= tolerance for q in junctions)
        ]

    # Merge near-duplicate points produced by adjacent sub-curves.
    points = []
    for p in found:
        if all(np.linalg.norm(p - q) > tolerance for q in points):
            points.append(p)
    return points


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
               p1, p2 = [0.5, 1.5, 0], [1.5, 0.5, 0]
               line = Line([-3, 0, 0], [3, 0, 0], color=BLUE)
               tangent = TangentPoint(p1, p2, line.get_start(), line.get_end())

               circle = Circle.from_three_points(p1, p2, tangent, color=RED)
               radius = DashedLine(circle.get_center(), tangent, color=YELLOW)

               self.add(line, circle, Dot(p1, color=BLUE), Dot(p2, color=BLUE))
               self.add(radius, LabelDot("T", tangent, label_pos=UP, buff=0.15))
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
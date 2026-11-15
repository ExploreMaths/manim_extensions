# SPDX-FileCopyrightText: 2026 manim-straightedge-compass contributors
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Pure geometry helpers for straightedge-and-compass constructions.

All points are ``manim`` style ``np.ndarray`` of shape ``(3,)`` with ``z=0``.
Every routine works with plain numpy arrays, so it can also be used without
rendering anything.
"""

from __future__ import annotations
from typing import Any

import numpy as np

# ---------------------------------------------------------------------------
# Basic point helpers
# ---------------------------------------------------------------------------


def P(x: float, y: float) -> np.ndarray:
    """Lift a 2D point into Manim's 3D coordinate system.

    Parameters
    ----------
    x
        Horizontal coordinate.
    y
        Vertical coordinate.

    Returns
    -------
    The point with ``z`` set to zero.
    """
    return np.array([float(x), float(y), 0.0])


def as_point(q: Any) -> np.ndarray:
    """Normalize a coordinate sequence into a 3D point.

    Parameters
    ----------
    q
        A 2D or 3D coordinate sequence.

    Returns
    -------
    The point as a float array of shape ``(3,)``.
    """
    q = np.asarray(q, dtype=float)
    if q.shape == (2,):
        q = np.array([q[0], q[1], 0.0])
    return q


def distance(a: np.ndarray, b: np.ndarray) -> float:
    """Return the planar distance between two points.

    Parameters
    ----------
    a
        First point.
    b
        Second point.

    Returns
    -------
    The Euclidean distance in the xy plane.
    """
    return float(np.linalg.norm(as_point(a)[:2] - as_point(b)[:2]))


def midpoint(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Return the midpoint of two points.

    Parameters
    ----------
    a
        First point.
    b
        Second point.

    Returns
    -------
    The point halfway between them.
    """
    return (as_point(a) + as_point(b)) / 2.0


def angle_of(a: np.ndarray, b: np.ndarray) -> float:
    """Return the direction angle from ``a`` to ``b``.

    Parameters
    ----------
    a
        Start point.
    b
        End point.

    Returns
    -------
    The angle in radians.
    """
    d = as_point(b)[:2] - as_point(a)[:2]
    return float(np.arctan2(d[1], d[0]))


def unit(v: np.ndarray) -> np.ndarray:
    """Return the unit vector in the direction of ``v``.

    Parameters
    ----------
    v
        Direction vector.

    Returns
    -------
    The normalized vector.

    Raises
    ------
    ValueError
        If the vector has zero length.
    """
    v = as_point(v)
    n = np.linalg.norm(v[:2])
    if n < 1e-12:
        raise ValueError("zero-length vector has no unit direction")
    return v / n


def rotate_vec(v: np.ndarray, angle: float) -> np.ndarray:
    """Rotate a vector counter-clockwise.

    Parameters
    ----------
    v
        Vector to rotate.
    angle
        Rotation angle in radians.

    Returns
    -------
    The rotated vector.
    """
    c, s = np.cos(angle), np.sin(angle)
    x, y = v[0], v[1]
    return np.array([c * x - s * y, s * x + c * y, 0.0])


def point_on(center: np.ndarray, radius: float, angle: float) -> np.ndarray:
    """Return the point on a circle at a given angle.

    Parameters
    ----------
    center
        Circle centre.
    radius
        Circle radius.
    angle
        Angle in radians.

    Returns
    -------
    The point on the circumference.
    """
    return as_point(center) + radius * P(np.cos(angle), np.sin(angle))


# ---------------------------------------------------------------------------
# Intersections
# ---------------------------------------------------------------------------


def circle_circle_intersection(
    c1: Any, r1: Any, c2: Any, r2: Any, tol: float = 1e-8
) -> Any:
    """Compute the intersections of two circles.

    Parameters
    ----------
    c1
        Centre of the first circle.
    r1
        Radius of the first circle.
    c2
        Centre of the second circle.
    r2
        Radius of the second circle.
    tol
        Distance tolerance for degenerate cases.

    Returns
    -------
    A list containing zero, one, or two intersection points.
    """
    c1, c2 = as_point(c1), as_point(c2)
    d = distance(c1, c2)
    if d < tol:
        return []  # concentric circles
    if d > r1 + r2 + tol or d < abs(r1 - r2) - tol:
        return []
    a = (r1 * r1 - r2 * r2 + d * d) / (2.0 * d)
    h2 = r1 * r1 - a * a
    if h2 < -tol:
        return []
    h = np.sqrt(max(h2, 0.0))
    u = (c2 - c1) / d
    n = P(-u[1], u[0])
    p0 = c1 + a * u
    if h < tol:
        return [p0]
    return [p0 + h * n, p0 - h * n]


def line_line_intersection(
    p1: Any, p2: Any, p3: Any, p4: Any, tol: float = 1e-8
) -> Any:
    """Compute the intersection of two infinite lines.

    Parameters
    ----------
    p1
        First point on the first line.
    p2
        Second point on the first line.
    p3
        First point on the second line.
    p4
        Second point on the second line.
    tol
        Determinant tolerance for parallel lines.

    Returns
    -------
    The intersection point, or ``None`` when the lines are parallel.
    """
    p1, p2, p3, p4 = map(as_point, (p1, p2, p3, p4))
    d1 = p2 - p1
    d2 = p4 - p3
    denom = d1[0] * d2[1] - d1[1] * d2[0]
    if abs(denom) < tol:
        return None
    diff = p3 - p1
    s = (diff[0] * d2[1] - diff[1] * d2[0]) / denom
    return p1 + s * d1


def circle_line_intersection(
    center: Any, radius: Any, p1: Any, p2: Any, tol: float = 1e-8
) -> Any:
    """Compute the intersections of a circle and an infinite line.

    Parameters
    ----------
    center
        Circle centre.
    radius
        Circle radius.
    p1
        First point on the line.
    p2
        Second point on the line.
    tol
        Distance tolerance for degenerate cases.

    Returns
    -------
    A list containing zero, one, or two intersection points.
    """
    center, p1, p2 = as_point(center), as_point(p1), as_point(p2)
    d = unit(p2 - p1)
    t0 = float(np.dot(center - p1, d))
    closest = p1 + t0 * d
    h2 = radius * radius - float(np.dot(closest - center, closest - center))
    if h2 < -tol:
        return []
    h = np.sqrt(max(h2, 0.0))
    if h < tol:
        return [closest]
    return [closest + h * d, closest - h * d]


# ---------------------------------------------------------------------------
# Convenience selectors
# ---------------------------------------------------------------------------


def uppermost(points: Any) -> Any:
    """Return the point with the largest y coordinate.

    Parameters
    ----------
    points
        Collection of candidate points.

    Returns
    -------
    The highest point in the collection.
    """
    return max(points, key=lambda q: as_point(q)[1])


def lowermost(points: Any) -> Any:
    """Return the point with the smallest y coordinate.

    Parameters
    ----------
    points
        Collection of candidate points.

    Returns
    -------
    The lowest point in the collection.
    """
    return min(points, key=lambda q: as_point(q)[1])


def leftmost(points: Any) -> Any:
    """Return the point with the smallest x coordinate.

    Parameters
    ----------
    points
        Collection of candidate points.

    Returns
    -------
    The leftmost point in the collection.
    """
    return min(points, key=lambda q: as_point(q)[0])


def rightmost(points: Any) -> Any:
    """Return the point with the largest x coordinate.

    Parameters
    ----------
    points
        Collection of candidate points.

    Returns
    -------
    The rightmost point in the collection.
    """
    return max(points, key=lambda q: as_point(q)[0])


def other(items: Any, given: Any) -> Any:
    """Return the element of a two-element collection that is not ``given``.

    Parameters
    ----------
    items
        Two-element collection of points.
    given
        Point to exclude.

    Returns
    -------
    The remaining point.

    Raises
    ------
    ValueError
        If no other point can be found.
    """
    for q in items:
        if not np.allclose(as_point(q)[:2], as_point(given)[:2], atol=1e-7):
            return q
    raise ValueError("no other point found")

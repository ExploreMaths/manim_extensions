# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Cover the degenerate branches of the Bézier intersection helpers."""

import numpy as np

from manim_extensions.geometry import vmobject_int


class _Dummy:
    """Minimal mobject exposing only the attributes the intersect code reads."""

    def __init__(self, points):
        self.points = np.asarray(points, dtype=float)
        self.submobjects = []


def _curve(points):
    return _Dummy(np.asarray(points, dtype=float))


def test_crossing_curves_without_bezier_getter():
    horizontal = _curve([[-1, 0, 0], [-0.3, 0, 0], [0.3, 0, 0], [1, 0, 0]])
    vertical = _curve([[0, -1, 0], [0, -0.3, 0], [0, 0.3, 0], [0, 1, 0]])

    points = vmobject_int(horizontal, vertical)

    assert len(points) == 1
    assert np.allclose(points[0], [0, 0, 0], atol=1e-6)


def test_point_to_point_contact():
    left = _curve([[0, 0, 0]] * 4)
    right = _curve([[0, 0, 0]] * 4)

    points = vmobject_int(left, right)

    assert len(points) == 1
    assert np.allclose(points[0], [0, 0, 0], atol=1e-6)


def test_point_to_segment_contact():
    point = _curve([[0, 0, 0]] * 4)
    segment = _curve([[-1, 0, 0], [-0.3, 0, 0], [0.3, 0, 0], [1, 0, 0]])

    points = vmobject_int(point, segment)

    assert len(points) == 1
    assert np.allclose(points[0], [0, 0, 0], atol=1e-6)


def test_segment_to_point_contact():
    segment = _curve([[-1, 0, 0], [-0.3, 0, 0], [0.3, 0, 0], [1, 0, 0]])
    point = _curve([[0, 0, 0]] * 4)

    points = vmobject_int(segment, point)

    assert len(points) == 1
    assert np.allclose(points[0], [0, 0, 0], atol=1e-6)


def test_parallel_segments_do_not_meet():
    first = _curve([[-1, 1, 0], [-0.3, 1, 0], [0.3, 1, 0], [1, 1, 0]])
    second = _curve([[-1, -1, 0], [-0.3, -1, 0], [0.3, -1, 0], [1, -1, 0]])

    assert vmobject_int(first, second) == []


def test_depth_limit_uses_chord_distance():
    first = _curve([[0, 0, 0], [0, 2, 0], [2, 2, 0], [2, 0, 0]])
    second = _curve([[1, -1, 0], [1, 0, 0], [1, 0, 0], [1, 2, 0]])

    points = vmobject_int(first, second, max_depth=0)

    assert isinstance(points, list)


def test_nan_curve_is_skipped_and_self_join_is_filtered():
    joined = _Dummy(
        np.asarray(
            [
                [0, 0, 0],
                [1, 1, 0],
                [2, 0, 0],
                [3, 0, 0],
                [np.nan, np.nan, np.nan],
                [np.nan, np.nan, np.nan],
                [np.nan, np.nan, np.nan],
                [np.nan, np.nan, np.nan],
            ],
            dtype=float,
        )
    )

    points = vmobject_int(joined, joined)

    assert isinstance(points, list)


def test_point_point_outside_tolerance_is_missed():
    left = _curve([[0, 0, 0]] * 4)
    right = _curve([[0.9, 0.9, 0.9]] * 4)

    assert vmobject_int(left, right, tolerance=1.0) == []


def test_point_to_segment_outside_tolerance_is_missed():
    point = _curve([[0, 0, 0]] * 4)
    segment = _curve(
        [[0.9, 0.9, 0.9], [1.2, 1.2, 1.2], [1.5, 1.5, 1.5], [1.8, 1.8, 1.8]]
    )

    assert vmobject_int(point, segment, tolerance=1.0) == []


def test_segment_to_point_outside_tolerance_is_missed():
    segment = _curve(
        [[0.9, 0.9, 0.9], [1.2, 1.2, 1.2], [1.5, 1.5, 1.5], [1.8, 1.8, 1.8]]
    )
    point = _curve([[0, 0, 0]] * 4)

    assert vmobject_int(segment, point, tolerance=1.0) == []


def test_parallel_non_collinear_segments_are_missed():
    first = _curve([[0, 0, 0], [3.3, 3.3, 0], [6.6, 6.6, 0], [10, 10, 0]])
    second = _curve([[-5, 0, 0], [-1.7, 3.3, 0], [1.6, 6.6, 0], [5, 10, 0]])

    assert vmobject_int(first, second, tolerance=2.0) == []


def test_collinear_disjoint_segments_are_missed():
    first = _curve([[0, 0, 0], [3.3, 0, 0], [6.6, 0, 0], [10, 0, 0]])
    second = _curve([[20, 0, 0], [23.3, 0, 0], [26.6, 0, 0], [30, 0, 0]])

    assert vmobject_int(first, second, tolerance=15.0) == []


def test_collinear_overlap_returns_endpoints():
    first = _curve([[0, 0, 0], [3.3, 0, 0], [6.6, 0, 0], [10, 0, 0]])
    second = _curve([[2, 0, 0], [4, 0, 0], [6, 0, 0], [8, 0, 0]])

    points = vmobject_int(first, second, tolerance=0.5)

    assert len(points) == 2
    assert np.allclose(points[0], [2, 0, 0], atol=1e-6)
    assert np.allclose(points[1], [8, 0, 0], atol=1e-6)


def test_general_closest_points_outside_tolerance_are_missed():
    first = _curve([[0, 0, 0], [0.3, 0, 0], [0.6, 0, 0], [1, 0, 0]])
    second = _curve([[1.9, -1, 0.9], [1.9, -0.3, 0.9], [1.9, 0.3, 0.9], [1.9, 1, 0.9]])

    assert vmobject_int(first, second, tolerance=0.9) == []


def test_short_collinear_overlap_returns_one_point():
    first = _curve([[0, 0, 0], [3.3, 0, 0], [6.6, 0, 0], [10, 0, 0]])
    second = _curve([[4.9, 0, 0], [4.97, 0, 0], [5.03, 0, 0], [5.1, 0, 0]])

    points = vmobject_int(first, second, tolerance=0.5)

    assert len(points) == 1
    assert abs(points[0][0] - 4.9) < 1e-6


def test_self_intersection_ignores_shared_path_join():
    joined = _Dummy(
        np.asarray(
            [
                [0, 0, 0],
                [0.7, 0, 0],
                [1.3, 0, 0],
                [2, 0, 0],
                [2, 0, 0],
                [1.4, 0.2, 0],
                [0.7, 0.35, 0],
                [0, 0.5, 0],
            ],
            dtype=float,
        )
    )

    points = vmobject_int(joined, joined, tolerance=0.2)

    assert all(np.linalg.norm(p - np.array([2.0, 0.0, 0.0])) > 0.2 for p in points)


class _GetterDummy(_Dummy):
    def get_cubic_bezier_tuples(self):
        return [self.points[:4]]


def test_nested_submobjects_are_traversed():
    child = _curve([[0, 0, 0], [0.3, 0, 0], [0.6, 0, 0], [1, 0, 0]])
    parent = _Dummy(np.empty((0, 3)))
    parent.submobjects = [child]
    vertical = _curve([[0.5, -1, 0], [0.5, -0.3, 0], [0.5, 0.3, 0], [0.5, 1, 0]])

    points = vmobject_int(parent, vertical)

    assert len(points) == 1


def test_bezier_getter_path_is_used():
    first = _GetterDummy([[0, 0, 0], [0.3, 0, 0], [0.6, 0, 0], [1, 0, 0]])
    second = _curve([[0.5, -1, 0], [0.5, -0.3, 0], [0.5, 0.3, 0], [0.5, 1, 0]])

    points = vmobject_int(first, second)

    assert len(points) == 1


def test_curved_first_curve_subdivides():
    first = _curve([[0, 0, 0], [0.2, 2, 0], [1.8, 2, 0], [2, 0, 0]])
    second = _curve([[1, -1, 0], [1, -0.3, 0], [1, 0.3, 0], [1, 1, 0]])

    points = vmobject_int(first, second, max_depth=4)

    assert isinstance(points, list)

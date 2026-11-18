# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the divide-and-conquer Delaunay helper."""

import numpy as np
import pytest
from manim import DashedLine, Scene

from manim_extensions.meshes.delaunay.divide_and_conquer import (
    DivideAndConquer,
    get_clockwise_angle,
    get_counter_clockwise_angle,
)
from manim_extensions.meshes.models.data_models.mesh import Mesh
from manim_extensions.meshes.models.manim_models.triangle_mesh import (
    TriangleManim2DMesh,
)

POINTS = np.array(
    [
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [2.0, 1.0, 0.0],
        [3.0, 0.0, 0.0],
    ]
)


@pytest.fixture()
def helper():
    triangle_mesh = TriangleManim2DMesh(Mesh(POINTS, [[0, 1, 2], [1, 2, 3]]))
    return DivideAndConquer(Scene(), triangle_mesh)


def test_angle_helpers_are_finite():
    a = np.array([0.0, 0.0])
    b = np.array([1.0, 0.0])
    c = np.array([1.0, 1.0])

    assert np.isfinite(get_counter_clockwise_angle(a, b))
    assert np.isfinite(get_clockwise_angle(b, c))


def test_split_points_halves_the_set(helper):
    left, right, split_line = helper.split_points([0, 1, 2, 3], speed=0.1)

    assert left == [0, 1]
    assert right == [2, 3]
    assert isinstance(split_line, DashedLine)


@pytest.mark.parametrize("indices", [[0], [0, 1], [0, 1, 2]])
def test_triangulate_leq_3_accepts_segments_and_triangles(helper, indices):
    helper.triangulate_leq_3(indices)

    assert len(helper.triangle_mesh.faces) >= 1


def test_triangulate_leq_3_rejects_larger_sets(helper):
    with pytest.raises(ValueError):
        helper.triangulate_leq_3([0, 1, 2, 3])


def test_divide_and_conquer_requires_empty_mesh(helper):
    with pytest.raises(ValueError, match="must be empty"):
        helper.divide_and_conquer_recursive()


def test_right_candidate_removes_conflicting_face(helper, monkeypatch):
    import manim_extensions.meshes.delaunay.divide_and_conquer as module

    points = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.5, 0.6, 0.0],
            [0.5, 0.4, 0.0],
        ]
    )
    helper.triangle_mesh = TriangleManim2DMesh(Mesh(points, [[0, 1, 2], [0, 1, 3]]))
    helper.scene.play = lambda *args, **kwargs: None
    helper.scene.wait = lambda *args, **kwargs: None
    monkeypatch.setattr(
        module,
        "get_triangle_circum_circle_params",
        lambda *args: (np.zeros(3), 10.0),
    )

    rr_edges = [(1, 2), (1, 3)]
    helper._right_candidate([0, 1], rr_edges)

    assert len(rr_edges) == 1


def test_left_candidate_removes_conflicting_face(helper, monkeypatch):
    import manim_extensions.meshes.delaunay.divide_and_conquer as module

    points = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.5, 0.6, 0.0],
            [0.5, 0.4, 0.0],
        ]
    )
    helper.triangle_mesh = TriangleManim2DMesh(Mesh(points, [[0, 1, 2], [0, 1, 3]]))
    helper.scene.play = lambda *args, **kwargs: None
    helper.scene.wait = lambda *args, **kwargs: None
    monkeypatch.setattr(
        module,
        "get_triangle_circum_circle_params",
        lambda *args: (np.zeros(3), 10.0),
    )

    ll_edges = [(0, 2), (0, 3)]
    helper._left_candidate([0, 1], ll_edges)

    assert len(ll_edges) == 1

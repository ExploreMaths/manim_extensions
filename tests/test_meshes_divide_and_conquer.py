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
from manim_extensions.meshes.models.manim_models.triangle_mesh import TriangleManim2DMesh

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

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the Delaunay helpers on a 2-D triangle mesh."""

import numpy as np
import pytest
from manim import Circle, Scene

from manim_extensions.meshes.delaunay import delaunay_criterion
from manim_extensions.meshes.delaunay.voronoi import VoronoiDelaunay
from manim_extensions.meshes.exceptions import InvalidMeshException
from manim_extensions.meshes.models.data_models.mesh import Mesh
from manim_extensions.meshes.models.manim_models.triangle_mesh import TriangleManim2DMesh

POINTS = [
    [0.0, 0.0, 0.0],
    [1.0, 0.0, 0.0],
    [1.0, 1.0, 0.0],
    [0.0, 1.0, 0.0],
    [2.0, 1.0, 0.0],
]
TRIANGLES = [[0, 1, 2], [0, 2, 3], [1, 4, 2]]


@pytest.fixture()
def triangle_mesh():
    return TriangleManim2DMesh(Mesh(POINTS, TRIANGLES))


def test_triangle_mesh_rejects_quads():
    with pytest.raises(InvalidMeshException):
        TriangleManim2DMesh(Mesh(POINTS, [[0, 1, 2, 3]]))


def test_circum_circle_params():
    centre, radius = delaunay_criterion.get_triangle_circum_circle_params(
        np.array([0.0, 0.0, 0.0]),
        np.array([1.0, 0.0, 0.0]),
        np.array([0.0, 1.0, 0.0]),
    )

    assert np.allclose(centre, [0.5, 0.5, 0.0])
    assert radius == pytest.approx(0.5 * np.sqrt(2.0))


def test_circum_circle_mobject(triangle_mesh):
    circle = delaunay_criterion.get_circum_circle(triangle_mesh, 0)

    assert isinstance(circle, Circle)


def test_violating_points_detection(triangle_mesh):
    indices = delaunay_criterion.get_point_indices_violating_delaunay(triangle_mesh, 0)

    assert isinstance(indices, list)
    assert not delaunay_criterion.is_point_violating_delaunay(triangle_mesh, 4, 0)


def test_voronoi_delaunay_builds_groups(triangle_mesh):
    diagram = VoronoiDelaunay(Scene(), triangle_mesh)

    voronoi, triangles = diagram.create_voronoi()

    assert len(voronoi) >= 1
    assert len(triangles) >= 1

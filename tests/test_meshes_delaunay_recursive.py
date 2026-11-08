# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the divide-and-conquer Delaunay triangulation driver."""

from manim import Scene

from manim_extensions.meshes.delaunay.divide_and_conquer import DivideAndConquer
from manim_extensions.meshes.models.data_models.mesh import Mesh
from manim_extensions.meshes.models.manim_models.triangle_mesh import (
    TriangleManim2DMesh,
)

POINTS = [(0, 0, 0), (2, 0, 0), (1, 1.8, 0), (3, 1.0, 0), (0, 2.0, 0)]


def test_recursive_triangulation_of_five_points():
    mesh = Mesh(POINTS, [])
    triangle_mesh = TriangleManim2DMesh(mesh)
    scene = Scene()

    driver = DivideAndConquer(scene, triangle_mesh)
    result = driver.divide_and_conquer_recursive(speed=0.05)

    assert result is None
    assert len(mesh.faces) > 0

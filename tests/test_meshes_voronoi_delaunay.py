# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the Voronoi/Delaunay visualization helper."""

import numpy as np
import pytest
from manim import Scene, tempconfig

from manim_extensions.meshes.delaunay.voronoi import VoronoiDelaunay
from manim_extensions.meshes.models.data_models.mesh import Mesh
from manim_extensions.meshes.models.manim_models.triangle_mesh import TriangleManim2DMesh


@pytest.fixture()
def helper():
    with tempconfig({"dry_run": True, "disable_caching": True, "renderer": "cairo"}):
        pts = np.random.RandomState(42).rand(8, 3)
        pts = (pts - 0.5) * 6
        pts[:, 2] = 0
        scene = Scene()
        mesh = TriangleManim2DMesh(Mesh(pts.tolist(), []), display_vertices=True)
        scene.add(mesh)
        yield scene, mesh, VoronoiDelaunay(scene, mesh)


def test_create_triangle_adds_faces(helper):
    scene, mesh, vd = helper
    index = 0

    vd.create_triangle(index)

    assert len(vd.voronoi.vertices) >= 1


def test_get_circum_circle_is_a_circle(helper):
    scene, mesh, vd = helper

    circle = vd.get_circum_circle(0)

    assert circle is not None

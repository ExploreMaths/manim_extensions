# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for triangle-mesh edge flipping."""

import pytest
from manim import Scene, tempconfig

from manim_extensions.meshes.models.data_models.mesh import Mesh
from manim_extensions.meshes.models.manim_models.triangle_mesh import TriangleManim2DMesh

PTS = [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0], [0.0, 1.0, 0.0]]
FACES = [[0, 1, 2], [0, 2, 3]]


@pytest.fixture()
def mesh_scene():
    with tempconfig({"dry_run": True, "disable_caching": True, "renderer": "cairo"}):
        scene = Scene()
        mesh = TriangleManim2DMesh(Mesh(PTS, FACES), display_vertices=True)
        scene.add(mesh)
        mesh.setup_vertices()
        yield scene, mesh


def test_edge_flip_rewires_adjacent_faces(mesh_scene):
    scene, mesh = mesh_scene

    mesh.edge_flip(scene, 0, 1, run_time=0.1)

    assert len(mesh.mesh.faces) == 2

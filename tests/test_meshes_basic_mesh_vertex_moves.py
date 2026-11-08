# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for absolute vertex moves, flipping and grid snapping."""

import numpy as np
import pytest
from manim import Scene, tempconfig

from manim_extensions.meshes.models.data_models.mesh import Mesh
from manim_extensions.meshes.models.manim_models.basic_mesh import ManimMesh

PTS = [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0], [0.0, 1.0, 0.0]]
FACES = [[0, 1, 2], [0, 2, 3]]


@pytest.fixture()
def mesh_scene():
    with tempconfig({"dry_run": True, "disable_caching": True, "renderer": "cairo"}):
        scene = Scene()
        mesh = ManimMesh(Mesh(PTS, FACES), display_vertices=True)
        scene.add(mesh)
        mesh.setup_vertices()
        yield scene, mesh


def test_move_vertex_to_absolute_position(mesh_scene):
    scene, mesh = mesh_scene

    mesh.move_vertex_to(scene, 0, np.array([0.5, 0.5, 0.0]))

    assert mesh.mesh.vertices[0] == pytest.approx([0.5, 0.5, 0.0])


def test_move_vertices_to_positions(mesh_scene):
    scene, mesh = mesh_scene

    mesh.move_vertices_to(scene, np.array([[0.1, 0.1, 0.0]] * 4))

    assert mesh.mesh.vertices[0] == pytest.approx([0.1, 0.1, 0.0])


def test_flip_mirrors_mesh(mesh_scene):
    _, mesh = mesh_scene

    mesh.flip(axis=np.array([1.0, 0.0, 0.0]))

    assert mesh.mesh.vertices.shape == (4, 3)


def test_move_to_grid_snaps_vertices(mesh_scene):
    scene, mesh = mesh_scene

    mesh.move_to_grid(scene, (0.5, 0.5, 0.5), (0.05, 0.05, 0.05), nof_steps=2)

    assert mesh.mesh.vertices[0] == pytest.approx([0.0, 0.0, 0.0], abs=0.5)

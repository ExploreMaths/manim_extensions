# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the mesh data model and its Manim wrapper."""

import numpy as np
import pytest

from manim_extensions.meshes import templates
from manim_extensions.meshes.exceptions import InvalidMeshException
from manim_extensions.meshes.models.data_models.mesh import Mesh
from manim_extensions.meshes.models.manim_models.basic_mesh import ManimMesh

VERTICES = [
    [0.0, 0.0, 0.0],
    [1.0, 0.0, 0.0],
    [0.0, 1.0, 0.0],
    [0.0, 0.0, 1.0],
]
FACES = [[0, 1, 2], [0, 1, 3], [1, 2, 3], [0, 2, 3]]


@pytest.fixture()
def mesh():
    return Mesh(VERTICES, FACES)


def test_mesh_extracts_edges(mesh):
    assert len(mesh.vertices) == 4
    assert len(mesh.faces) == 4
    assert len(mesh.edges) == 6


def test_get_3d_vertices_shape(mesh):
    assert np.shape(mesh.get_3d_vertices()) == (4, 3)


def test_faces_must_be_nested():
    with pytest.raises(InvalidMeshException):
        Mesh(VERTICES, [0, 1, 2])


def test_manim_mesh_builds_edges_and_faces(mesh):
    manim_mesh = ManimMesh(mesh)

    assert len(manim_mesh.faces) == 4
    assert len(manim_mesh.edges) == 6


def test_manim_mesh_accessors(mesh):
    manim_mesh = ManimMesh(mesh)

    assert manim_mesh.get_face(0) is not None
    assert manim_mesh.get_edge(0) is not None


def test_add_and_remove_face():
    manim_mesh = ManimMesh(Mesh(VERTICES, FACES))

    face, edges = manim_mesh.add_face([0, 1, 2])

    assert face is not None
    assert len(manim_mesh.faces) == 5

    manim_mesh.remove_face(len(manim_mesh.mesh.faces) - 1)

    assert len(manim_mesh.faces) == 4


def test_flip_keeps_geometry_consistent(mesh):
    manim_mesh = ManimMesh(mesh)

    manim_mesh.flip([1.0, 0.0, 0.0])

    assert len(manim_mesh.faces) == 4
    assert np.shape(manim_mesh.mesh.get_3d_vertices()) == (4, 3)


def test_display_vertices_adds_spheres():
    manim_mesh = ManimMesh(Mesh(VERTICES, FACES), display_vertices=True)

    assert len(manim_mesh.vertices) == 4


@pytest.mark.parametrize(
    "areas,vertex_count",
    [
        ([(0.0, 1.0, 2), (0.0, 1.0, 2)], 4),
        ([(0.0, 1.0, 2)] * 3, 8),
        ([(0.0, 1.0, 2)] * 4, 16),
    ],
)
def test_create_grid(areas, vertex_count):
    grid = templates.create_grid(areas)

    assert len(grid.vertices) == vertex_count
    assert isinstance(ManimMesh(grid), ManimMesh)

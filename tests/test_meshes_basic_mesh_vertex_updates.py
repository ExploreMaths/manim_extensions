# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for direct (non-animated) mesh editing helpers."""

import numpy as np

from manim_extensions.meshes.models.data_models.mesh import Mesh
from manim_extensions.meshes.models.manim_models.basic_mesh import ManimMesh

VERTICES = [(0, 0, 0), (1, 0, 0), (0, 1, 0)]
FACES = [[0, 1, 2]]


def make_mesh():
    return ManimMesh(Mesh(VERTICES, FACES))


def test_setup_vertices_builds_group():
    mesh = make_mesh()

    assert mesh.setup_vertices() is not None


def test_update_vertex_and_edge():
    mesh = make_mesh()

    mesh.setup_vertices()
    mesh._update_vertex(0, np.array([0.2, 0.2, 0.0]))
    mesh._update_edge((0, 1))

    assert mesh.get_vertex(0) is not None


def test_flip_mirrors_the_mesh():
    mesh = make_mesh()

    mesh.flip(np.array([1.0, 0.0, 0.0]))

    assert mesh is not None

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for 2D mesh vertex dots and 4D mesh flips."""

import numpy as np
import pytest
from manim import tempconfig

from manim_extensions.meshes.models.data_models.mesh import Mesh
from manim_extensions.meshes.models.manim_models.basic_mesh import Manim2DMesh, ManimMesh

MESH_2D = Mesh([[0, 0, 0], [1, 0, 0], [0, 1, 0]], [[0, 1, 2]], [[0]])
MESH_4D = Mesh([[0, 0, 0, 0], [1, 0, 0, 0], [0, 1, 0, 0]], [[0, 1, 2]], [[0]])


@pytest.fixture(autouse=True)
def _config():
    with tempconfig({"dry_run": True, "disable_caching": True, "renderer": "cairo"}):
        yield


def test_dots_track_vertices():
    mesh = Manim2DMesh(MESH_2D, verts_size=0.05)

    dots = mesh.get_dots([0, 1])

    assert len(dots) == 2


def test_dots_use_mesh_vertex_positions():
    mesh = Manim2DMesh(MESH_2D, verts_size=0.05)

    dots = mesh.get_dots([1])

    assert np.allclose(dots[0].get_center()[:2], mesh.mesh.get_3d_vertices()[1][:2])


def test_four_dim_mesh_flip_updates_data():
    mesh = ManimMesh(MESH_4D, verts_size=0.05)

    mesh.flip(axis=np.array([1.0, 0.0, 0.0, 0.0]))

    assert mesh.mesh.dim == 4

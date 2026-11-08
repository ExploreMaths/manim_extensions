# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests that animate mesh vertices inside a scene."""

import numpy as np
import pytest
from manim import Scene, tempconfig

from manim_extensions.meshes.models.data_models.mesh import Mesh
from manim_extensions.meshes.models.manim_models.basic_mesh import ManimMesh

TRIANGLE = [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]


@pytest.fixture()
def context():
    with tempconfig({"dry_run": True, "disable_caching": True, "renderer": "cairo"}):
        scene = Scene()
        mesh = ManimMesh(Mesh(TRIANGLE, [[0, 1, 2]]))
        mesh.setup_vertices()
        yield scene, mesh


def test_shift_vertex_animates_one_vertex(context):
    scene, mesh = context

    mesh.shift_vertex(scene, 0, np.array([1.0, 0.0, 0.0]), shift_vertex_runtime=0.1)

    assert mesh is not None


def test_shift_vertices_animates_all_vertices(context):
    scene, mesh = context

    mesh.shift_vertices(
        scene, np.array([[1.0, 0.0, 0.0]] * len(TRIANGLE)), shift_vertices_runtime=0.1
    )

    assert mesh is not None

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the ManimMesh transform methods."""

import numpy as np
import pytest

from manim_extensions.meshes.models.data_models.mesh import Mesh
from manim_extensions.meshes.models.manim_models.basic_mesh import ManimMesh
from manim_extensions.meshes.templates import create_grid


@pytest.fixture()
def flat_mesh():
    mesh = Mesh([(0, 0, 0), (1, 0, 0), (0, 1, 0)], [[0, 1, 2]])
    return ManimMesh(mesh)


def test_rotate_two_dimensional_mesh(flat_mesh):
    flat_mesh.rotate(np.pi / 4)

    assert len(flat_mesh.mesh.faces) == 1


def test_scale_and_shift(flat_mesh):
    flat_mesh.scale(2.0)
    flat_mesh.shift([1, 0, 0])

    assert len(flat_mesh.mesh.faces) == 1


def test_flip(flat_mesh):
    flat_mesh.flip([1, 0, 0])

    assert len(flat_mesh.mesh.faces) == 1


def test_four_dimensional_grid_rotation():
    grid = create_grid([(-1, 1, 2), (-1, 1, 2), (-1, 1, 2), (-1, 1, 2)])
    manim_grid = ManimMesh(grid)

    assert manim_grid.mesh.dim == 4

    manim_grid.rotate(np.pi / 3, np.array([[1.0, 0, 0, 0], [0, 1.0, 0, 0]]))
    manim_grid.rotate(np.pi / 3, axis=[0, 0, 1])

    assert len(manim_grid.mesh.vertices) == len(grid.vertices)

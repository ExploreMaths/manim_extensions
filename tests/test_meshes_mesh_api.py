# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the editable mesh mobjects and the Delaunay helpers."""

import numpy as np
import pytest
from manim import RIGHT, UP, Scene

from manim_extensions.meshes.delaunay.divide_and_conquer import (
    get_clockwise_angle,
    get_counter_clockwise_angle,
)
from manim_extensions.meshes.models.data_models.mesh import Mesh
from manim_extensions.meshes.models.manim_models.basic_mesh import ManimMesh

VERTICES = np.array(
    [[0, 0, 0], [1, 0, 0], [0.5, 1, 0], [0.5, 0.5, 1.0]],
    dtype=float,
)
FACES = [np.array([0, 1, 2]), np.array([0, 1, 3])]


@pytest.fixture
def manim_mesh():
    """A tetrahedron-ish mesh wrapped in a manim mobject."""
    return ManimMesh(Mesh(VERTICES.copy(), [f.copy() for f in FACES]))


def test_add_and_remove_face(manim_mesh):
    added = manim_mesh.add_face(np.array([1, 2, 3]))
    assert added is not None

    removed = manim_mesh.remove_face(0)
    assert removed is not None


@pytest.mark.parametrize("factor", [0.5, 2.0])
def test_scale(manim_mesh, factor):
    manim_mesh.scale(factor)

    assert manim_mesh.mesh.vertices.shape == (4, 3)


def test_shift_rotate_flip_and_stretch(manim_mesh):
    manim_mesh.shift(UP)
    manim_mesh.rotate(np.pi / 2, axis=UP)
    manim_mesh.flip(axis=RIGHT)
    manim_mesh.stretch(2, dim=0)

    assert manim_mesh.mesh.vertices.shape == (4, 3)


def test_add_vertices(manim_mesh):
    scene = Scene()
    new_vertices = np.array([[2.0, 0.0, 0.0]])

    manim_mesh.add_vertices(new_vertices, scene)


def test_mesh_geometry_helpers(manim_mesh):
    assert manim_mesh._as_mesh_dim(np.array([1.0, 2.0])) is not None
    assert manim_mesh._mesh_center().shape == (3,)
    manim_mesh._rebuild_objects()


@pytest.mark.parametrize(
    "a,b",
    [
        (np.array([1.0, 0.0]), np.array([0.0, 1.0])),
        (np.array([1.0, 0.0]), np.array([-1.0, 0.0])),
        (np.array([1.0, 0.0]), np.array([1.0, 0.0])),
    ],
)
def test_angle_helpers(a, b):
    clockwise = get_clockwise_angle(a, b)
    counter = get_counter_clockwise_angle(a, b)

    assert np.isscalar(clockwise)
    assert np.isscalar(counter)

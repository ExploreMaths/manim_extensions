# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the mesh data model's validation branches."""

import numpy as np
import pytest

from manim_extensions.meshes.exceptions import (
    InvalidMeshException,
    InvalidRequestException,
    MeshIndexException,
)
from manim_extensions.meshes.models.data_models.mesh import Mesh


def build_mesh() -> Mesh:
    return Mesh(
        [[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0]],
        [[0, 1, 2], [1, 3, 2]],
        [[0, 1]],
    )


def test_vertices_must_be_twice_nested():
    with pytest.raises(InvalidMeshException):
        Mesh([0, 1, 2], [[0, 1, 2]], [[0]])


def test_perspective_behind_vertices_raises():
    mesh = Mesh([[0, 0, 0, 5], [1, 0, 0, 5]], [[0, 1, 2, 3]])
    with pytest.raises(InvalidRequestException):
        mesh._project_4d(3.0)


def test_higher_dimensional_mesh_cannot_broadcast():
    mesh = Mesh([[0, 0, 0, 0, 0], [1, 0, 0, 0, 0]], [[0, 1, 2, 3, 4]])
    with pytest.raises(InvalidRequestException):
        mesh.get_3d_vertices()


def test_update_vertex_dimension_mismatch():
    mesh = build_mesh()
    with pytest.raises(InvalidMeshException):
        mesh.update_vertex(0, [0, 0])


def test_add_faces_accepts_tuple():
    mesh = build_mesh()

    mesh.add_faces(((0, 2, 3),))

    assert len(mesh.faces) == 3


def test_add_faces_rejects_unknown_type():
    mesh = build_mesh()
    with pytest.raises(Exception):
        mesh.add_faces("bad")


def test_update_part_requires_one_dimensional_array():
    mesh = build_mesh()
    with pytest.raises(Exception):
        mesh.update_part(0, np.array([[0], [1]]))


def test_update_part_index_out_of_range():
    mesh = build_mesh()
    with pytest.raises(MeshIndexException):
        mesh.update_part(5, np.array([0]))


def test_update_part_face_index_out_of_range():
    mesh = build_mesh()
    with pytest.raises(MeshIndexException):
        mesh.update_part(0, np.array([9]))


def test_dangling_face_check_without_faces():
    mesh = Mesh([[0, 0, 0], [1, 0, 0]], [], [[0]])

    assert mesh.dangling_face_check() is False


def test_rotation_plane_rejects_zero_axis():
    with pytest.raises(InvalidRequestException):
        Mesh._rotation_plane_4d(np.array([[0, 0, 0, 0], [1, 0, 0, 0]]))


def test_rotation_plane_rejects_dependent_axes():
    with pytest.raises(InvalidRequestException):
        Mesh._rotation_plane_4d(np.array([[1, 0, 0, 0], [2, 0, 0, 0]]))


@pytest.mark.parametrize("axis", [np.array([[1, 0, 0, 0, 0], [0, 1, 0, 0, 0]])])
def test_rotation_plane_requires_two_four_dim_vectors(axis):
    with pytest.raises(InvalidRequestException):
        Mesh._rotation_plane_4d(axis)

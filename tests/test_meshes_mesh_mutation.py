# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for mesh mutation helpers."""

import numpy as np
import pytest

from manim_extensions.meshes.exceptions import (
    InvalidMeshException,
    InvalidTypeException,
    MeshIndexException,
)
from manim_extensions.meshes.models.data_models.mesh import Mesh

TRI = Mesh([[0, 0, 0], [1, 0, 0], [0, 1, 0]], [[0, 1, 2]], [[0]])


def _mesh():
    return Mesh([[0, 0, 0], [1, 0, 0], [0, 1, 0]], [[0, 1, 2]], [[0]])


def test_update_vertex_writes_new_coordinates():
    mesh = _mesh()

    mesh.update_vertex(0, [0.5, 0.5, 0.0])

    assert list(mesh.vertices[0]) == pytest.approx([0.5, 0.5, 0.0])


def test_update_vertex_out_of_range_raises():
    mesh = _mesh()

    with pytest.raises(MeshIndexException):
        mesh.update_vertex(9, [0.0, 0.0, 0.0])


def test_update_vertex_with_wrong_shape_raises():
    mesh = _mesh()

    with pytest.raises(InvalidTypeException):
        mesh.update_vertex(0, np.zeros((2, 3)))


def test_update_vertex_with_wrong_dimension_raises():
    mesh = _mesh()

    with pytest.raises(InvalidMeshException):
        mesh.update_vertex(0, [0.0, 0.0])


def test_update_part_replaces_face_indices():
    mesh = _mesh()

    mesh.update_part(0, [0])

    assert list(mesh.parts[0]) == [0]


def test_add_faces_appends_faces():
    mesh = Mesh([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]], [[0, 1, 2]], [[0]])

    mesh.add_faces([[0, 2, 3]])

    assert len(mesh.faces) == 2


def test_add_faces_with_bad_index_raises():
    mesh = _mesh()

    with pytest.raises(MeshIndexException):
        mesh.add_faces([[0, 1, 9]])


def test_add_parts_appends_parts():
    mesh = _mesh()

    mesh.add_parts([[0]])

    assert len(mesh.parts) == 2


def test_add_to_mesh_merges_and_shifts_indices():
    first = _mesh()
    second = Mesh([[2, 0, 0], [3, 0, 0], [2, 1, 0]], [[0, 1, 2]], [[0]])

    first.add_to_mesh(second)

    assert len(first.vertices) == 6
    assert len(first.faces) == 2


def test_add_to_mesh_with_different_dimension_raises():
    first = _mesh()
    second = Mesh([[2, 0, 0, 0], [3, 0, 0, 0], [2, 1, 0, 0]], [[0, 1, 2]], [[0]])

    with pytest.raises(InvalidMeshException):
        first.add_to_mesh(second)


def test_apply_flip_mirrors_vertices():
    mesh = _mesh()

    mesh.apply_flip(axis=np.array([1.0, 0.0, 0.0]))

    assert list(mesh.vertices[2]) == pytest.approx([0.0, -1.0, 0.0])


def test_apply_flip_about_point():
    mesh = _mesh()

    mesh.apply_flip(axis=np.array([1.0, 0.0, 0.0]), about_point=np.array([0.0, 2.0, 0.0]))

    assert list(mesh.vertices[2]) == pytest.approx([0.0, 3.0, 0.0])

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Regression tests for the local-only gaps in the vendored meshes package."""

import numpy as np
import pytest

from manim_extensions.meshes.models.data_models.mesh import Mesh
from manim_extensions.meshes.models.manim_models.opengl_mesh import FastManimMesh


def _quad_mesh() -> Mesh:
    return Mesh(
        np.array(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [1.0, 1.0, 0.0],
                [0.0, 1.0, 0.0],
            ]
        ),
        np.array([[0, 1, 2], [0, 2, 3]]),
        np.array([[0, 1]]),
    )


def _assert_edges_consistent(mesh: Mesh) -> None:
    assert mesh.edges == sorted(mesh.edges)
    assert set(mesh.edges) == set(mesh.extract_edges())


def test_edge_cache_tracks_add_update_remove() -> None:
    mesh = _quad_mesh()
    _assert_edges_consistent(mesh)
    assert (0, 2) in mesh.edges  # shared diagonal

    mesh.add_faces([np.array([1, 2, 3])])
    _assert_edges_consistent(mesh)

    mesh.remove_faces([0])
    _assert_edges_consistent(mesh)
    assert (0, 2) in mesh.edges  # still used by the remaining second face

    mesh.update_face(0, np.array([0, 1, 3]))
    _assert_edges_consistent(mesh)
    assert (0, 2) not in mesh.edges

    mesh.remove_faces([1])
    _assert_edges_consistent(mesh)


def test_edge_cache_tracks_merge_and_deduplication() -> None:
    mesh = _quad_mesh()
    other = Mesh(
        np.array([[2.0, 0.0, 0.0], [3.0, 0.0, 0.0], [2.0, 1.0, 0.0]]),
        np.array([[0, 1, 2]]),
    )
    mesh.add_to_mesh(other)
    _assert_edges_consistent(mesh)

    mesh.remove_duplicate_vertices()
    _assert_edges_consistent(mesh)
    mesh.remove_duplicate_faces()
    _assert_edges_consistent(mesh)


def test_find_part_is_order_insensitive() -> None:
    mesh = _quad_mesh()
    assert mesh.find_part(np.array([1, 0])) == [0]
    assert mesh.find_part(np.array([0, 1])) == [0]


def test_remove_duplicate_parts_handles_reordered_faces() -> None:
    mesh = _quad_mesh()
    mesh.add_parts([np.array([0, 1]), np.array([1, 0])])
    mesh.remove_duplicate_parts()
    assert len(mesh.parts) == 1


def test_fast_manim_mesh_supports_mesh_updates() -> None:
    mesh = _quad_mesh()
    fast = FastManimMesh(mesh)

    np.testing.assert_array_equal(fast.get_triangle_indices(), [0, 1, 2, 0, 2, 3])

    fast.add_face(np.array([1, 2, 3]))
    np.testing.assert_array_equal(
        fast.get_triangle_indices(), [0, 1, 2, 0, 2, 3, 1, 2, 3]
    )
    _assert_edges_consistent(fast.mesh)

    fast.remove_face(0)
    np.testing.assert_array_equal(fast.get_triangle_indices(), [0, 2, 3, 1, 2, 3])

    fast.update_vertex(0, np.array([-1.0, 0.0, 0.0]))
    np.testing.assert_array_equal(fast.points[0], [-1.0, 0.0, 0.0])

    replacement = Mesh(
        np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]),
        np.array([[0, 1, 2]]),
    )
    fast.set_mesh(replacement)
    np.testing.assert_array_equal(fast.get_triangle_indices(), [0, 1, 2])


def test_fast_manim_mesh_rejects_non_triangle_add() -> None:
    fast = FastManimMesh(_quad_mesh())
    with pytest.raises(ValueError, match="three"):
        fast.add_face(np.array([0, 1]))

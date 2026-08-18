# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


from manim import *
import numpy as np
import pytest


@pytest.fixture
def scene():
    """Provide a fresh Manim Scene for testing."""
    return Scene()


@pytest.fixture
def triangle_vertices():
    """Simple 2D triangle vertices."""
    return np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.5, 1.0, 0.0]])


@pytest.fixture
def triangle_faces():
    """Face for a single triangle."""
    return [np.array([0, 1, 2])]


@pytest.fixture
def square_vertices():
    """Simple 2D square vertices."""
    return np.array([
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [1.0, 1.0, 0.0],
        [0.0, 1.0, 0.0],
    ])


@pytest.fixture
def square_faces():
    """Two triangles forming a square."""
    return [np.array([0, 1, 2]), np.array([0, 2, 3])]


@pytest.fixture
def cube_vertices():
    """Simple 3D cube vertices."""
    return np.array([
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [1.0, 1.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
        [1.0, 0.0, 1.0],
        [1.0, 1.0, 1.0],
        [0.0, 1.0, 1.0],
    ])


@pytest.fixture
def cube_faces():
    """Six faces for a cube (each a triangle fan)."""
    return [
        np.array([0, 1, 2]), np.array([0, 2, 3]),
        np.array([4, 5, 6]), np.array([4, 6, 7]),
        np.array([0, 1, 5]), np.array([0, 5, 4]),
        np.array([2, 3, 7]), np.array([2, 7, 6]),
        np.array([1, 2, 6]), np.array([1, 6, 5]),
        np.array([0, 3, 7]), np.array([0, 7, 4]),
    ]


@pytest.fixture
def simple_mesh_data(triangle_vertices, triangle_faces):
    """A single-triangle Mesh object."""
    from manim_extensions.meshes.models.data_models.mesh import Mesh
    return Mesh(triangle_vertices, triangle_faces)


@pytest.fixture
def square_mesh_data(square_vertices, square_faces):
    """A square (2 triangles) Mesh object."""
    from manim_extensions.meshes.models.data_models.mesh import Mesh
    return Mesh(square_vertices, square_faces)


@pytest.fixture
def cube_mesh_data(cube_vertices, cube_faces):
    """A cube Mesh object."""
    from manim_extensions.meshes.models.data_models.mesh import Mesh
    return Mesh(cube_vertices, cube_faces)
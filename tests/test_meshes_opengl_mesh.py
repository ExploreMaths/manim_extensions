import numpy as np
import pytest

from manim_extensions.meshes.models.data_models.mesh import Mesh
from manim_extensions.meshes.models.manim_models.opengl_mesh import FastManimMesh


def _triangle_mesh():
    return Mesh(
        np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]),
        np.array([[0, 1, 2]]),
    )


def test_quad_faces_are_rejected():
    mesh = Mesh(np.zeros((4, 3)), np.array([[0, 1, 2, 3]]))
    with pytest.raises(ValueError, match="triangles"):
        FastManimMesh(mesh)


def test_triangle_indices_and_points():
    mesh = _triangle_mesh()
    mobject = FastManimMesh(mesh)

    np.testing.assert_array_equal(mobject.get_triangle_indices(), [0, 1, 2])
    np.testing.assert_array_equal(mobject.get_shader_vert_indices(), [0, 1, 2])
    mobject.init_points()
    assert mobject.points.shape[0] == 3


def test_shader_data_contains_colors():
    mobject = FastManimMesh(_triangle_mesh())
    data = mobject.get_shader_data()

    assert data.dtype.names == ("point", "color")
    assert len(data) == 3

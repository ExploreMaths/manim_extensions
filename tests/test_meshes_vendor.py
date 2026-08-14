import numpy as np
import pytest

from manim_extensions.meshes.models.data_models.mesh import Mesh
from manim_extensions.meshes.exceptions import (
    InvalidMeshException,
    MeshIndexException,
    InvalidTypeException,
    InvalidMeshDimensionsException,
    InvalidRequestException,
)
from manim_extensions.meshes.helpers import (
    is_in_vararray,
    find_in_vararray,
    is_vararray_equal,
    is_twice_nested_iterable,
    are_edges_equal,
    fix_references,
    remove_keys_from_dict,
)
from manim_extensions.meshes.types import Edge, VarArray


class TestMeshInit:
    def test_init_with_vertices_and_faces(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0]])
        faces = [np.array([0, 1, 2])]
        mesh = Mesh(verts, faces)
        assert mesh.dim == 3
        assert len(mesh.vertices) == 3
        assert len(mesh.faces) == 1
        assert len(mesh.parts) == 0

    def test_init_with_parts(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0], [0.5, 0.5, 1]])
        faces = [np.array([0, 1, 2]), np.array([0, 1, 3])]
        parts = [np.array([0, 1])]
        mesh = Mesh(verts, faces, parts)
        assert len(mesh.parts) == 1

    def test_init_without_faces(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0]])
        mesh = Mesh(verts, None)
        assert len(mesh.faces) == 0

    def test_init_2d_vertices(self):
        verts = np.array([[0, 0], [1, 0], [0.5, 1]])
        faces = [np.array([0, 1, 2])]
        mesh = Mesh(verts, faces)
        assert mesh.dim == 2

    def test_init_1d_vertices(self):
        verts = np.array([[0], [1], [2]])
        faces = [np.array([0, 1, 2])]
        mesh = Mesh(verts, faces)
        assert mesh.dim == 1

    def test_init_invalid_faces_type(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0]])
        with pytest.raises(InvalidMeshException):
            Mesh(verts, "not_a_list")

    def test_init_parts_without_faces(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0]])
        with pytest.raises(InvalidMeshException):
            Mesh(verts, None, parts=[np.array([0])])

    def test_init_parts_invalid_type(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0]])
        faces = [np.array([0, 1, 2])]
        with pytest.raises(InvalidMeshException):
            Mesh(verts, faces, parts="invalid")

    def test_init_mismatched_vertex_dims(self):
        verts = [[0, 0, 0], [1, 0], [0.5, 1, 0]]
        with pytest.raises(InvalidMeshException):
            Mesh(verts, None)

    def test_extract_edges(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0]])
        faces = [np.array([0, 1, 2])]
        mesh = Mesh(verts, faces)
        assert len(mesh.edges) == 3


class TestMeshProperties:
    def test_vertices_property(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0]])
        mesh = Mesh(verts, None)
        assert np.array_equal(mesh.vertices, verts)

    def test_faces_property(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0]])
        faces = [np.array([0, 1, 2])]
        mesh = Mesh(verts, faces)
        assert len(mesh.faces) == 1

    def test_parts_property(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0], [0.5, 0.5, 1]])
        faces = [np.array([0, 1, 2]), np.array([0, 1, 3])]
        parts = [np.array([0])]
        mesh = Mesh(verts, faces, parts)
        assert len(mesh.parts) == 1

    def test_edges_property(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0]])
        faces = [np.array([0, 1, 2])]
        mesh = Mesh(verts, faces)
        assert isinstance(mesh.edges, list)
        assert all(isinstance(e, tuple) and len(e) == 2 for e in mesh.edges)

    def test_dim_property(self):
        verts_3d = np.array([[0, 0, 0], [1, 0, 0]])
        mesh = Mesh(verts_3d, None)
        assert mesh.dim == 3

        verts_2d = np.array([[0, 0], [1, 0]])
        mesh2 = Mesh(verts_2d, None)
        assert mesh2.dim == 2


class TestMeshGet3DVertices:
    def test_2d_to_3d(self):
        verts = np.array([[0, 0], [1, 0], [0.5, 1]])
        mesh = Mesh(verts, None)
        result = mesh.get_3d_vertices()
        assert result.shape == (3, 3)
        assert np.array_equal(result[:, 2], np.zeros(3))

    def test_1d_to_3d(self):
        verts = np.array([[0], [1], [2]])
        mesh = Mesh(verts, None)
        result = mesh.get_3d_vertices()
        assert result.shape == (3, 3)

    def test_3d_unchanged(self):
        verts = np.array([[0, 0, 0], [1, 0, 0]])
        mesh = Mesh(verts, None)
        result = mesh.get_3d_vertices()
        assert np.array_equal(result, verts)

    def test_4d_raises(self):
        verts = np.array([[0, 0, 0, 0], [1, 0, 0, 0]])
        mesh = Mesh(verts, None)
        with pytest.raises(InvalidRequestException):
            mesh.get_3d_vertices()

    def test_convert_vertices_to_3d(self):
        verts = np.array([[0, 0], [1, 0], [0.5, 1]])
        mesh = Mesh(verts, None)
        mesh.convert_vertices_to_3d()
        assert mesh.dim == 3

    def test_convert_vertices_to_3d_already_3d(self):
        verts = np.array([[0, 0, 0], [1, 0, 0]])
        mesh = Mesh(verts, None)
        mesh.convert_vertices_to_3d()
        assert mesh.dim == 3

    def test_convert_4d_raises(self):
        verts = np.array([[0, 0, 0, 0], [1, 0, 0, 0]])
        mesh = Mesh(verts, None)
        with pytest.raises(InvalidRequestException):
            mesh.convert_vertices_to_3d()


class TestMeshVertexOps:
    def test_add_vertices(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0]])
        mesh = Mesh(verts, None)
        new_verts = np.array([[2, 0, 0], [2.5, 1, 0]])
        mesh.add_vertices(new_verts)
        assert len(mesh.vertices) == 5

    def test_add_vertices_invalid_type(self):
        verts = np.array([[0, 0, 0], [1, 0, 0]])
        mesh = Mesh(verts, None)
        with pytest.raises(InvalidMeshException):
            mesh.add_vertices([[2, 0, 0]])

    def test_add_vertices_invalid_dim(self):
        verts = np.array([[0, 0, 0], [1, 0, 0]])
        mesh = Mesh(verts, None)
        with pytest.raises(InvalidMeshDimensionsException):
            mesh.add_vertices(np.array([[2, 0]]))

    def test_remove_vertices(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0]])
        faces = [np.array([0, 1, 2])]
        mesh = Mesh(verts, faces)
        mesh.remove_vertices([2])
        assert len(mesh.vertices) == 2

    def test_remove_vertices_out_of_range(self):
        verts = np.array([[0, 0, 0], [1, 0, 0]])
        mesh = Mesh(verts, None)
        with pytest.raises(MeshIndexException):
            mesh.remove_vertices([5])

    def test_remove_vertices_negative(self):
        verts = np.array([[0, 0, 0], [1, 0, 0]])
        mesh = Mesh(verts, None)
        with pytest.raises(MeshIndexException):
            mesh.remove_vertices([-1])

    def test_update_vertex(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0]])
        mesh = Mesh(verts, None)
        mesh.update_vertex(0, np.array([10, 10, 10]))
        assert np.array_equal(mesh.vertices[0], np.array([10, 10, 10]))

    def test_update_vertex_out_of_range(self):
        verts = np.array([[0, 0, 0], [1, 0, 0]])
        mesh = Mesh(verts, None)
        with pytest.raises(MeshIndexException):
            mesh.update_vertex(5, np.array([10, 10, 10]))

    def test_update_vertex_invalid_shape(self):
        verts = np.array([[0, 0, 0], [1, 0, 0]])
        mesh = Mesh(verts, None)
        with pytest.raises(InvalidTypeException):
            mesh.update_vertex(0, np.array([[10, 10, 10]]))

    def test_update_vertex_wrong_dim(self):
        verts = np.array([[0, 0, 0], [1, 0, 0]])
        mesh = Mesh(verts, None)
        with pytest.raises(InvalidMeshException):
            mesh.update_vertex(0, np.array([10, 10]))

    def test_find_vertex(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0]])
        mesh = Mesh(verts, None)
        result = mesh.find_vertex(np.array([1, 0, 0]))
        assert result == [1]

    def test_find_vertex_not_found(self):
        verts = np.array([[0, 0, 0], [1, 0, 0]])
        mesh = Mesh(verts, None)
        result = mesh.find_vertex(np.array([99, 99, 99]))
        assert result == []

    def test_find_vertex_wrong_dim(self):
        verts = np.array([[0, 0, 0], [1, 0, 0]])
        mesh = Mesh(verts, None)
        result = mesh.find_vertex(np.array([1, 0]))
        assert result == []


class TestMeshFaceOps:
    def test_add_faces(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0], [0, 1, 0]])
        mesh = Mesh(verts, None)
        mesh.add_faces([np.array([0, 1, 2])])
        assert len(mesh.faces) == 1

    def test_add_faces_multiple(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0], [0, 1, 0]])
        mesh = Mesh(verts, None)
        mesh.add_faces([np.array([0, 1, 2]), np.array([0, 2, 3])])
        assert len(mesh.faces) == 2

    def test_add_faces_invalid_type(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0]])
        mesh = Mesh(verts, None)
        with pytest.raises(InvalidMeshException):
            mesh.add_faces("not_valid")

    def test_add_faces_out_of_range(self):
        verts = np.array([[0, 0, 0], [1, 0, 0]])
        mesh = Mesh(verts, None)
        with pytest.raises(MeshIndexException):
            mesh.add_faces([np.array([0, 1, 5])])

    def test_remove_faces(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0], [0, 1, 0]])
        faces = [np.array([0, 1, 2]), np.array([0, 2, 3])]
        mesh = Mesh(verts, faces)
        mesh.remove_faces([0])
        assert len(mesh.faces) == 1

    def test_remove_faces_out_of_range(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0]])
        faces = [np.array([0, 1, 2])]
        mesh = Mesh(verts, faces)
        with pytest.raises(MeshIndexException):
            mesh.remove_faces([5])

    def test_update_face(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0], [0, 1, 0]])
        faces = [np.array([0, 1, 2])]
        mesh = Mesh(verts, faces)
        mesh.update_face(0, np.array([0, 1, 3]))
        assert np.array_equal(mesh.faces[0], np.array([0, 1, 3]))

    def test_update_face_out_of_range(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0]])
        faces = [np.array([0, 1, 2])]
        mesh = Mesh(verts, faces)
        with pytest.raises(MeshIndexException):
            mesh.update_face(5, np.array([0, 1, 2]))

    def test_update_face_invalid_shape(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0]])
        faces = [np.array([0, 1, 2])]
        mesh = Mesh(verts, faces)
        with pytest.raises(InvalidTypeException):
            mesh.update_face(0, np.array([[0, 1, 2]]))

    def test_update_face_wrong_vertex_index(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0]])
        faces = [np.array([0, 1, 2])]
        mesh = Mesh(verts, faces)
        with pytest.raises(MeshIndexException):
            mesh.update_face(0, np.array([0, 1, 99]))

    def test_find_face(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0]])
        faces = [np.array([0, 1, 2])]
        mesh = Mesh(verts, faces)
        result = mesh.find_face(np.array([0, 1, 2]))
        assert result == [0]

    def test_find_face_not_found(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0]])
        faces = [np.array([0, 1, 2])]
        mesh = Mesh(verts, faces)
        result = mesh.find_face(np.array([0, 1, 0]))
        assert result == []


class TestMeshPartOps:
    def test_add_parts(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0], [0.5, 0.5, 1]])
        faces = [np.array([0, 1, 2]), np.array([0, 1, 3])]
        mesh = Mesh(verts, faces)
        mesh.add_parts([np.array([0, 1])])
        assert len(mesh.parts) == 1

    def test_add_parts_invalid_type(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0]])
        faces = [np.array([0, 1, 2])]
        mesh = Mesh(verts, faces)
        with pytest.raises(InvalidMeshException):
            mesh.add_parts("invalid")

    def test_add_parts_out_of_range(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0]])
        faces = [np.array([0, 1, 2])]
        mesh = Mesh(verts, faces)
        with pytest.raises(MeshIndexException):
            mesh.add_parts([np.array([0, 5])])

    def test_remove_parts(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0], [0.5, 0.5, 1]])
        faces = [np.array([0, 1, 2]), np.array([0, 1, 3])]
        parts = [np.array([0]), np.array([1])]
        mesh = Mesh(verts, faces, parts)
        mesh.remove_parts([0])
        assert len(mesh.parts) == 1

    def test_remove_parts_out_of_range(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0]])
        faces = [np.array([0, 1, 2])]
        parts = [np.array([0])]
        mesh = Mesh(verts, faces, parts)
        with pytest.raises(MeshIndexException):
            mesh.remove_parts([5])

    def test_update_part(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0], [0.5, 0.5, 1]])
        faces = [np.array([0, 1, 2]), np.array([0, 1, 3])]
        parts = [np.array([0])]
        mesh = Mesh(verts, faces, parts)
        mesh.update_part(0, np.array([1]))
        assert np.array_equal(mesh.parts[0], np.array([1]))

    def test_update_part_out_of_range(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0]])
        faces = [np.array([0, 1, 2])]
        parts = [np.array([0])]
        mesh = Mesh(verts, faces, parts)
        with pytest.raises(MeshIndexException):
            mesh.update_part(5, np.array([0]))

    def test_find_part(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0], [0.5, 0.5, 1]])
        faces = [np.array([0, 1, 2]), np.array([0, 1, 3])]
        parts = [np.array([0])]
        mesh = Mesh(verts, faces, parts)
        result = mesh.find_part(np.array([0]))
        assert result == [0]

    def test_get_vertices_from_part_id(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0], [0.5, 0.5, 1]])
        faces = [np.array([0, 1, 2]), np.array([0, 1, 3])]
        parts = [np.array([0])]
        mesh = Mesh(verts, faces, parts)
        result = mesh.get_vertices_from_part_id(0)
        assert set(result) == {0, 1, 2}


class TestMeshEdgeOps:
    def test_get_edge_index(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0]])
        faces = [np.array([0, 1, 2])]
        mesh = Mesh(verts, faces)
        idx = mesh.get_edge_index((0, 1))
        assert isinstance(idx, int)

    def test_get_edge_index_not_found(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0]])
        faces = [np.array([0, 1, 2])]
        mesh = Mesh(verts, faces)
        with pytest.raises(ValueError):
            mesh.get_edge_index((5, 6))

    def test_get_vertex_edges(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0]])
        faces = [np.array([0, 1, 2])]
        mesh = Mesh(verts, faces)
        result = mesh.get_vertex_edges(0)
        assert len(result) == 2

    def test_get_vertex_edges_isolated(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0]])
        mesh = Mesh(verts, None)
        result = mesh.get_vertex_edges(0)
        assert result == []


class TestMeshMerge:
    def test_add_mesh(self):
        verts1 = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0]])
        verts2 = np.array([[2, 0, 0], [3, 0, 0], [2.5, 1, 0]])
        mesh1 = Mesh(verts1, [np.array([0, 1, 2])])
        mesh2 = Mesh(verts2, [np.array([0, 1, 2])])
        result = mesh1 + mesh2
        assert len(result.vertices) == 6

    def test_add_non_mesh(self):
        verts = np.array([[0, 0, 0], [1, 0, 0]])
        mesh = Mesh(verts, None)
        with pytest.raises(NotImplementedError):
            mesh + "not_a_mesh"

    def test_iadd_mesh(self):
        verts1 = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0]])
        verts2 = np.array([[2, 0, 0], [3, 0, 0], [2.5, 1, 0]])
        mesh1 = Mesh(verts1, [np.array([0, 1, 2])])
        mesh2 = Mesh(verts2, [np.array([0, 1, 2])])
        mesh1 += mesh2
        assert len(mesh1.vertices) == 6

    def test_iadd_non_mesh(self):
        verts = np.array([[0, 0, 0], [1, 0, 0]])
        mesh = Mesh(verts, None)
        with pytest.raises(NotImplementedError):
            mesh += "not_a_mesh"


class TestMeshEquality:
    def test_equal_meshes(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0]])
        faces = [np.array([0, 1, 2])]
        mesh1 = Mesh(verts, faces)
        mesh2 = Mesh(verts.copy(), [np.array([0, 1, 2])])
        assert mesh1 == mesh2

    def test_not_equal_meshes(self):
        verts1 = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0]])
        verts2 = np.array([[0, 0, 0], [2, 0, 0], [0.5, 1, 0]])
        mesh1 = Mesh(verts1, [np.array([0, 1, 2])])
        mesh2 = Mesh(verts2, [np.array([0, 1, 2])])
        assert mesh1 != mesh2

    def test_equal_mesh_non_mesh(self):
        verts = np.array([[0, 0, 0], [1, 0, 0]])
        mesh = Mesh(verts, None)
        with pytest.raises(NotImplementedError):
            mesh == "not_a_mesh"

    def test_ne_mesh_non_mesh(self):
        verts = np.array([[0, 0, 0], [1, 0, 0]])
        mesh = Mesh(verts, None)
        with pytest.raises(NotImplementedError):
            mesh != "not_a_mesh"


class TestMeshDuplicates:
    def test_remove_duplicate_vertices(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0, 0, 0], [0.5, 1, 0]])
        mesh = Mesh(verts, [np.array([0, 1, 3])])
        mesh.remove_duplicate_vertices()
        assert len(mesh.vertices) == 3

    def test_remove_duplicate_faces(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0]])
        faces = [np.array([0, 1, 2]), np.array([0, 1, 2])]
        mesh = Mesh(verts, faces)
        mesh.remove_duplicate_faces()
        assert len(mesh.faces) == 1

    def test_remove_duplicate_parts(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0], [0.5, 0.5, 1]])
        faces = [np.array([0, 1, 2]), np.array([0, 1, 3])]
        parts = [np.array([0]), np.array([0])]
        mesh = Mesh(verts, faces, parts)
        mesh.remove_duplicate_parts()
        assert len(mesh.parts) == 1


class TestHelpers:
    def test_is_in_vararray_rolling(self):
        arr = [np.array([1, 2, 3]), np.array([4, 5, 6])]
        assert is_in_vararray(arr, np.array([2, 3, 1]), rolling=True)
        assert not is_in_vararray(arr, np.array([1, 3, 2]), rolling=True)

    def test_is_in_vararray_no_rolling(self):
        arr = [np.array([1, 2, 3])]
        assert is_in_vararray(arr, np.array([1, 2, 3]), rolling=False)
        assert not is_in_vararray(arr, np.array([2, 3, 1]), rolling=False)

    def test_find_in_vararray(self):
        arr = [np.array([1, 2, 3]), np.array([4, 5, 6]), np.array([1, 2, 3])]
        result = find_in_vararray(arr, np.array([1, 2, 3]))
        assert result == [0, 2]

    def test_find_in_vararray_with_start(self):
        arr = [np.array([1, 2, 3]), np.array([4, 5, 6]), np.array([1, 2, 3])]
        result = find_in_vararray(arr, np.array([1, 2, 3]), start=1)
        assert result == [2]

    def test_is_vararray_equal(self):
        arr1 = [np.array([1, 2, 3]), np.array([4, 5, 6])]
        arr2 = [np.array([4, 5, 6]), np.array([1, 2, 3])]
        assert is_vararray_equal(arr1, arr2, rolling=True)

    def test_is_vararray_equal_not_equal(self):
        arr1 = [np.array([1, 2, 3])]
        arr2 = [np.array([1, 2, 4])]
        assert not is_vararray_equal(arr1, arr2)

    def test_is_twice_nested_iterable_2d_array(self):
        obj = np.array([[1, 2, 3], [4, 5, 6]])
        assert is_twice_nested_iterable(obj)

    def test_is_twice_nested_iterable_list(self):
        obj = [[1, 2, 3], [4, 5, 6]]
        assert is_twice_nested_iterable(obj)

    def test_is_twice_nested_iterable_empty(self):
        assert is_twice_nested_iterable([])

    def test_is_twice_nested_iterable_too_small(self):
        obj = np.array([[1]])
        assert not is_twice_nested_iterable(obj)

    def test_is_twice_nested_iterable_not_iterable(self):
        assert not is_twice_nested_iterable("string")

    def test_are_edges_equal(self):
        edges1 = [(0, 1), (1, 2)]
        edges2 = [(1, 2), (0, 1)]
        assert are_edges_equal(edges1, edges2)

    def test_are_edges_not_equal(self):
        edges1 = [(0, 1)]
        edges2 = [(0, 2)]
        assert not are_edges_equal(edges1, edges2)

    def test_fix_references(self):
        original = [np.array([0, 1, 2]), np.array([1, 2, 3]), np.array([4, 5])]
        indices = [1]
        removed = fix_references(original, indices)
        assert removed == [0, 1]
        assert len(original) == 1

    def test_remove_keys_from_dict(self):
        d = {"a": 1, "b": 2, "c": 3}
        result = remove_keys_from_dict(d, ["a", "c"])
        assert "a" not in result
        assert "c" not in result
        assert result["b"] == 2

    def test_remove_keys_from_dict_missing_key(self):
        d = {"a": 1}
        result = remove_keys_from_dict(d, ["b"])
        assert result == {"a": 1}

    def test_remove_keys_from_dict_none(self):
        result = remove_keys_from_dict(None, ["a"])
        assert result == {}


class TestMeshTransform:
    def test_scale_mesh(self):
        verts = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
        mesh = Mesh(verts, None)
        mesh.scale_mesh(2.0)
        assert np.array_equal(mesh.vertices, np.array([[0.0, 0.0, 0.0], [2.0, 0.0, 0.0], [0.0, 2.0, 0.0]]))

    def test_scale_mesh_about_point(self):
        verts = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
        mesh = Mesh(verts, None)
        mesh.scale_mesh(2.0, about_point=np.array([1.0, 0.0, 0.0]))
        assert mesh.vertices[0][0] == pytest.approx(-1.0)
        assert mesh.vertices[1][0] == pytest.approx(1.0)

    def test_stretch_mesh(self):
        verts = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
        mesh = Mesh(verts, None)
        mesh.stretch_mesh(2.0, dim=0)
        assert mesh.vertices[1][0] == pytest.approx(2.0)
        assert mesh.vertices[2][1] == pytest.approx(1.0)

    def test_stretch_mesh_about_point(self):
        verts = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
        mesh = Mesh(verts, None)
        mesh.stretch_mesh(2.0, dim=1, about_point=np.array([0.0, 1.0, 0.0]))
        assert mesh.vertices[0][1] == pytest.approx(-1.0)
        assert mesh.vertices[2][1] == pytest.approx(1.0)

    def test_translate_mesh(self):
        verts = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
        mesh = Mesh(verts, None)
        mesh.translate_mesh(np.array([1.0, 2.0, 3.0]))
        assert mesh.vertices[0][0] == pytest.approx(1.0)
        assert mesh.vertices[0][1] == pytest.approx(2.0)
        assert mesh.vertices[0][2] == pytest.approx(3.0)

    def test_translate_mesh_invalid_type(self):
        verts = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
        mesh = Mesh(verts, None)
        with pytest.raises(InvalidTypeException):
            mesh.translate_mesh([1.0, 2.0, 3.0])

    def test_translate_mesh_invalid_dim(self):
        verts = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
        mesh = Mesh(verts, None)
        with pytest.raises(InvalidMeshDimensionsException):
            mesh.translate_mesh(np.array([1.0, 2.0]))

    def test_translate_vertex(self):
        verts = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
        mesh = Mesh(verts, None)
        mesh.translate_vertex(0, np.array([1.0, 1.0, 1.0]))
        assert mesh.vertices[0][0] == pytest.approx(1.0)
        assert mesh.vertices[1][0] == pytest.approx(1.0)

    def test_translate_vertex_out_of_range(self):
        verts = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
        mesh = Mesh(verts, None)
        with pytest.raises(MeshIndexException):
            mesh.translate_vertex(5, np.array([1.0, 1.0, 1.0]))

    def test_translate_vertex_invalid_type(self):
        verts = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
        mesh = Mesh(verts, None)
        with pytest.raises(InvalidTypeException):
            mesh.translate_vertex(0, [1.0, 2.0, 3.0])

    def test_translate_vertex_invalid_dim(self):
        verts = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
        mesh = Mesh(verts, None)
        with pytest.raises(InvalidMeshDimensionsException):
            mesh.translate_vertex(0, np.array([1.0, 2.0]))

    def test_apply_rotation_2d(self):
        verts = np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]])
        mesh = Mesh(verts, None)
        mesh.apply_rotation(np.pi / 2)
        assert mesh.vertices[0][0] == pytest.approx(0.0, abs=1e-10)
        assert mesh.vertices[1][1] == pytest.approx(1.0, abs=1e-10)

    def test_apply_rotation_about_point(self):
        verts = np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]])
        mesh = Mesh(verts, None)
        mesh.apply_rotation(np.pi / 2, about_point=np.array([1.0, 0.0]))
        assert mesh.vertices[1][0] == pytest.approx(1.0, abs=1e-10)

    def test_apply_rotation_1d_not_implemented(self):
        verts = np.array([[0.0], [1.0], [2.0]])
        mesh = Mesh(verts, None)
        with pytest.raises(NotImplementedError):
            mesh.apply_rotation(0.5)


class TestMeshSnapToGrid:
    def test_snap_to_grid_basic(self):
        verts = np.array([[0.999, 0.0, 0.0], [1.001, 0.0, 0.0], [0.0, 0.0, 0.0]])
        mesh = Mesh(verts, None)
        result = mesh.snap_to_grid(grid_sizes=(1.0, 1.0, 1.0), threshold=(0.01, 0.01, 0.01))
        assert result[0][0] == pytest.approx(1.0, abs=1e-6)
        assert result[1][0] == pytest.approx(1.0, abs=1e-6)

    def test_snap_to_grid_no_snap(self):
        verts = np.array([[0.5, 0.0, 0.0], [1.6, 0.0, 0.0]])
        mesh = Mesh(verts, None)
        result = mesh.snap_to_grid(grid_sizes=(1.0, 1.0, 1.0), threshold=(0.05, 0.05, 0.05))
        assert result[0][0] == pytest.approx(0.5, abs=1e-6)
        assert result[1][0] == pytest.approx(1.6, abs=1e-6)

    def test_snap_to_grid_update_verts(self):
        verts = np.array([[0.999, 0.0, 0.0], [1.001, 0.0, 0.0]])
        mesh = Mesh(verts, None)
        mesh.snap_to_grid(grid_sizes=(1.0, 1.0, 1.0), threshold=(0.01, 0.01, 0.01), update_verts=True)
        assert mesh.vertices[0][0] == pytest.approx(1.0, abs=1e-6)

    def test_snap_to_grid_invalid_dim(self):
        verts = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
        mesh = Mesh(verts, None)
        with pytest.raises(InvalidMeshDimensionsException):
            mesh.snap_to_grid(grid_sizes=(1.0, 1.0), threshold=(0.01,))

    def test_snap_to_grid_invalid_grid_size(self):
        verts = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
        mesh = Mesh(verts, None)
        with pytest.raises(InvalidRequestException):
            mesh.snap_to_grid(grid_sizes=(0.0, 1.0, 1.0), threshold=(0.01, 0.01, 0.01))

    def test_snap_to_grid_invalid_threshold(self):
        verts = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
        mesh = Mesh(verts, None)
        with pytest.raises(InvalidRequestException):
            mesh.snap_to_grid(grid_sizes=(1.0, 1.0, 1.0), threshold=(0.6, 0.01, 0.01))

    def test_snap_to_grid_all_zero_threshold(self):
        verts = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
        mesh = Mesh(verts, None)
        with pytest.raises(InvalidRequestException):
            mesh.snap_to_grid(grid_sizes=(1.0, 1.0, 1.0), threshold=(0.0, 0.0, 0.0))

    def test_snap_to_grid_negative_steps(self):
        verts = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
        mesh = Mesh(verts, None)
        with pytest.raises(InvalidRequestException):
            mesh.snap_to_grid(grid_sizes=(1.0, 1.0, 1.0), threshold=(0.01, 0.01, 0.01), steps=-1)


class TestMeshDangling:
    def test_dangling_vert_check_no_faces(self):
        verts = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
        mesh = Mesh(verts, None)
        assert mesh.dangling_vert_check() is True

    def test_dangling_vert_check_all_used(self):
        verts = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.5, 1.0, 0.0]])
        faces = [np.array([0, 1, 2])]
        mesh = Mesh(verts, faces)
        assert mesh.dangling_vert_check() is False

    def test_dangling_vert_check_some_dangling(self):
        verts = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.5, 1.0, 0.0], [5.0, 5.0, 5.0]])
        faces = [np.array([0, 1, 2])]
        mesh = Mesh(verts, faces)
        assert mesh.dangling_vert_check() is True

    def test_dangling_face_check_no_parts(self):
        verts = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.5, 1.0, 0.0]])
        faces = [np.array([0, 1, 2])]
        mesh = Mesh(verts, faces)
        assert mesh.dangling_face_check() is True

    def test_dangling_face_check_all_used(self):
        verts = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.5, 1.0, 0.0], [0.5, 0.5, 1.0]])
        faces = [np.array([0, 1, 2]), np.array([0, 1, 3])]
        parts = [np.array([0]), np.array([1])]
        mesh = Mesh(verts, faces, parts)
        assert mesh.dangling_face_check() is False

    def test_dangling_face_check_some_dangling(self):
        verts = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.5, 1.0, 0.0], [0.5, 0.5, 1.0]])
        faces = [np.array([0, 1, 2]), np.array([0, 1, 3])]
        parts = [np.array([0])]
        mesh = Mesh(verts, faces, parts)
        assert mesh.dangling_face_check() is True


class TestMeshSplit:
    def test_split_mesh_into_objects_single(self):
        verts = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.5, 1.0, 0.0]])
        faces = [np.array([0, 1, 2])]
        mesh = Mesh(verts, faces)
        result = mesh.split_mesh_into_objects()
        assert len(result) == 1

    def test_split_mesh_into_objects_two(self):
        verts = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.5, 1.0, 0.0],
                           [2.0, 0.0, 0.0], [3.0, 0.0, 0.0], [2.5, 1.0, 0.0]])
        faces = [np.array([0, 1, 2]), np.array([3, 4, 5])]
        mesh = Mesh(verts, faces)
        result = mesh.split_mesh_into_objects()
        assert len(result) == 2

    def test_split_mesh_into_objects_no_vertices(self):
        verts = np.zeros((0, 3))
        mesh = Mesh(verts, None)
        result = mesh.split_mesh_into_objects()
        assert len(result) == 0


class TestMeshRemoveDuplicates:
    def test_remove_duplicates(self):
        verts = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.5, 1.0, 0.0]])
        faces = [np.array([0, 1, 3]), np.array([0, 1, 3])]
        mesh = Mesh(verts, faces)
        mesh.remove_duplicates()
        assert len(mesh.vertices) == 3
        assert len(mesh.faces) == 1
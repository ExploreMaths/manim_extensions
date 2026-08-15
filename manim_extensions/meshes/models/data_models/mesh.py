"""
Mesh structure
"""
# python imports
from copy import deepcopy
# third-party imports
from typing import List, Set, Tuple, Union
import numpy as np
# local imports
from scipy.spatial.transform import Rotation

from manim_extensions.meshes.decorators import dangling_face_decorator, dangling_vert_decorator
from manim_extensions.meshes.exceptions import InvalidMeshDimensionsException, InvalidMeshException, InvalidRequestException, \
    InvalidTypeException, MeshIndexException
from manim_extensions.meshes.helpers import find_in_vararray, is_vararray_equal, fix_references, is_twice_nested_iterable
from manim_extensions.meshes.types import Edge, VarArray, Vertex, Vertices, Face, Faces, Part, Parts, Edges


class Mesh:
    """Basic mesh structure based on vertices and faces. For 3D objects parts is additionally used.

    Examples
    --------
    .. manim:: MeshExample
       :save_last_frame:

       from manim import *
       from manim_extensions.meshes.models.data_models.mesh import Mesh

       class MeshExample(Scene):
           def construct(self):
               vertices = [[0, 0, 0], [1, 0, 0], [0.5, 1, 0]]
               faces = [[0, 1, 2]]
               mesh = Mesh(vertices, faces)
               label = Text(f"Mesh: {len(mesh.vertices)} verts, {len(mesh.faces)} faces", font_size=24)
               self.add(label)
"""

    @dangling_vert_decorator()
    @dangling_face_decorator()
    def __init__(self, vertices, faces, parts=None, dangling: bool = False):
        """Initialize mesh with the correct internal structure for all variables.

        Faces and parts are stored as :class:`VarArray` objects so that
        each entry may contain a variable number of elements (e.g. a mix
        of triangles and quadrilaterals).

        Parameters
        ----------
        vertices : array-like
            List of vertices, all with the same dimensionality
            (shape ``[N, d]``).
        faces : 2D array-like or None
            List of faces, each face being a list of vertex indices.
            Entries may have different lengths.
        parts : 2D array-like or None
            List of parts (3D objects), each part being a list of face
            indices.  Cannot be set when *faces* is ``None``.
        dangling : bool, optional
            If ``True``, check and warn about dangling vertices and faces
            after each operation (default ``False``).

        Raises
        ------
        InvalidMeshException
            If *faces* or *parts* have incorrect nested structure, or
            if *parts* is provided without *faces*.
        """
        # check vertices, faces and parts for correct types
        if faces is not None and not is_twice_nested_iterable(faces):
            raise InvalidMeshException("Faces have to be twice nested enumerates.")
        if parts is not None and faces is None:
            raise InvalidMeshException("Parts can not be defined while faces is None.")
        if parts is not None and not is_twice_nested_iterable(parts, min_lens=(1, 1)):
            raise InvalidMeshException("Parts have to be twice nested enumerates or None.")

        # indirectly check vertices
        try:
            conv_vertices = np.array(vertices, dtype=float)
            # if array or inner array could not be broadcast, one of the exceptions should be raised
            if len(conv_vertices.shape) != 2:
                raise InvalidMeshException("Could not broadcast vertices to np.array of shape 2. Dimensional mismatch "
                                           "for vertices. All vertices should have the same number of dimensions.")
        except (TypeError, ValueError) as e:
            raise InvalidMeshException("Dimensional mismatch for vertices. All vertices should have the same number of "
                                       "dimensions.") from e
        # set class variables
        self._vertices: Vertices = conv_vertices
        self._faces: Faces = [np.array(f, dtype=int) for f in faces] if faces is not None else []
        self._parts: Parts = [np.array(p, dtype=int) for p in parts] if parts is not None else []
        self._edges = self.extract_edges()
        self.test_for_dangling = dangling

    def __add__(self, other: 'Mesh') -> 'Mesh':
        """Concatenate *other* mesh into this mesh (``mesh + other``).

        Parameters
        ----------
        other : Mesh
            Another mesh to merge into this one.

        Returns
        -------
        Mesh
            The modified mesh instance.

        Raises
        ------
        NotImplementedError
            If *other* is not a :class:`Mesh`.
        """
        if isinstance(other, Mesh):
            self.add_to_mesh(other)
            return self
        raise NotImplementedError

    def __iadd__(self, other: 'Mesh') -> 'Mesh':
        """Concatenate *other* mesh in-place (``mesh += other``).

        Parameters
        ----------
        other : Mesh
            Another mesh to merge into this one.

        Returns
        -------
        Mesh
            The modified mesh instance.

        Raises
        ------
        NotImplementedError
            If *other* is not a :class:`Mesh`.
        """
        if isinstance(other, Mesh):
            self.add_to_mesh(other)
            return self
        raise NotImplementedError

    def __eq__(self, other: 'Mesh') -> bool:
        """Check whether two meshes are equal.

        Two meshes are considered equal when their vertex coordinates
        match exactly and their face/part references resolve to the
        same coordinates (allowing cyclic permutations).

        Parameters
        ----------
        other : Mesh
            Another mesh to compare against.

        Returns
        -------
        bool
            ``True`` if the meshes are equal.

        Raises
        ------
        NotImplementedError
            If *other* is not a :class:`Mesh`.
        """

        def replace_part_ids_with_vertex_ids(parts: Parts, faces: Faces, vertices: Vertices) -> VarArray:
            """Resolve part → face → vertex references into flat coordinate arrays.

            Parameters
            ----------
            parts : Parts
                Part definitions referencing face indices.
            faces : Faces
                Face definitions referencing vertex indices.
            vertices : Vertices
                Vertex coordinate array.

            Returns
            -------
            VarArray
                A list of coordinate arrays, one per part.
            """
            return [
                np.hstack([np.hstack([vertices[vert_idx] for vert_idx in faces[face_idx]])
                          for face_idx in part]) for part in parts
            ]

        def replace_face_ids_with_vertex_ids(faces: Faces, vertices: Vertices) -> VarArray:
            """Resolve face → vertex references into flat coordinate arrays.

            Parameters
            ----------
            faces : Faces
                Face definitions referencing vertex indices.
            vertices : Vertices
                Vertex coordinate array.

            Returns
            -------
            VarArray
                A list of coordinate arrays, one per face.
            """
            return [np.hstack([vertices[vert_idx] for vert_idx in face]) for face in faces]

        if isinstance(other, Mesh):
            # vertex array contain every other vertex, coordinates must be exact equal, no rolling
            # faces reference the same coordinates
            # parts reference the same coordinates
            if is_vararray_equal(list(self.vertices), list(other.vertices), rolling=False) and \
                    is_vararray_equal(
                        replace_face_ids_with_vertex_ids(self.faces, self.vertices),
                        replace_face_ids_with_vertex_ids(other.faces, other.vertices),
                        rolling=True,
                    ) and \
                    is_vararray_equal(
                        replace_part_ids_with_vertex_ids(self.parts, self.faces, self.vertices),
                        replace_part_ids_with_vertex_ids(other.parts, other.faces, other.vertices),
                        rolling=True,
                    ):
                return True
            return False
        raise NotImplementedError(f'Not equal is not defined for mesh and {type(other)}')

    def __ne__(self, other: 'Mesh') -> bool:
        """Check whether two meshes are not equal.

        Parameters
        ----------
        other : Mesh
            Another mesh to compare against.

        Returns
        -------
        bool
            ``True`` if the meshes are not equal.

        Raises
        ------
        NotImplementedError
            If *other* is not a :class:`Mesh`.
        """
        if isinstance(other, Mesh):
            return not self.__eq__(other)
        raise NotImplementedError(f'Not equal is not defined for mesh and {type(other)}')

    @property
    def dim(self) -> int:
        """get the shape / dimension of every vertex"""
        return self._vertices.shape[1]

    @property
    def vertices(self) -> Vertices:
        """get private property _vertices"""
        return self._vertices

    @property
    def faces(self) -> Faces:
        """get private property _faces"""
        return self._faces

    @property
    def parts(self) -> Parts:
        """get private property _parts"""
        return self._parts

    @property
    def edges(self) -> Edges:
        """get private property _edges"""
        return self._edges

    def get_3d_vertices(self) -> Vertices:
        """Get 3D vertices, for 1D, 2D, 3D meshes, to be able to draw them using the manim functions"""
        if self.dim < 3:
            return np.pad(self._vertices, ((0, 0), (0, 3 - self.dim)))
        if self.dim == 3:
            return self._vertices
        raise InvalidRequestException(f'Can not Broadcast from {self.dim}-D Mesh to 3D Mesh.')

    def get_edge_index(self, edge: Edge) -> int:
        """Return the index of the given edge in the internal edge list.

        Parameters
        ----------
        edge : Edge
            A sorted ``(v_a, v_b)`` tuple representing the edge.

        Returns
        -------
        int
            Index of the edge, or raises if not found.
        """
        # currently edges are sorted indices and not start->end, therefore check for inverse is not necessary
        return self._edges.index(edge)

    def get_vertex_edges(self, vertex_idx: int) -> Edges:
        """Return all edges that contain the given vertex.

        Parameters
        ----------
        vertex_idx : int
            Index of the vertex.

        Returns
        -------
        Edges
            List of edges incident to *vertex_idx*.
        """
        vertex_edges = []
        for edge in self._edges:
            if vertex_idx in edge:
                vertex_edges.append(edge)
        return vertex_edges

    def get_vertices_from_part_id(self, part_id: int) -> List[int]:
        """Return the indices of all vertices contained in the given part.

        Parameters
        ----------
        part_id : int
            Index of the part.

        Returns
        -------
        list of int
            Vertex indices belonging to the part.
        """
        vert_ids = set()
        for face_id in self._parts[part_id]:
            vert_ids.update(set(int(vert_id) for vert_id in self._faces[face_id]))
        return list(vert_ids)

    def convert_vertices_to_3d(self) -> None:
        """transforms currents mesh vertices permanently to be 3D, works if dim is < 3"""
        if self.dim < 3:
            self._vertices = np.pad(self._vertices, ((0, 0), (0, 3 - self.dim)))
        elif self.dim > 3:
            raise InvalidRequestException(f'Can not Broadcast from {self.dim}-D Mesh to 3D Mesh.')

    def find_vertex(self, vertex: np.ndarray, start: int = 0) -> List[int]:
        """Return all vertex indices whose coordinates match *vertex*.

        Parameters
        ----------
        vertex : np.ndarray
            Coordinates to search for.
        start : int, optional
            Index from which the search starts (default ``0``).

        Returns
        -------
        list of int
            Matching vertex indices.  Returns an empty list if the
            coordinate dimension does not match.
        """
        if len(vertex) != self.dim:
            return []
        return [i for i, v in enumerate(self._vertices[start:], start=start)
                if np.array_equal(vertex, v)]

    def find_face(self, face: np.ndarray, start: int = 0) -> List[int]:
        """Return all face indices that match the given face.

        Parameters
        ----------
        face : np.ndarray
            Face vertex indices to search for.
        start : int, optional
            Index from which the search starts (default ``0``).

        Returns
        -------
        list of int
            Matching face indices.
        """
        return find_in_vararray(array=self._faces, item=face, start=start)

    def find_part(self, part: np.ndarray, start: int = 0) -> List[int]:
        """Return all part indices that match the given part.

        Parameters
        ----------
        part : np.ndarray
            Part face indices to search for.
        start : int, optional
            Index from which the search starts (default ``0``).

        Returns
        -------
        list of int
            Matching part indices.
        """
        # Fixme: are two parts equal even if the faces are randomly sorted, not clockwise?
        #  [1,2,3] ?=? [1,3,2] or is it "rolling" like faces?
        return find_in_vararray(array=self._parts, item=part, start=start)

    @dangling_vert_decorator()
    def add_vertices(self, new_vertices: Vertices) -> None:
        """Append new vertices to the mesh.

        Parameters
        ----------
        new_vertices : Vertices
            Array of vertex coordinates to add.

        Raises
        ------
        InvalidMeshException
            If *new_vertices* is not a :class:`numpy.ndarray`.
        InvalidMeshDimensionsException
            If the shape of *new_vertices* does not match the mesh dimension.
        """
        if not isinstance(new_vertices, np.ndarray):
            raise InvalidMeshException(f'new_vertices has invalid type {new_vertices}')
        if len(new_vertices.shape) != 2 or new_vertices.shape[1] != self.dim:
            raise InvalidMeshDimensionsException(
                actual=new_vertices.shape, expected=("N", self.dim), name="new_vertices")
        self._vertices = np.vstack([self._vertices, new_vertices])

    def remove_vertices(self, indices: Union[np.ndarray, List[int]]) -> None:
        """Remove vertices at the given indices and update references.

        Parameters
        ----------
        indices : Union[np.ndarray, List[int]]
            Indices of the vertices to remove.  Negative indexing is not
            supported.

        Raises
        ------
        MeshIndexException
            If any index is out of range.
        """
        if any(len(self._vertices) <= idx or idx < 0 for idx in indices):
            raise MeshIndexException('Vertex index out of range')
        # use indices to update self._faces
        faces_to_remove = fix_references(self._faces, indices)
        # remove vertices at all the indices
        self._vertices = np.delete(self._vertices, indices, axis=0)
        # remove faces and possibly parts
        fix_references(self._parts, faces_to_remove)
        # edges may be changed # Fixme: update only partly
        self._edges = self.extract_edges()

    def update_vertex(self, idx: int, new_vert: Vertex) -> None:
        """Update the coordinates of a single vertex.

        Parameters
        ----------
        idx : int
            Index of the vertex to update.  Negative indexing is not supported.
        new_vert : Vertex
            New coordinates for the vertex.

        Raises
        ------
        MeshIndexException
            If *idx* is out of range.
        InvalidTypeException
            If *new_vert* has an unexpected shape.
        InvalidMeshException
            If the coordinate dimension does not match the mesh.
        """
        if len(self._vertices) <= idx or idx < 0:
            raise MeshIndexException(f'Vertex index {idx} out of range for vertices of length {len(self._vertices)}')
        if isinstance(new_vert, np.ndarray) and len(new_vert.shape) != 1:
            raise InvalidTypeException(f'Vertex {new_vert} has incorrect shape, expected 1D-like array.')
        if self._vertices.shape[1] != len(new_vert):
            raise InvalidMeshException(f'Current indices have dimension {self._vertices.shape[1]}, while '
                                       f'new vertex has dimension {len(new_vert)} .')
        try:
            self._vertices[idx] = np.array(new_vert)
        except (TypeError, ValueError) as e:
            raise InvalidMeshException("Could not update Vertex. Dimensional mismatch for vertices."
                                       "All vertices should have the same number of dimensions.") from e

    @dangling_face_decorator()
    def add_faces(self, new_faces: Faces) -> None:
        """Append new faces to the mesh.

        Parameters
        ----------
        new_faces : Faces
            Faces to add.  Each face is an iterable of vertex indices.

        Raises
        ------
        InvalidMeshException
            If *new_faces* is not a twice-nested iterable or contains
            out-of-range vertex indices.
        InvalidTypeException
            If *new_faces* has an unsupported type.
        """
        # type-check whole array
        if not is_twice_nested_iterable(new_faces):
            raise InvalidMeshException("new_faces should be twice nested iterable.")
        # check for out of bound indices
        for new_face in new_faces:
            if any(v < 0 or v >= len(self._vertices) for v in new_face):
                raise MeshIndexException('Vertex index not defined')
        # add to self._faces depending on type
        if isinstance(new_faces, list):
            self._faces += new_faces
        elif isinstance(new_faces, (np.ndarray, tuple)):
            for val in new_faces:
                self._faces.append(val)
        else:
            raise InvalidTypeException(f'unknown type for new_face {type(new_faces)}')
        # edges may be changed # Fixme: update only partly
        self._edges = self.extract_edges()

    @dangling_vert_decorator()
    @dangling_face_decorator()
    def remove_faces(self, indices: Union[np.ndarray, List[int]]) -> None:
        """Remove faces at the given indices and update parts.

        Parameters
        ----------
        indices : Union[np.ndarray, List[int]]
            Indices of the faces to remove.  Negative indexing is not
            supported.

        Raises
        ------
        MeshIndexException
            If any index is out of range.
        """
        if any(len(self._faces) <= idx or idx < 0 for idx in indices):
            raise MeshIndexException('Face index out of range')

        # use indices to update self._parts
        fix_references(self._parts, indices)
        # remove faces at all the indices
        for index in sorted(indices, reverse=True):
            del self._faces[index]
        # edges may be changed # Fixme: update only partly
        self._edges = self.extract_edges()

    @dangling_vert_decorator()
    def update_face(self, idx: int, new_face: Face) -> None:
        """Update the vertices of a single face.

        Parameters
        ----------
        idx : int
            Index of the face to update.  Negative indexing is not supported.
        new_face : Face
            New vertex indices for the face.

        Raises
        ------
        MeshIndexException
            If *idx* or any vertex index in *new_face* is out of range.
        InvalidTypeException
            If *new_face* has an unexpected shape.
        """
        if len(self._faces) <= idx or idx < 0:
            raise MeshIndexException(f'Face index {idx} out of range.')
        if isinstance(new_face, np.ndarray) and len(new_face.shape) != 1:
            raise InvalidTypeException(f'Face {new_face} has incorrect shape, expected 1D-like array.')
        if any(0 > v_idx or v_idx >= len(self._vertices) for v_idx in new_face):
            raise MeshIndexException('Vertex index out of range.')
        # update face
        self._faces[idx] = np.array(new_face)
        # edges may be changed # Fixme: update only partly
        self._edges = self.extract_edges()

    @dangling_face_decorator()
    def add_parts(self, new_parts: Parts) -> None:
        """Append new parts to the mesh.

        Parameters
        ----------
        new_parts : Parts
            Parts to add.  Each part is an iterable of face indices.

        Raises
        ------
        InvalidMeshException
            If *new_parts* is not a twice-nested iterable or contains
            out-of-range face indices.
        InvalidTypeException
            If *new_parts* has an unsupported type.
        """
        # validate array type
        if not is_twice_nested_iterable(new_parts, min_lens=(1, 1)):
            raise InvalidMeshException('new_parts is not a valid nested iterable')
        # validate face indices
        for new_part in new_parts:
            if any(0 > f or f >= len(self._faces) for f in new_part):
                raise MeshIndexException(f'Face index out of range for new part: {new_part}')
        # add new to existing based on type
        if isinstance(new_parts, list):
            self._parts += [np.array(part) for part in new_parts]
        elif isinstance(new_parts, (np.ndarray, tuple)):
            for val in new_parts:
                self._parts.append(np.array(val))
        else:
            raise InvalidTypeException(f'unknown type for new_part {type(new_parts)}')

    @dangling_face_decorator()
    def remove_parts(self, indices: Union[np.ndarray, List[int]]) -> None:
        """Remove parts at the given indices.

        Parameters
        ----------
        indices : Union[np.ndarray, List[int]]
            Indices of the parts to remove.  Negative indexing is not
            supported.

        Raises
        ------
        MeshIndexException
            If any index is out of range.
        """
        if any(len(self._parts) <= idx or idx < 0 for idx in indices):
            raise MeshIndexException('Part index out of range')
        # remove indices back to front
        indices[:] = list(set(indices))
        indices.sort(reverse=True)
        for idx in indices:
            del self._parts[idx]

    @dangling_face_decorator()
    def update_part(self, idx: int, new_part: Part) -> None:
        """Update the faces of a single part.

        Parameters
        ----------
        idx : int
            Index of the part to update.  Negative indexing is not supported.
        new_part : Part
            New face indices for the part.

        Raises
        ------
        MeshIndexException
            If *idx* or any face index in *new_part* is out of range.
        InvalidTypeException
            If *new_part* has an unexpected shape.
        """
        if len(self._parts) <= idx or idx < 0:
            raise MeshIndexException(f'Part index {idx} out of range.')
        if isinstance(new_part, np.ndarray) and len(new_part.shape) != 1:
            raise InvalidTypeException(f'Part {new_part} has incorrect shape, expected 1D-like array.')
        if any(0 > f_idx or f_idx >= len(self._faces) for f_idx in new_part):
            raise MeshIndexException('Face index out of range.')
        # update part
        self._parts[idx] = np.array(new_part)

    @dangling_vert_decorator()
    @dangling_face_decorator()
    def add_to_mesh(self, other: 'Mesh') -> None:
        """Merge another mesh into this one by shifting its indices.

        The vertices, faces and parts of *other* are appended with
        shifted indices so that references remain consistent.  Use
        negative indices to reference the original mesh from the
        appended one (e.g. ``-1`` refers to the last old vertex).

        Parameters
        ----------
        other : Mesh
            Another mesh to merge into this one.

        Raises
        ------
        InvalidMeshException
            If the meshes have different vertex dimensionalities or
            the shifted indices would be out of range.
        """
        # Mesh has to be a correct mesh therefore many checks can be omitted
        # check if vertices have the same dimension
        if self._vertices.shape[1] != other.vertices.shape[1]:
            raise InvalidMeshException("Can not concatenate meshes with vertices of different dimensionality.")

        # save shift factor
        pre_nof_vertices = len(self.vertices)
        pre_nof_faces = len(self.faces)

        # add vertices
        self.add_vertices(other.vertices)
        # shift faces indices by the amount of vertices of the current mesh, check them and finally append them
        shifted_faces = [face + pre_nof_vertices for face in other.faces]
        if any(min(sf) < 0 or max(sf) >= len(self._vertices) for sf in shifted_faces):
            raise MeshIndexException("A face index is out of bounds.")
        self._faces += shifted_faces
        # shift parts indices by the amount of faces of the current mesh and append them
        shifted_parts = [part + pre_nof_faces for part in other.parts]
        if any(min(sp) < 0 or max(sp) >= len(self._faces) for sp in shifted_parts):
            raise MeshIndexException("A part index is out of bounds.")
        self._parts += shifted_parts

        # edges may be changed # Fixme: update only partly
        self._edges = self.extract_edges()

    def split_mesh_into_objects(self) -> List['Mesh']:
        """
        given a mesh, return a list of independent meshes that are not interconnected
        returns list of meshes with updated indices and references, does not change current mesh
        """

        def get_references_from_ids(ids: Set[int], nested: VarArray) -> Set[int]:
            """Return the indices of entries in *nested* that reference any of *ids*.

            Parameters
            ----------
            ids : set of int
                Set of identifiers to look up.
            nested : VarArray
                Nested array of references (e.g. faces referencing vertices).

            Returns
            -------
            set of int
                Indices of entries that contain at least one reference to *ids*.
            """
            return {i for i, nest in enumerate(nested) if any(_id in nest for _id in ids)}

        def get_ids_from_references(ids: Set[int], referenced: VarArray) -> Set[int]:
            """Return the union of all references made by *ids* inside *referenced*.

            Parameters
            ----------
            ids : set of int
                Indices into *referenced*.
            referenced : VarArray
                Array of reference lists.

            Returns
            -------
            set of int
                The aggregated set of all referenced identifiers.
            """
            if len(ids) > 0:
                return set(np.unique(np.stack([referenced[_id] for _id in ids])))
            return set()

        new_meshes: List['Mesh'] = []
        analyzed_verts: Set[int] = set()
        while any(vert not in analyzed_verts for vert in range(len(self._vertices))):
            # get first value not in analyzed or 0
            obj_vert_ids: Set[int] = {next((i for i in range(len(self._vertices)) if i not in analyzed_verts), 0)}
            prev_iter: Set[int] = set()
            face_ids: Set[int] = set()
            part_ids: Set[int] = set()
            while prev_iter != obj_vert_ids:
                # update prev to stop when no new points were added
                prev_iter = obj_vert_ids.copy()
                # find all the references to all known vertices
                face_ids = get_references_from_ids(obj_vert_ids, self._faces)
                part_ids = get_references_from_ids(face_ids, self._parts)
                # generate all the faces and vertices from all the parts found including all the old ones
                face_ids.update(get_ids_from_references(part_ids, self._parts))
                # update all the vertices of the current object
                obj_vert_ids.update(get_ids_from_references(face_ids, self._faces))
            # create new mesh object and save it to new_meshes
            # make sure to update all the references to zero indexed lists
            new_ids: List[int] = sorted(list(int(_id) for _id in obj_vert_ids))
            new_faces: List[int] = sorted(list(face_ids))
            new_meshes.append(Mesh(
                vertices=np.vstack([self._vertices[_id] for _id in new_ids]),
                faces=[np.array([new_ids.index(old_vertex_id) for old_vertex_id in self._faces[f_id]])
                       for f_id in face_ids],
                parts=[np.array([new_faces.index(old_face_id) for old_face_id in self._parts[p_id]])
                       for p_id in part_ids],
            ))
            # update analyzed vertices
            analyzed_verts.update(obj_vert_ids)
        return new_meshes

    def dangling_vert_check(self) -> bool:
        """check whether there are any dangling nodes - vertices that are not part of a face"""
        if len(self._faces) == 0:
            return len(self._vertices) != 0
        unique = np.unique(np.concatenate(self._faces).ravel())
        return any(v_idx not in unique for v_idx in range(len(self._vertices)))

    def dangling_face_check(self) -> bool:
        """check whether there are any dangling faces - faces that are not part of a part"""
        if len(self._parts) == 0:
            return len(self._faces) != 0
        if len(self._parts) > 0 and len(self._faces) == 0:
            return False
        unique = np.unique(np.concatenate(self._parts).ravel())
        return any(f_idx not in unique for f_idx in range(len(self._faces)))

    def scale_mesh(self, scaling: float, about_point=None) -> None:
        """Scale all vertices by a uniform factor.

        Parameters
        ----------
        scaling : float
            Scale factor applied to every vertex.
        about_point : numpy.ndarray or None, optional
            If given, the scaling is performed around this point.
        """
        if about_point is not None:
            self._vertices -= about_point
            self._vertices *= float(scaling)
            self._vertices += about_point
        else:
            self._vertices *= float(scaling)

    def stretch_mesh(self, factor: float, dim: int, about_point=None) -> None:
        """Stretch all vertices along a single dimension.

        Parameters
        ----------
        factor : float
            Stretch factor.
        dim : int
            Index of the dimension to stretch.
        about_point : numpy.ndarray or None, optional
            If given, the stretch is performed around this point.
        """
        if about_point is not None:
            self._vertices -= about_point
            self._vertices[:,dim] *= float(factor)
            self._vertices += about_point
        else:
            self._vertices[:,dim] *= float(factor)

    def translate_mesh(self, translation: np.ndarray) -> None:
        """Translate (shift) all vertices by the given vector.

        Parameters
        ----------
        translation : np.ndarray
            Translation vector.  Its length must equal the mesh
            dimension.

        Raises
        ------
        InvalidTypeException
            If *translation* is not a :class:`numpy.ndarray`.
        InvalidMeshDimensionsException
            If the length of *translation* does not match the mesh dimension.
        """
        if not isinstance(translation, np.ndarray):
            raise InvalidTypeException(f'Translation should be a np.ndarray, but was a {type(translation)} instead')
        if len(translation.shape) != 1 or translation.shape[0] != self.dim:
            raise InvalidMeshDimensionsException(name="Translation", expected=self.dim, actual=translation.shape)
        self._vertices += np.array(translation)

    def translate_vertex(self, v_id: int, translation: np.ndarray) -> None:
        """Translate a single vertex by the given vector.

        Parameters
        ----------
        v_id : int
            Index of the vertex to translate.
        translation : np.ndarray
            Translation vector.  Its length must equal the mesh
            dimension.

        Raises
        ------
        MeshIndexException
            If *v_id* is out of range.
        InvalidTypeException
            If *translation* is not a :class:`numpy.ndarray`.
        InvalidMeshDimensionsException
            If the length of *translation* does not match the mesh dimension.
        """
        if 0 > v_id or v_id >= len(self._vertices):
            raise MeshIndexException(f'Index {v_id} out of bounds for vertices of shape {self._vertices.shape}')
        if not isinstance(translation, np.ndarray):
            raise InvalidTypeException(f'Translation should be a np.ndarray, but was a {type(translation)} instead')
        if len(translation.shape) != 1 or translation.shape[0] != self.dim:
            raise InvalidMeshDimensionsException(name="Translation", expected=self.dim, actual=translation.shape)
        self._vertices[v_id] += translation

    def apply_rotation(self, angle: float, axis: np.ndarray = np.array([0, 0, 1]), about_point=None) -> None:
        """Rotate all vertices around a given axis.

        Only 2D and 3D rotations are supported.  For 2D meshes the
        rotation is performed around the implicit z-axis; for 3D meshes
        the rotation is performed around *axis*.

        Parameters
        ----------
        angle : float
            Rotation angle in radians.
        axis : np.ndarray, optional
            Rotation axis (only used for 3D).  Defaults to the z-axis.
        about_point : np.ndarray or None, optional
            If given, the rotation is performed around this point.

        Raises
        ------
        NotImplementedError
            If the mesh dimension is not 2 or 3.
        """

        def rotation_matrix(
                angle: float,
                axis: np.ndarray,
        ) -> np.ndarray:
            """Compute a 3D rotation matrix for *angle* radians around *axis*.

            Parameters
            ----------
            angle : float
                Rotation angle in radians.
            axis : np.ndarray
                Rotation axis (will be normalised internally).

            Returns
            -------
            np.ndarray
                A 3×3 rotation matrix.
            """
            rot_mat = Rotation.from_rotvec(
                angle * np.array(axis)/np.linalg.norm(np.array(axis))
            ).as_matrix()
            return rot_mat

        # define basic rotation matrix
        rot_2d = np.array([[np.cos(angle), -np.sin(angle)],
                           [np.sin(angle), np.cos(angle)]])

        if about_point is not None:
            self._vertices -= about_point

        if self.dim == 2:
            self._vertices = self._vertices @ rot_2d.T  # transposed because we got row vectors not col vecs
        elif self.dim == 3:  # 3d uses the 2D matrix in different columns
            rot_matrix = rotation_matrix(angle, axis)
            self._vertices = np.dot(self._vertices, rot_matrix.T)  # transposed because we got row vectors not col vecs
        else:
            raise NotImplementedError("No implementation for n-Dimensional vector rotation")

        if about_point is not None:
            self._vertices += about_point

    def snap_to_grid(
            self, grid_sizes: Tuple[float, ...], threshold: Tuple[float, ...], steps: int = 1,
            update_verts: bool = False, precision: int = 10
    ) -> np.ndarray:
        """Snap vertices to grid positions when they are sufficiently close.

        For example, a value of ``0.999`` or ``1.001`` would be shifted
        towards ``1.000`` when the grid size is ``1``, while ``0.699``
        would *not* be shifted to ``0.700`` unless the grid size changes.
        To snap only one dimension, set the threshold to ``0`` on all
        other axes.

        Parameters
        ----------
        grid_sizes : tuple of float
            Grid resolution in every axis direction (length must equal
            :attr:`dim`).
        threshold : tuple of float
            Maximum allowed movement per axis to snap into the next grid
            position (length must equal :attr:`dim`).
        steps : int, optional
            Number of intermediate steps to the grid position (useful for
            animations).  Must be positive.
        update_verts : bool, optional
            If ``True``, :attr:`_vertices` is updated in-place and
            duplicates are removed.
        precision : int, optional
            Decimal places used for rounding the result (default ``10``).

        Returns
        -------
        np.ndarray
            New vertex positions after snapping.

        Raises
        ------
        InvalidMeshDimensionsException
            If the lengths of *grid_sizes* or *threshold* do not match
            the mesh dimension.
        InvalidRequestException
            If *grid_sizes* contains non-positive values, any threshold
            is ≥ half the corresponding grid size, all thresholds are zero,
            or *steps* is not positive.
        """
        if len(grid_sizes) != self.dim:
            raise InvalidMeshDimensionsException(name="Grid sizes", actual=len(grid_sizes), expected=self.dim)
        if len(threshold) != self.dim:
            raise InvalidMeshDimensionsException(name="Threshold", actual=len(threshold), expected=self.dim)
        if any(v <= 0 for v in grid_sizes):
            raise InvalidRequestException("invalid value for grid_sizes. Has to be greater than zero.")
        if any(2 * threshold[i] >= grid_sizes[i] for i in range(self.dim)):
            raise InvalidRequestException("threshold can not be bigger than half of grid_size for same dimension.")
        if all(t == 0 for t in threshold):
            raise InvalidRequestException("one value in threshold has to be != 0")
        if steps <= 0:
            raise InvalidRequestException(f'steps has to be a positive integer, but was {steps}')
        vertices = np.zeros_like(self._vertices)
        # look at every dimension separately
        for d in range(self.dim):
            curr_vals = self._vertices[:, d]
            mod = curr_vals % grid_sizes[d]
            # set everything that is less than threshold to the difference to the next step
            differences = np.where((mod > 0) & (mod <= threshold[d]), -mod, mod)
            # set everything that is close to the next step to the (positive) missing difference to the next step
            differences = np.where(
                (differences > 0) & (differences >= grid_sizes[d] - threshold[d]),
                grid_sizes[d] - differences,
                differences
            )
            # set everything that is bigger than Threshold to zero
            differences = np.where(differences > threshold[d], 0, differences)
            # add differences to vertices to snap every modified value
            # possibility to move stepwise for later animation
            vertices[:, d] = self._vertices[:, d] + (differences / steps)
        # round the result to reduce floating point precision errors
        vertices.round(decimals=precision)
        if update_verts:
            self._vertices = vertices
            self.remove_duplicates()
        return vertices

    def remove_duplicate_vertices(self, precision: int = 10) -> None:
        """Remove duplicate vertices and update all face references.

        Parameters
        ----------
        precision : int, optional
            Decimal places used when comparing vertices (default ``10``,
            i.e. equality up to ``1e-10``).
        """
        old_vertices = deepcopy(self._vertices)
        # get unique vertices, indices, and the inverse references
        unique_verts, indices = np.unique(np.around(self._vertices, decimals=precision), axis=0, return_index=True)
        # sort indices, to keep current sorting for faces, then set unique vertices
        permutation = indices.argsort()
        self._vertices = unique_verts[permutation]
        # switch index of every face that contains a value that is duplicate
        for old_idx, old_vert in enumerate(old_vertices):
            # skip if index of vertex in current list is the same as the old one
            new_idx = np.argwhere(np.all(np.abs(self._vertices - old_vert) <= pow(0.1, precision), axis=1))[0, 0]
            if new_idx != old_idx:
                for f_i, face in enumerate(self._faces):
                    np.place(self._faces[f_i], face == old_idx, new_idx)
        # current faces are fixed now
        # edges may be changed # Fixme: update only partly
        self._edges = self.extract_edges()

    def remove_duplicate_faces(self) -> None:
        """Remove duplicate faces and update part references.

        Faces are considered equal when their vertex indices match
        up to a cyclic permutation (rolling order), not necessarily
        at the exact same positions.
        """
        to_delete = []
        for i_face, face in enumerate(self._faces):
            if i_face in to_delete:  # skip indices marked for deletion
                continue
            others = self.find_face(face, start=i_face + 1)
            to_delete += others
            for o_f_idx in others:
                # change parts to use first index of the same face
                for part in self._parts:
                    np.place(part, part == o_f_idx, i_face)
        # delete all duplicates from faces
        for del_f_idx in sorted(list(set(to_delete)), reverse=True):
            del self._faces[del_f_idx]
        # edges may be changed # Fixme: update only partly
        self._edges = self.extract_edges()

    def remove_duplicate_parts(self) -> None:
        """Remove duplicate parts from the mesh.

        Parts are considered equal when their face indices match
        up to a cyclic permutation (rolling order), not necessarily
        at the exact same positions.
        """
        to_delete = []
        for i_part, part in enumerate(self._parts):
            if i_part in to_delete:  # skip indices marked for deletion
                continue
            others = self.find_part(part, start=i_part + 1)
            to_delete += others
            # no further nested type
        for del_p_idx in sorted(list(set(to_delete)), reverse=True):
            # exact duplicates can be removed
            del self._parts[del_p_idx]

    def remove_duplicates(self, precision: int = 10) -> None:
        """Remove all duplicate vertices, faces and parts.

        Parameters
        ----------
        precision : int, optional
            Decimal places passed to :meth:`remove_duplicate_vertices`
            (default ``10``).
        """
        self.remove_duplicate_vertices(precision=precision)
        self.remove_duplicate_faces()
        self.remove_duplicate_parts()

    def extract_edges(self) -> Edges:
        """returns all edges of the mesh as List of sorted 2-tuples of vertex indices, e.g. [(1,2), (2,3)]"""
        # TODO: possibility to update edges only partly (e.g. by index)
        # TODO: possibly create a separate edge class to remove overhead from mesh
        edges: Edges = []
        for face in self._faces:
            last_vertex = face[-1]
            for _, vertex_idx in enumerate(face):
                # Fixme: sorted edge for "if edge in edges", but removes possibility to iterate around face
                edge: Edge = (min(last_vertex, vertex_idx), max(last_vertex, vertex_idx))
                # edge: Edge = tuple(sorted([int(last_vertex), int(vertex_idx)]))
                last_vertex = vertex_idx
                if edge not in edges:
                    edges.append(edge)
        return sorted(edges)
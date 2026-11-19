# SPDX-FileCopyrightText: 2022 bmmtstb, 99Vicky
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Faster meshes (WORK IN PROGRESS) by using OpenGL more efficiently."""

from manim.mobject.opengl.opengl_mobject import OpenGLMobject

# Implementation in progress
# patched: lazy-import moderngl (meshes extra)
# pylint: skip-file
# pylint: disable-all

import numpy as np

from ...helpers import remove_keys_from_dict
from ..data_models.mesh import Mesh
from ...params import get_param_or_default
from manim.typing import VectorND


class FastManimMesh(OpenGLMobject):
    """More efficient mesh implementation.
    Uses custom shaders and stores vertices and faces in a single VAO.
    Useful for rendering meshes with many vertices / faces. The underlying
    :class:`~manim_extensions.meshes.models.data_models.mesh.Mesh` can be
    updated through
    :meth:`~manim_extensions.meshes.models.manim_models.opengl_mesh.FastManimMesh.set_mesh`,
    :meth:`~manim_extensions.meshes.models.manim_models.opengl_mesh.FastManimMesh.add_face`,
    :meth:`~manim_extensions.meshes.models.manim_models.opengl_mesh.FastManimMesh.remove_face`
    and
    :meth:`~manim_extensions.meshes.models.manim_models.opengl_mesh.FastManimMesh.update_vertex`;
    every update rebuilds the shader arrays.

    .. warning::

       Requires manipulating the manim lib:
       copy the directory ``mesh`` (under ``manim_extensions/meshes/shaders/``)
       to ``manim/renderer/shaders/``.

    .. hint::

       The mesh must only consist of triangles.

    Parameters
    ----------
    mesh
        The mesh data model. Must consist only of triangles.
    shader_folder
        Path to the shader folder. (uses ``"mesh"``).
    **kwargs
        Additional keyword arguments forwarded to OpenGLMobject.
    """

    shader_dtype = [
        ("point", np.float32, (3,)),
        ("color", np.float32, (4,)),
    ]
    shader_folder = "mesh"

    def __init__(
        self,
        mesh: Mesh,
        shader_folder: str | None = None,
        **kwargs,
    ):
        # imported here because OGLM requires the optional moderngl dependency
        from ...params import OGLM

        self._validate_mesh(mesh)
        self.mesh = mesh
        self.triangle_indices = self._flatten_triangles(mesh)
        super().__init__(
            shader_folder=shader_folder if shader_folder is not None else "mesh",
            # default params
            **{key: get_param_or_default(key, kwargs, OGLM) for key in OGLM},
            # regular kwargs
            **remove_keys_from_dict(kwargs, list(OGLM.keys())),
        )

    @staticmethod
    def _validate_mesh(mesh: Mesh) -> None:
        """Raise when the mesh is not composed exclusively of triangles.

        Parameters
        ----------
        mesh
            Mesh to validate.

        Raises
        ------
        ValueError
            If any face does not have exactly three vertices.
        """
        if any(len(face) != 3 for face in mesh.faces):
            raise ValueError("mesh must only consist of triangles!")

    @staticmethod
    def _flatten_triangles(mesh: Mesh) -> VectorND:
        """Return the flat triangle index array for the shader.

        Parameters
        ----------
        mesh
            Triangle mesh whose faces are concatenated.

        Returns
        -------
            A one-dimensional array of vertex indices, empty for no faces.
        """
        return np.hstack(mesh.faces) if mesh.faces else np.array([], dtype=int)

    def init_points(self):
        """Set the mesh vertices as the mobject's points."""
        self.set_points(self.mesh.vertices)

    def refresh_from_mesh(self) -> None:
        """Rebuild points and triangle indices after changing ``mesh`` in place."""
        self._validate_mesh(self.mesh)
        self.triangle_indices = self._flatten_triangles(self.mesh)
        self.init_points()

    def set_mesh(self, mesh: Mesh) -> None:
        """Replace the displayed mesh and rebuild the shader arrays.

        Parameters
        ----------
        mesh
            Triangle-only mesh to display.
        """
        self._validate_mesh(mesh)
        self.mesh = mesh
        self.refresh_from_mesh()

    def add_face(self, face: VectorND) -> None:
        """Append a triangular face and refresh the displayed geometry.

        Parameters
        ----------
        face
            Three vertex indices forming the new face.

        Raises
        ------
        ValueError
            If ``face`` does not contain exactly three indices.
        """
        face_array = np.asarray(face, dtype=int)
        if face_array.shape != (3,):
            raise ValueError("face must contain exactly three vertex indices")
        self.mesh.add_faces([face_array])
        self.refresh_from_mesh()

    def remove_face(self, idx: int) -> None:
        """Remove a triangular face by index and refresh the geometry.

        Parameters
        ----------
        idx
            Index of the face to remove.
        """
        self.mesh.remove_faces([idx])
        self.refresh_from_mesh()

    def update_vertex(self, idx: int, vertex: VectorND) -> None:
        """Update one vertex and refresh the displayed geometry.

        Parameters
        ----------
        idx
            Index of the vertex to update.
        vertex
            New vertex coordinates.
        """
        self.mesh.update_vertex(idx, vertex)
        self.init_points()

    def get_triangle_indices(self) -> VectorND:
        """Return the flat array of triangle indices.

        Returns
        -------
            Triangle vertex indices concatenated into a 1-D array.
        """
        return self.triangle_indices

    # For shaders
    def get_shader_data(self) -> np.ndarray:
        """Build the shader data array from the mobject's points and colours.

        Returns
        -------
            A structured array with the shader dtype.
        """
        shader_data = np.zeros(len(self.points), dtype=self.shader_dtype)
        if "points" not in self.locked_data_keys:
            shader_data["point"] = self.points
        self.fill_in_shader_color_info(shader_data)
        return shader_data

    def fill_in_shader_color_info(self, shader_data: np.ndarray) -> np.ndarray:
        """Write colour information into the shader data array.

        Parameters
        ----------
        shader_data
            The structured shader data array to modify.

        Returns
        -------
            The updated shader data array.
        """
        self.read_data_to_shader(shader_data, "color", "rgbas")
        return shader_data

    def get_shader_vert_indices(self) -> VectorND:
        """Return the triangle indices used for shader rendering.

        Returns
        -------
            The same array as :meth:`~manim_extensions.meshes.models.manim_models.opengl_mesh.FastManimMesh.get_triangle_indices`.
        """
        return self.get_triangle_indices()

# SPDX-FileCopyrightText: 2022 bmmtstb, 99Vicky
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
# patched: implement flip and 4-D transforms for the underlying data mesh

"""Manim models for mesh objects.

Contains a 3D and a 2D version. Additionally there is the mesh for only
triangles in triangle_mesh.py.
"""

# unlinked-class-ok: Array

from manim.mobject.opengl.opengl_compatibility import ConvertToOpenGL

# python imports
import copy
from typing import List

# third-party imports
from manim import (
    Dot,
    FadeIn,
    FadeOut,
    Group,
    ManimColor,
    Mobject,
    ORIGIN,
    OUT,
    RED,
    Scene,
    Sphere,
    TAU,
    ThreeDVMobject,
    UP,
    VGroup,
    ValueTracker,
)
import numpy as np

# local imports
from ...exceptions import (
    InvalidMeshDimensionsException,
    InvalidMeshException,
    InvalidShapeException,
)
from ...helpers import remove_keys_from_dict
from ..data_models.mesh import Mesh
from ...params import get_param_or_default, BM2DM, BM3DM
from ...types import Vertices
from manim.typing import Point3D, Point3D_Array, Vector3D, VectorND


# pylint: disable=too-many-instance-attributes
class ManimMesh(Group, metaclass=ConvertToOpenGL):
    """another :class:`~manim_extensions.meshes.models.data_models.mesh.Mesh` implementation, a bit faster + looks better.

    inspired by manim class
    :class:`~manim.mobject.three_d.three_dimensions.Surface`

    Parameters
    ----------
    mesh
        The mesh data model containing vertices, faces, and parts.
    args
        Positional arguments forwarded to the parent :class:`~manim.mobject.mobject.Group`.
    **kwargs
        Additional keyword arguments controlling display options.

        Possible keyword arguments (see :data:`~manim_extensions.meshes.params.BM3DM`):

        * ``display_vertices``: whether to display the vertices
        * ``display_edges``: whether to display the edges
        * ``display_faces``: whether to display the faces
        * ``clear_vertices``: whether to clear the vertices after WHAT?
        * ``clear_edges``: whether to clear the edges after WHAT?
        * ``clear_faces``: whether to clear the faces after WHAT?
        * ``edges_color``: color of the edges
        * ``edges_width``: width of the lines of the edges
        * ``faces_color``: color of the faces
        * ``faces_opacity``: opacity of the faces
        * ``verts_color``: color of the vertices.
        * ``pre_function_handle_to_anchor_scale_factor``: ?

    Examples
    --------
    .. manim:: ManimMeshExample

       import numpy as np
       from manim import *
       from manim_extensions.meshes.templates import create_pyramid
       from manim_extensions.meshes.models.manim_models.basic_mesh import ManimMesh

       class ManimMeshExample(ThreeDScene):
           def construct(self):
               self.set_camera_orientation(phi=70 * DEGREES, theta=30 * DEGREES)
               # pyramid built from triangles only
               tri_pyramid = ManimMesh(
                   create_pyramid(triangles_only=True), display_vertices=True
               )
               tri_pyramid.shift(OUT)
               # pyramid with a quadrilateral base, to test the renderer
               quad_pyramid = ManimMesh(
                   create_pyramid(triangles_only=False), display_vertices=True
               )
               quad_pyramid.shift(IN, IN)
               self.add(tri_pyramid, quad_pyramid)
               # color single faces
               self.play(
                   tri_pyramid.get_face(0).animate.set_fill(RED, 1),
                   quad_pyramid.get_face(4).animate.set_fill(GREEN, 1),
               )
               # move a vertex; all adjacent faces and edges are updated.
               tri_pyramid.move_vertex_to(
                   vertex_idx=0, scene=self, pos=np.array([2, 2, 1])
               )
               # rotate the whole mesh; mesh data and mobjects stay in sync
               self.play(Rotate(quad_pyramid, PI / 3, about_point=ORIGIN))
               self.wait()
    """

    # pylint:disable=abstract-method

    def __init__(self, mesh: Mesh, *args, **kwargs):
        self.mesh: Mesh = mesh
        self.vertices: Group = Group()
        self.edges: VGroup = VGroup()
        self.faces: VGroup = VGroup()

        # set all the parameters
        for param_name in BM3DM:
            self.__setattr__(
                param_name, get_param_or_default(param_name, kwargs, BM3DM)
            )

        super().__init__(*args, **remove_keys_from_dict(kwargs, list(BM3DM.keys())))

        self.setup()

    def setup(self):
        """create all the necessary manim objects for the renderer."""
        if self.display_faces:
            self.setup_faces()
        if self.display_edges:
            self.setup_edges()
        if self.display_vertices:
            self.setup_vertices()
        # add all the objects to the scene renderer
        self.add(self.faces, self.edges, self.vertices)

    def setup_vertices(self) -> Group:
        """Create Manim sphere mobjects for every vertex of the mesh.

        Returns
        -------
            Group containing the vertex sphere mobjects.
        """
        # clear previous work if wanted
        if self.clear_vertices:
            self.vertices = Group()
        # create and add all the points into self.vertices
        for v in self.mesh.get_3d_vertices():
            self.vertices.add(Sphere(v, radius=self.verts_size, color=self.verts_color))
        return self.vertices

    def setup_edges(self) -> VGroup:
        """Create Manim line mobjects for every edge of the mesh.

        Returns
        -------
            Vector group containing the edge mobjects.
        """
        # clear previous work if wanted
        if self.clear_edges:
            self.edges.clear_points()
        # create and add all the edges into self.edges
        vertices = self.mesh.get_3d_vertices()
        for edge_verts in self.mesh.edges:
            vert_1 = vertices[edge_verts[0]]
            vert_2 = vertices[edge_verts[1]]
            edge = ThreeDVMobject()
            edge.set_points_as_corners([vert_1, vert_2])
            self.edges.add(edge)
        # color, scale, ... all edges at once
        self.edges.set_fill(
            color=self.edges_color,
            opacity=1.0,
        )
        self.edges.set_stroke(
            color=self.edges_color,
            width=self.edges_width,
            opacity=1.0,
        )
        return self.edges

    def setup_faces(self) -> VGroup:
        """Create Manim surface mobjects for every face of the mesh.

        Works for faces of any size, not only triangles.

        Returns
        -------
            Vector group containing the face mobjects.
        """
        # clear previous work if wanted
        if self.clear_faces:
            self.faces.clear_points()
        # create and add all the faces into self.faces
        verts_3d = self.mesh.get_3d_vertices()
        for face_indices in self.mesh.faces:
            face_points = [verts_3d[i] for i in face_indices]
            # make sure to add the first point to have a closed loop
            face_points.append(verts_3d[face_indices[0]])
            new_face = ThreeDVMobject()
            new_face.set_points_as_corners(face_points)
            self.faces.add(new_face)
        # color, scale, ... all faces at once
        self.faces.set_fill(color=self.faces_color, opacity=self.faces_opacity)
        self.faces.set_stroke(
            color=self.faces_color,
            width=0.0,
            opacity=0.0,
        )
        return self.faces

    def add_face(
        self, face: VectorND, color: ManimColor | None = None
    ) -> tuple[VGroup, VGroup]:
        """Add a face to the mesh and create the corresponding Manim objects.

        If ``color`` is ``None``, the default ``self.faces_color`` is used.

        Parameters
        ----------
        face
            Array of vertex indices defining the face to add.
        color
            Optional colour for the new face.

        Returns
        -------
            The newly created face mobject and a list of newly created edge mobjects.
        """
        if color is None:
            color = self.faces_color
        old_edges = self.mesh.edges
        self.mesh.add_faces([face])
        verts_3d = self.mesh.get_3d_vertices()
        face_points = [verts_3d[i] for i in face]
        face_points.append(verts_3d[face[0]])
        new_face = ThreeDVMobject()
        new_face.set_points_as_corners(face_points)
        new_face.set_fill(color=color, opacity=self.faces_opacity)
        new_face.set_stroke(
            color=color,
            width=0.0,
            opacity=0.0,
        )
        self.faces.add(new_face)
        # update edges
        new_edges = []
        if self.display_edges:
            vertices = self.mesh.get_3d_vertices()
            for edge_verts in sorted(set(self.mesh.edges).difference(set(old_edges))):
                vert_1 = vertices[edge_verts[0]]
                vert_2 = vertices[edge_verts[1]]
                edge = ThreeDVMobject()
                edge.set_points_as_corners([vert_1, vert_2])
                edge.set_fill(
                    color=self.edges_color,
                    opacity=1.0,
                )
                edge.set_stroke(
                    color=self.edges_color,
                    width=self.edges_width,
                    opacity=1.0,
                )
                self.edges.insert(self.mesh.get_edge_index(edge_verts), edge)
                new_edges.append(edge)

        return new_face, new_edges

    def remove_face(self, face_idx: int) -> tuple:
        """Remove a face (and its orphaned edges) by index.

        Parameters
        ----------
        face_idx
            Index of the face to remove.

        Returns
        -------
            The removed face mobject and a list of removed edge mobjects.
        """
        old_edges = self.mesh.edges
        self.mesh.remove_faces([face_idx])
        removed_face = self.faces.submobjects[face_idx]
        self.faces.remove(removed_face)
        removed_edges = []
        if self.display_edges:
            del_indices = [
                old_edges.index(edge)
                for edge in set(old_edges).difference(set(self.mesh.edges))
            ]
            for index in sorted(del_indices, reverse=True):
                removed_edge = self.edges.submobjects[index]
                removed_edges.append(removed_edge)
                self.edges.remove(removed_edge)
        return removed_face, removed_edges

    def get_vertex(self, vertex_idx: int) -> Mobject:
        """Return the Manim mobject for the vertex at ``vertex_idx``.

        Parameters
        ----------
        vertex_idx
            Index of the vertex to retrieve.

        Returns
        -------
            The vertex mobject (e.g. :class:`~manim.mobject.three_d.three_dimensions.Sphere` or :class:`~manim.mobject.geometry.arc.Dot`).
        """
        return self.vertices.submobjects[vertex_idx]

    def get_face(self, face_idx: int) -> Mobject:
        """Return the Manim mobject for the face at ``face_idx``.

        Parameters
        ----------
        face_idx
            Index of the face to retrieve.

        Returns
        -------
            The face mobject (a :class:`~manim.mobject.three_d.three_dimensions.ThreeDVMobject`).
        """
        return self.faces.submobjects[face_idx]

    def get_edge(self, edge_idx: int) -> Mobject:
        """Return the Manim mobject for the edge at ``edge_idx``.

        Parameters
        ----------
        edge_idx
            Index of the edge to retrieve.

        Returns
        -------
            The edge mobject (a :class:`~manim.mobject.three_d.three_dimensions.ThreeDVMobject`).
        """
        return self.edges.submobjects[edge_idx]

    def add_vertices(self, new_vertices: Vertices, scene: Scene):
        """fade in some additional vertices.

        Parameters
        ----------
        new_vertices
            New vertices processed by this operation.
        scene
            The scene in which the action is performed.
        """
        self.mesh.add_vertices(new_vertices)
        # fade out current ones, fade in all after add
        if self.display_vertices:
            scene.play(FadeOut(self.vertices), FadeIn(self.setup_vertices()))

    def _update_vertex(self, vertex_idx: int, pos: Point3D):
        """Change the position of a vertex and update all dependent mobjects.

        If vertices are displayed the corresponding vertex object is moved.
        If faces are displayed every face sharing this vertex is re-rendered.
        If edges are displayed every edge touching this vertex is re-rendered.

        Parameters
        ----------
        vertex_idx
            Index of the vertex to update.
        pos
            New position for the vertex (2-D or 3-D coordinates).
        """
        # update mesh
        self.mesh.update_vertex(vertex_idx, pos)
        if self.display_vertices:
            # update vertex
            vertex = self.get_vertex(vertex_idx)
            vertex.move_to(np.pad(pos, (0, 3 - len(pos))))
        if self.display_faces:
            # update faces
            for face_idx, face in enumerate(self.mesh.faces):
                if vertex_idx in face:
                    mesh_vertices = [self.mesh.get_3d_vertices()[i] for i in face]
                    mesh_vertices.append(mesh_vertices[0])
                    drawn_face = self.get_face(face_idx)
                    drawn_face.set_points_as_corners(mesh_vertices)
        if self.display_edges:
            # update edges
            for edge in self.mesh.get_vertex_edges(vertex_idx):
                self._update_edge(edge)

    def _update_edge(self, edge: tuple[int, int]):
        """Update the Manim object of ``edge`` to reflect the latest vertex positions.

        Parameters
        ----------
        edge
            A pair of vertex indices defining the edge to update.
        """
        e = self.get_edge(self.mesh.get_edge_index(edge))
        vert_1 = self.mesh.get_3d_vertices()[edge[0]]
        vert_2 = self.mesh.get_3d_vertices()[edge[1]]
        e.set_points_as_corners([vert_1, vert_2])

    def _as_mesh_dim(self, point: object) -> np.ndarray:
        """Expand a point to the mesh dimensionality, padding extra axes with zero.

        Parameters
        ----------
        point
            Coordinates in two, three or four dimensions.

        Returns
        -------
            Coordinates whose length equals ``mesh.dim``.
        """
        array = np.asarray(point, dtype=float)
        if array.shape[0] < self.mesh.dim:
            array = np.pad(array, (0, self.mesh.dim - array.shape[0]))
        return array[: self.mesh.dim]

    def _mesh_center(self) -> np.ndarray:
        """Return the bounding-box centre expanded to the mesh dimensionality.

        Returns
        -------
            Centre coordinates whose length equals ``mesh.dim``.
        """
        return self._as_mesh_dim(self.get_critical_point(ORIGIN))

    def _rebuild_objects(self) -> None:
        """Rebuild the vertex, edge and face mobjects from the mesh data."""
        self.remove(self.faces, self.edges, self.vertices)
        self.faces = VGroup()
        self.edges = VGroup()
        self.vertices = Group()
        self.setup()

    def shift(self, *vectors: Vector3D):
        """Shift the mesh and its underlying data by the sum of ``vectors``.

        Multiple vectors of the same dimensionality are summed to produce
        the final translation.

        Parameters
        ----------
        vectors
            One or more displacement vectors to apply.
        """
        total_shift = np.sum(vectors, axis=0)
        # update vertices of self.mesh
        self.mesh.translate_mesh(self._as_mesh_dim(total_shift))
        # shift manim vertices, edges and faces
        super().shift(total_shift)

    def scale(self, scale_factor: float, **kwargs):
        """Scale the mesh (data and Manim objects) about its bounding-box centre.

        Parameters
        ----------
        scale_factor
            The uniform scale factor to apply.
        **kwargs
            Forwarded to the parent :meth:`~manim.mobject.mobject.Mobject.scale`.
        """
        about_point = self._mesh_center()
        self.mesh.scale_mesh(scale_factor, about_point)
        super().scale(scale_factor, **kwargs)

    def stretch(self, factor: float, dim: int, **kwargs):
        """Stretch the mesh along a single dimension.

        Parameters
        ----------
        factor
            Stretch factor (e.g. ``2.0`` doubles the size along ``dim``).
        dim
            The axis index to stretch (0 = x, 1 = y, 2 = z).
        **kwargs
            Forwarded to the parent Mobject.stretch.

        Raises
        ------
        LookupError
            If ``dim`` is greater than or equal to ``self.mesh.dim``.
        """
        if dim >= self.mesh.dim:
            raise LookupError("dim must lower than ManimMesh.mesh.dim!")
        about_point = self._mesh_center()
        self.mesh.stretch_mesh(factor, dim, about_point)
        super().stretch(factor, dim, **kwargs)

    def rotate(
        self,
        angle: float,
        axis: Vector3D = OUT,
        about_point: Point3D | None = None,
        **kwargs,
    ):
        """Rotate the mesh (data and Manim objects) about ``about_point``.

        For 2-D meshes the rotation is always about the z-axis; for 3-D
        meshes an arbitrary ``axis`` can be specified.

        Parameters
        ----------
        angle
            Rotation angle in radians.
        axis
            Axis vector for the rotation.
        about_point
            Pivot point for the rotation.
        **kwargs
            Forwarded to the parent :meth:`~manim.mobject.mobject.Mobject.rotate`.
        """
        if self.mesh.dim == 4:
            if np.asarray(axis, dtype=float).shape == (2, 4):
                center = (
                    self._mesh_center()
                    if about_point is None
                    else self._as_mesh_dim(about_point)
                )
                self.mesh.apply_rotation(angle, axis, center)
                self._rebuild_objects()
                return
            # a 3-D axis cannot express a 4-D rotation: rotate the projection only
            if about_point is None:
                about_point = self.get_critical_point(ORIGIN)
            super().rotate(angle, axis, about_point=about_point, **kwargs)
            return

        if about_point is None:
            about_point = self.get_critical_point(ORIGIN)

        if self.mesh.dim == 2:  # always rotate about Z if mesh is 2D
            self.mesh.apply_rotation(angle, OUT, about_point[:2])
        else:
            self.mesh.apply_rotation(angle, axis, about_point)
        super().rotate(angle, axis, about_point=about_point, **kwargs)

    def flip(
        self,
        axis: Vector3D = UP,
        about_point: Point3D | None = None,
        **kwargs,
    ):
        """Flip the mesh (data and Manim objects) about the plane orthogonal to ``axis``.

        The underlying data mesh is updated first; the resulting Manim
        mobject is then flipped with the same arguments.

        Parameters
        ----------
        axis
            Axis orthogonal to the mirror plane.
        about_point
            Pivot point for the flip. Defaults to the critical point at the
            origin.
        **kwargs
            Forwarded to the parent :meth:`~manim.mobject.mobject.Mobject.flip`.
        """
        if self.mesh.dim == 4 and np.asarray(axis, dtype=float).shape[0] == 4:
            center = (
                self._mesh_center()
                if about_point is None
                else self._as_mesh_dim(about_point)
            )
            self.mesh.apply_flip(axis, center)
            self._rebuild_objects()
            return

        if about_point is None:
            about_point = self.get_critical_point(ORIGIN)
        self.mesh.apply_flip(axis, about_point[: self.mesh.dim])
        # Mobject.flip delegates to self.rotate, which this class overrides to
        # rotate the mesh data as well; use the parent rotation to avoid
        # applying the flip to the data twice.
        super().rotate(TAU / 2, axis, about_point=about_point, **kwargs)

    def shift_vertex(self, scene: Scene, vertex_idx: int, shift: Vector3D, **kwargs):
        """Animate a single vertex and update all adjacent faces/edges.

        Parameters
        ----------
        scene
            The scene in which the animation is played.
        vertex_idx
            Index of the vertex to move.
        shift
            Displacement vector (same dimensionality as ``mesh.dim``).
        **kwargs
            May include ``shift_vertex_runtime`` (animation duration in seconds).
        """
        start = self.mesh.vertices[vertex_idx].copy()
        tracker = ValueTracker(0)
        tracker.add_updater(
            # make sure even with multiple calls lambda has the correct values
            lambda mo, go=start, move=shift: self._update_vertex(
                vertex_idx,
                go + tracker.get_value() * move,
                **remove_keys_from_dict(kwargs, ["shift_vertex_runtime"]),
            )
        )
        scene.add(tracker)
        scene.play(
            tracker.animate(**kwargs).set_value(1),
            run_time=(
                kwargs["shift_vertex_runtime"]
                if "shift_vertex_runtime" in kwargs
                else 1.0
            ),
        )
        scene.remove(tracker)

    def shift_vertices(self, scene: Scene, shift: Vector3D, **kwargs):
        """Animate all vertices simultaneously with per-vertex offsets.

        Parameters
        ----------
        scene
            The scene in which the animation is played.
        shift
            Array of displacement vectors, one per vertex (same length as
            ``self.mesh.vertices``).
        **kwargs
            May include ``shift_vertices_runtime`` (animation duration in seconds).
        """
        start = copy.deepcopy(self.mesh.vertices)
        tracker = ValueTracker(0)
        for vertex_idx in range(len(self.mesh.vertices)):
            tracker.add_updater(
                # make sure at the moment when lambda is called, it still has the correct bound loop variable
                lambda mo, bound_v_id=vertex_idx: self._update_vertex(
                    vertex_idx=bound_v_id,
                    pos=start[bound_v_id] + tracker.get_value() * shift[bound_v_id],
                    **remove_keys_from_dict(kwargs, ["shift_vertices_runtime"]),
                )
            )
        scene.add(tracker)
        scene.play(
            tracker.animate(
                **remove_keys_from_dict(kwargs, ["shift_vertices_runtime"])
            ).set_value(1),
            run_time=(
                kwargs["shift_vertices_runtime"]
                if "shift_vertices_runtime" in kwargs
                else 1.0
            ),
        )
        scene.remove(tracker)

    def move_vertices_to(self, scene: Scene, new_positions: Point3D_Array, **kwargs):
        """Animate all vertices to ``new_positions`` and update the underlying mesh.

        Parameters
        ----------
        scene
            The scene in which the animation is played.
        new_positions
            Target positions for every vertex (same shape as ``self.mesh.vertices``).
        **kwargs
            Forwarded to :meth:`~manim_extensions.meshes.models.manim_models.basic_mesh.ManimMesh.shift_vertices`.

        Raises
        ------
        InvalidShapeException
            If ``new_positions`` does not have the same length as the vertex list.
        """
        if len(new_positions) != len(self.mesh.vertices):
            raise InvalidShapeException(
                "new_positions", len(new_positions), len(self.mesh.vertices)
            )
        shift: Point3D_Array = new_positions - self.mesh.vertices
        self.shift_vertices(scene, shift=shift, **kwargs)

    def move_vertex_to(self, scene: Scene, vertex_idx: int, pos: Point3D, **kwargs):
        """Animate a single vertex to a new absolute position.

        Parameters
        ----------
        scene
            The scene in which the animation is played.
        vertex_idx
            Index of the vertex to move.
        pos
            Target position for the vertex (must match ``mesh.dim``).
        **kwargs
            Forwarded to :meth:`~manim_extensions.meshes.models.manim_models.basic_mesh.ManimMesh.shift_vertex`.

        Raises
        ------
        InvalidMeshDimensionsException
            If ``pos`` has the wrong dimensionality.
        """
        # expect pos and curr_pos / mesh.dim to have the same dimensions
        if self.mesh.dim != len(pos):
            raise InvalidMeshDimensionsException(len(pos), self.mesh.dim, "pos")
        shift = pos - self.mesh.vertices[vertex_idx]
        # use shift method to slowly move point to desired place
        self.shift_vertex(scene, vertex_idx, shift, **kwargs)

    def move_to_grid(
        self,
        scene: Scene,
        grid_sizes: tuple[float, ...],
        threshold: tuple[float, ...],
        nof_steps: int = 1,
        **kwargs,
    ):
        """Animate vertices snapping to a regular grid.

        Uses :meth:`~manim_extensions.meshes.models.data_models.mesh.Mesh.snap_to_grid` to compute the target positions and
        then animates the transition via :meth:`~manim_extensions.meshes.models.manim_models.basic_mesh.ManimMesh.move_vertices_to`.

        Parameters
        ----------
        scene
            The scene in which the animation is played.
        grid_sizes
            Grid spacing per dimension.
        threshold
            Per-dimensional snap thresholds.
        nof_steps
            Number of intermediate snap steps.
        **kwargs
            Forwarded to :meth:`~manim_extensions.meshes.models.manim_models.basic_mesh.ManimMesh.move_vertices_to`.
        """
        # to be able to show the movement, the update needs to be calculated on a dummy mesh first
        new_verts = self.mesh.snap_to_grid(
            grid_sizes, threshold, steps=nof_steps, update_verts=False
        )
        # use new calculated positions but have still the old mesh
        self.move_vertices_to(scene, new_verts, **kwargs)


class Manim2DMesh(ManimMesh, metaclass=ConvertToOpenGL):
    """'2D' mesh implementation.

    printing Vertices in Manim is currently not supported for 2D vertices. Therefore, while printing the appropriate
    3D-vertices are used. Everything else should accept plain 2D values. Therefore, this :class:`~manim_extensions.meshes.models.manim_models.basic_mesh.Manim2DMesh` class should
    support 2D vertices or 3D vertices with z-value == 0 on initialization

    This mesh is mainly for Educational purposes and has a few functions we needed for drawing basic
    mesh functionalities. It is performant up to a point and should not be used for large meshes.

    Parameters
    ----------
    mesh
        The mesh data model containing vertices and faces.
    args
        Positional arguments forwarded to the parent :class:`~manim_extensions.meshes.models.manim_models.basic_mesh.ManimMesh`.
    **kwargs
        Additional keyword arguments controlling display options.

        Possible keyword arguments (see :data:`~manim_extensions.meshes.params.BM2DM`):

        * ``display_vertices``: whether to display the vertices
        * ``display_edges``: whether to display the edges
        * ``display_faces``: whether to display the faces
        * ``clear_vertices``: whether to clear the vertices after WHAT?
        * ``clear_edges``: whether to clear the edges after WHAT?
        * ``clear_faces``: whether to clear the faces after WHAT?
        * ``edges_color``: color of the edges
        * ``edges_width``: width of the lines of the edges
        * ``faces_color``: color of the faces
        * ``faces_opacity``: opacity of the faces
        * ``verts_color``: color of the vertices.

    Examples
    --------
    .. manim:: Manim2DMeshExample

       from manim import *
       import numpy as np
       from manim_extensions.meshes.models.data_models.mesh import Mesh
       from manim_extensions.meshes.models.manim_models.basic_mesh import Manim2DMesh

       class Manim2DMeshExample(Scene):
           def construct(self):
               vertices = [[0, 0, 0], [1, 0.1, 0], [0.5, 1.05, 0], [1.5, 0.95, 0]]
               mm = Manim2DMesh(Mesh(vertices, []), display_vertices=True)
               self.add(mm)
               # add the faces one by one
               for face in [[0, 1, 2], [1, 3, 2]]:
                   face_mob, new_edges = mm.add_face(np.array(face), color=TEAL)
                   self.play(FadeIn(face_mob), FadeIn(VGroup(*new_edges)))
               # then snap all vertices onto a regular grid
               mm.move_to_grid(self, (1.0, 1.0, 1.0), (0.2, 0.2, 0.2))
               self.wait()
               content = Group(*self.mobjects)
               content.scale_to_fit_height(5).move_to(ORIGIN)
    """

    # pylint:disable=abstract-method
    def __init__(self, mesh: Mesh, *args, **kwargs):
        # validate if we have a useful 2D mesh
        if mesh.dim == 3:
            if np.sum(np.abs(mesh.vertices[:, 2] != 0)):
                raise InvalidMeshException(
                    "Mesh has z values != 0 and therefore is not 2D."
                )
        elif mesh.dim > 3:
            raise InvalidMeshException(
                f"Mesh is not in the correct format. Expected Dim 2 or 3 with z zero, was {mesh.dim}"
            )
        # init ManimMesh
        super().__init__(
            mesh=mesh,
            *args,
            **{key: get_param_or_default(key, kwargs, BM2DM) for key in BM2DM},
            **remove_keys_from_dict(kwargs, list(BM2DM.keys())),
        )

    def setup_vertices(self) -> Group:
        """Create Manim vertex mobjects for every vertex of the 2D mesh.

        Returns
        -------
            Group containing the vertex mobjects.
        """
        # clear previous work if wanted
        if self.clear_vertices:
            self.vertices = Group()
        # create and add all the points into self.vertices
        for v in self.mesh.get_3d_vertices():
            self.vertices.add(Dot(v, radius=self.verts_size, color=self.verts_color))
        return self.vertices

    def get_dots(self, indices: list) -> List[Dot]:
        """Return Manim :class:`~manim.mobject.geometry.arc.Dot` objects that track the specified vertices.

        Each dot is automatically updated via an updater so that it stays at
        the current vertex position whenever the underlying mesh changes.

        Parameters
        ----------
        indices
            Vertex indices for which to create tracking dots.

        Returns
        -------
            A list of :class:`~manim.mobject.geometry.arc.Dot` mobjects bound to the requested vertices.
        """
        dots = []
        vertices = self.mesh.get_3d_vertices()
        for idx in indices:
            dot = Dot(vertices[idx], radius=self.verts_size, color=RED)
            dot.add_updater(
                lambda mo, mesh=self.mesh, index=idx: mo.move_to(
                    mesh.get_3d_vertices()[index]
                )
            )
            dots.append(dot)
        return dots

# SPDX-FileCopyrightText: 2022 bmmtstb, 99Vicky
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


"""
functions to create delaunay meshes by divide and conquer
"""
from manim import *
# python imports
from typing import List
# third-party imports
import numpy as np
# TODO will most likely be moved in the future
from scipy.spatial import ConvexHull  # pylint: disable=no-name-in-module
# local imports
from manim_extensions.meshes.delaunay.delaunay_criterion import get_triangle_circum_circle_params
from manim_extensions.meshes.models.manim_models.triangle_mesh import TriangleManim2DMesh


def get_clockwise_angle(a, b) -> float:
    """Returns clockwise angle between 2D vectors a and b.

    Parameters
    ----------
    a : numpy.ndarray
        First 2D vector.
    b : numpy.ndarray
        Second 2D vector.

    Returns
    -------
    float
        Clockwise angle in radians between 0 and 2π.
    """
    dot = a[0] * b[0] + a[1] * b[1]  # proportional to cos
    det = a[0] * b[1] - b[0] * a[1]  # proportional to sin
    angle = -np.arctan2(det, dot)  # atan2(sin, cos)
    if angle < 0:  # counterclockwise
        angle = 2 * np.pi + angle
    return angle


def get_counter_clockwise_angle(a, b) -> float:
    """Returns counter-clockwise angle between 2D vectors a and b.

    Parameters
    ----------
    a : numpy.ndarray
        First 2D vector.
    b : numpy.ndarray
        Second 2D vector.

    Returns
    -------
    float
        Counter-clockwise angle in radians between 0 and 2π.
    """
    dot = a[0] * b[0] + a[1] * b[1]  # proportional to cos
    det = a[0] * b[1] - b[0] * a[1]  # proportional to sin
    angle = np.arctan2(det, dot)  # atan2(sin, cos)
    if angle < 0:  # clockwise
        angle = 2 * np.pi + angle
    return angle


class DivideAndConquer:
    """Visualise the divide-and-conquer algorithm for Delaunay triangulation.

    The class operates on a :class:`~manim_extensions.meshes.models.manim_models.triangle_mesh.TriangleManim2DMesh` that has already
    been added to a scene and contains only vertices (no faces yet).  It
    animates the recursive splitting, triangulation of base cases, and
    merging steps described by Guibas and Stolfi.

    Parameters
    ----------
    scene : :class:`~manim.scene.scene.Scene`
        The scene in which the triangulation will be animated.
    triangle_mesh : TriangleManim2DMesh
        A triangle mesh containing only vertices (no faces) that has
        already been added to *scene*.

    Algorithm based on http://www.geom.uiuc.edu/~samuelp/del_project.html

    Examples
    --------
    .. manim:: DivideAndConquerExample
       :save_last_frame:

       from manim import *
       from manim_extensions.meshes.models.data_models.mesh import Mesh
       from manim_extensions.meshes.models.manim_models.triangle_mesh import TriangleManim2DMesh
       from manim_extensions.meshes.delaunay.divide_and_conquer import DivideAndConquer

       class DivideAndConquerExample(Scene):
           def construct(self):
               import numpy as np
               pts = np.random.RandomState(42).rand(10, 3)
               pts[:, 2] = 0
               vertices = pts.tolist()
               faces = []
               mesh_data = Mesh(vertices, faces)
               tm = TriangleManim2DMesh(mesh_data)
               self.add(tm)
               dc = DivideAndConquer(self, tm)
    """

    def __init__(self, scene: Scene, triangle_mesh: TriangleManim2DMesh) -> None:
        """Initialise the divide-and-conquer visualisation helper."""
        self.scene: Scene = scene
        self.triangle_mesh: TriangleManim2DMesh = triangle_mesh

    def split_points(self, vert_indices, dash_length=0.2, line_width=1, speed=1.):
        """Split the vertex set into two halves along the x-coordinate median.

        The vertices referenced by *vert_indices* are sorted by their
        x-coordinate and divided into a left and right subset.  A dashed
        separator line is drawn at the split position.

        Parameters
        ----------
        vert_indices : list of int
            Indices of the vertices to split.
        dash_length : float, optional
            Dash length of the separator line.
        line_width : float, optional
            Stroke width of the separator line.
        speed : float, optional
            Animation speed multiplier (lower is faster).

        Returns
        -------
        tuple[list[int], list[int], :class:`~manim.mobject.geometry.line.DashedLine`]
            Left vertex indices, right vertex indices, and the separator
            line mobject.
        """

        verts_3d = self.triangle_mesh.mesh.get_3d_vertices()
        vertices = verts_3d[vert_indices]

        # sort and get split index
        sort_indices = [x for x, y in sorted(enumerate(vertices), key=lambda x: x[1][0])]
        sorted_verts = [vertices[x] for x in sort_indices]
        sorted_vert_indices = [vert_indices[x] for x in sort_indices]
        split_index = len(sorted_verts) // 2

        # draw split line
        x_mid = (sorted_verts[split_index - 1][0] + sorted_verts[split_index][0]) / 2.
        y_max = np.max(verts_3d[:, 1])
        y_min = np.min(verts_3d[:, 1])
        split_line = DashedLine(start=np.array([x_mid, y_min, 0.]), end=np.array([x_mid, y_max, 0.]),
                                  stroke_width=line_width, dash_length=dash_length)
        self.scene.play(Create(split_line, run_time=1. * speed))
        self.scene.wait(0.3 * speed)

        # return indices of resulting sets
        return sorted_vert_indices[:split_index], sorted_vert_indices[split_index:], split_line

    def triangulate_leq_3(self, vert_indices: List) -> None:
        """Triangulate a base case of at most three vertices.

        Creates a triangle (or a degenerate segment when only two vertices
        are supplied) and adds it to the mesh.

        Parameters
        ----------
        vert_indices : list of int
            Indices of the vertices to triangulate.  The list must contain
            at most three entries.

        Raises
        ------
        ValueError
            If *vert_indices* contains more than three entries.
        """

        if len(vert_indices) > 3:
            raise ValueError("len(vert_indices) must be lower-equal 3")
        if len(vert_indices) > 1:
            if len(vert_indices) == 2:
                vert_indices = vert_indices.copy()
                vert_indices.append(vert_indices[0])
            _, _ = self.triangle_mesh.add_face(np.array(vert_indices))
            # update hack
            self.scene.renderer.update_frame(self.scene)

    def _right_candidate(self, base_lr, rr_edges, speed: float = 1.0):
        """Find the best right-side candidate vertex for the merge step.

        The method evaluates all right-side vertices connected to the
        base edge *base_lr* and returns the first one whose circumscribed
        circle does not contain the next candidate in the angularly sorted
        order (Incircle criterion).  If a conflicting RR edge is found it is
        removed from the mesh.

        Parameters
        ----------
        base_lr : tuple of int
            Indices ``(l, r)`` forming the base edge of the merge.
        rr_edges : set of tuple
            Right-right edges currently present in the mesh.
        speed : float, optional
            Animation speed multiplier.

        Returns
        -------
        int or None
            Index of the right candidate vertex, or ``None`` if no valid
            candidate exists.
        """
        endpoints = [edge[0] if base_lr[1] != edge[0] else edge[1] for edge in rr_edges if base_lr[1] in edge]
        vertices = self.triangle_mesh.mesh.get_3d_vertices()
        angles = np.array(
            [get_clockwise_angle(vertices[base_lr[0]] - vertices[base_lr[1]], vertices[endpoint] - vertices[base_lr[1]])
             for endpoint in endpoints])
        order = np.argsort(angles)
        for i in range(len(endpoints)):
            potential_candidate = endpoints[order[i]]
            next_potential_candidate = endpoints[order[i + 1]] if i != len(endpoints) - 1 else None
            c, r = get_triangle_circum_circle_params(vertices[base_lr[0]], vertices[base_lr[1]],
                                                     vertices[potential_candidate])
            if angles[order[i]] < np.pi:  # angle less than 0 degree
                if next_potential_candidate is None or not np.linalg.norm(c - vertices[endpoints[order[i + 1]]]) < r:
                    return endpoints[order[i]]  # next_potential_candidate not within circle defined by base_lr and
                    # potential_candidate

                # delete RR edge to potential_candidate
                faces = self.triangle_mesh.mesh.faces
                face_idx_to_delete = None
                for face_idx, face in enumerate(faces):
                    if endpoints[order[i]] in face and base_lr[1] in face:
                        face_idx_to_delete = face_idx
                        break
                face, edges = self.triangle_mesh.remove_face(face_idx_to_delete)
                rr_edges.remove(tuple(sorted((base_lr[1], potential_candidate))))
                self.scene.play(FadeOut(face, *edges, run_time=1. * speed))
                self.scene.wait(0.3 * speed)
        return None

    def _left_candidate(self, base_lr, ll_edges, speed: float = 1.0):
        """Find the best left-side candidate vertex for the merge step.

        Mirror of :meth:`~manim_extensions.meshes.delaunay.divide_and_conquer.DivideAndConquer._right_candidate` for the left side.  Evaluates
        left-side vertices connected to the base edge and returns the
        first one satisfying the Incircle criterion, removing conflicting
        LL edges when necessary.

        Parameters
        ----------
        base_lr : tuple of int
            Indices ``(l, r)`` forming the base edge of the merge.
        ll_edges : set of tuple
            Left-left edges currently present in the mesh.
        speed : float, optional
            Animation speed multiplier.

        Returns
        -------
        int or None
            Index of the left candidate vertex, or ``None`` if no valid
            candidate exists.
        """
        endpoints = [edge[0] if base_lr[0] != edge[0] else edge[1] for edge in ll_edges if base_lr[0] in edge]
        vertices = self.triangle_mesh.mesh.get_3d_vertices()
        angles = np.array([get_counter_clockwise_angle(vertices[base_lr[1]] - vertices[base_lr[0]],
                                                       vertices[endpoint] - vertices[base_lr[0]])
                           for endpoint in endpoints])
        order = np.argsort(angles)
        for i in range(len(endpoints)):
            potential_candidate = endpoints[order[i]]
            next_potential_candidate = endpoints[order[i + 1]] if i != len(endpoints) - 1 else None
            c, r = get_triangle_circum_circle_params(vertices[base_lr[0]], vertices[base_lr[1]],
                                                     vertices[potential_candidate])
            if angles[order[i]] < np.pi:
                if next_potential_candidate is None or not np.linalg.norm(c - vertices[endpoints[order[i + 1]]]) < r:
                    return endpoints[order[i]]

                # delete LL edge to potential_candidate
                faces = self.triangle_mesh.mesh.faces
                face_idx_to_delete = None
                for face_idx, face in enumerate(faces):
                    if endpoints[order[i]] in face and base_lr[0] in face:
                        face_idx_to_delete = face_idx
                        break
                face, edges = self.triangle_mesh.remove_face(face_idx_to_delete)
                ll_edges.remove(tuple(sorted((base_lr[0], potential_candidate))))
                self.scene.play(FadeOut(face, *edges, run_time=0.5 * speed))
                self.scene.wait(0.3 * speed)
        return None

    def merge_sets(self, indices_left: List, indices_right: List, split_line: DashedLine, speed: float = 1.0):
        """Merge two Delaunay-triangulated vertex sets into a combined triangulation.

        The method removes the split separator line, locates the base edge
        between the two sets via :meth:`~manim_extensions.meshes.delaunay.divide_and_conquer.DivideAndConquer._find_base_lr`, and iteratively
        adds new triangles by selecting the best left/right candidates
        until the merge is complete.

        Parameters
        ----------
        indices_left : list of int
            Indices of the vertices in the left set.
        indices_right : list of int
            Indices of the vertices in the right set.
        split_line : :class:`~manim.mobject.geometry.line.DashedLine`
            The separator line drawn during :meth:`~manim_extensions.meshes.delaunay.divide_and_conquer.DivideAndConquer.split_points`; it is
            removed as part of the merge animation.
        speed : float, optional
            Animation speed multiplier.

        Returns
        -------
        list of int
            Combined list of vertex indices from both sets.
        """

        # remove split line
        self.scene.play(Uncreate(split_line), run_time=1. * speed)
        self.scene.wait(0.3 * speed)

        base_lr = self._find_base_lr(indices_left, indices_right)
        # check edge[0] != edge[1]: class Mesh does not support plain edges without a face, thus they are drawn as
        # faces, e.g. [0,1,0] for edge (0,1) ~> introduces also invalid edge (0,0)
        rr_edges = set(edge for edge in self.triangle_mesh.mesh.extract_edges() if edge[0] != edge[1]
                       and edge[0] in indices_right and edge[1] in indices_right)
        ll_edges = set(edge for edge in self.triangle_mesh.mesh.extract_edges() if edge[0] != edge[1]
                       and edge[0] in indices_left and edge[1] in indices_left)
        while True:
            r_candidate = self._right_candidate(base_lr, rr_edges, speed)
            l_candidate = self._left_candidate(base_lr, ll_edges, speed)
            if r_candidate is None and l_candidate is None:
                break  # merge complete
            if r_candidate is not None and l_candidate is not None:
                # choose candidate by criterion, see http://www.geom.uiuc.edu/~samuelp/del_project.html
                vertices = self.triangle_mesh.mesh.get_3d_vertices()
                c, r = get_triangle_circum_circle_params(vertices[base_lr[0]], vertices[base_lr[1]],
                                                         vertices[l_candidate])
                if np.linalg.norm(c - vertices[r_candidate]) < r:
                    l_candidate = None
                else:
                    r_candidate = None

            candidate = r_candidate if r_candidate is not None else l_candidate
            indices = indices_right if r_candidate is not None else indices_left
            if len(indices) == 2:  # delete segment (fake face, see comment about check edge[0] != edge[1])
                face = self.triangle_mesh.mesh.find_face(np.array([indices[0], indices[1],
                                                                   indices[0]]))
                if len(face) != 0:  # found
                    face_idx_to_delete = face[0]
                    _, _ = self.triangle_mesh.remove_face(face_idx_to_delete)
            # add new face
            _, _ = self.triangle_mesh.add_face(np.array([base_lr[0], base_lr[1], candidate]))
            base_lr = (base_lr[0], candidate) if r_candidate is not None else (candidate, base_lr[1])
            self.scene.wait(0.3 * speed)
        merged_indices = indices_left.copy()
        merged_indices.extend(indices_right)
        return merged_indices

    def _find_base_lr(self, indices_left: List, indices_right: List):
        """Find the initial base edge connecting the left and right vertex sets.

        The method identifies the rightmost vertex of the left hull and the
        leftmost vertex of the right hull, then walks down the convex hulls
        until the tangent line satisfies the Delaunay criterion.

        Parameters
        ----------
        indices_left : list of int
            Indices of the vertices in the left set.
        indices_right : list of int
            Indices of the vertices in the right set.

        Returns
        -------
        tuple[int, int]
            The ``(l, r)`` vertex indices forming the initial base edge.
        """

        def next_index(cur_idx, indices):
            """Return the next index in a cyclic sequence.

            Parameters
            ----------
            cur_idx : int
                The current index.
            indices : list of int
                The full sequence of indices.

            Returns
            -------
            int or None
                The next index, or ``None`` if ``cur_idx`` is not found.
            """
            for i, idx in enumerate(indices):
                if idx == cur_idx:
                    return indices[(i+1) % len(indices)]
            return None

        def on_right(tangent, point):
            """Check whether a point lies to the right of a tangent line.

            Parameters
            ----------
            tangent : tuple of numpy.ndarray
                The two endpoints of the tangent line.
            point : numpy.ndarray
                The point to test.

            Returns
            -------
            bool
                ``True`` if the point is to the right of the tangent.
            """
            return ((tangent[1][0] - tangent[0][0]) * (point[1] - tangent[0][1]) -
                    (tangent[1][1] - tangent[0][1]) * (point[0] - tangent[0][0])) < 0

        verts = self.triangle_mesh.mesh.get_3d_vertices()
        left_hull = ConvexHull(verts[indices_left][:, :2]).vertices if len(indices_left) > 2 else range(2)
        right_hull = ConvexHull(verts[indices_right][:, :2]).vertices if len(indices_right) > 2 else range(2)
        left = max((v[0], i) for i, v in enumerate(verts[indices_left]))[1]
        right = min((v[0], i) for i, v in enumerate(verts[indices_right]))[1]

        # move tangent 'down'
        next_left = next_index(left, left_hull[::-1])
        next_right = next_index(right, right_hull)
        move_left = on_right((verts[indices_left][left], verts[indices_right][right]),
                             verts[indices_left][next_left])
        move_right = on_right((verts[indices_left][left], verts[indices_right][right]),
                              verts[indices_right][next_right])
        while move_left or move_right:
            if move_left:
                left = next_left
                next_left = next_index(left, left_hull[::-1])
            else:
                right = next_right
                next_right = next_index(right, right_hull)
            move_left = on_right((verts[indices_left][left], verts[indices_right][right]),
                                 verts[indices_left][next_left])
            move_right = on_right((verts[indices_left][left], verts[indices_right][right]),
                                  verts[indices_right][next_right])

        return indices_left[left], indices_right[right]

    def divide_and_conquer_recursive(self, speed: float = 1.0):
        """Run the complete recursive divide-and-conquer algorithm.

        Starts with the full set of mesh vertices and recursively splits,
        triangulates base cases, and merges until a Delaunay triangulation
        is produced.

        Parameters
        ----------
        speed : float, optional
            Animation speed multiplier.

        Raises
        ------
        ValueError
            If the mesh already contains faces (must be empty).
        """

        if len(self.triangle_mesh.mesh.faces) != 0:
            raise ValueError("self.triangle_mesh.mesh.faces must be empty to apply the divide and conquer algorithm!")

        vert_indices = list(range(len(self.triangle_mesh.mesh.vertices)))
        self._divide_and_conquer_recursive(vert_indices, speed)

    def _divide_and_conquer_recursive(self, vert_indices: List, speed: float = 1.0):
        """Internal recursive implementation of the divide-and-conquer algorithm.

        Base cases (<= 3 vertices) are triangulated directly; otherwise the
        set is split and recursively processed before merging.

        Parameters
        ----------
        vert_indices : list of int
            Indices of the vertices to process.
        speed : float, optional
            Animation speed multiplier.

        Returns
        -------
        list of int
            Combined vertex indices after triangulation and merging.
        """

        if len(vert_indices) <= 3:
            self.triangulate_leq_3(vert_indices)
            self.scene.wait(0.3 * speed)
            return vert_indices

        indices_left, indices_right, line = self.split_points(vert_indices)
        vert_indices_left = self._divide_and_conquer_recursive(indices_left, speed=speed)
        vert_indices_right = self._divide_and_conquer_recursive(indices_right, speed=speed)
        return self.merge_sets(vert_indices_left, vert_indices_right, line, speed=speed)
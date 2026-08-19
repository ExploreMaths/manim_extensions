# SPDX-FileCopyrightText: 2022 bmmtstb, 99Vicky
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


"""
functions to check delaunay criterion
"""
# python imports
from typing import List
import numpy as np
# third-party imports
import manim as m
# local imports

from manim_extensions.meshes.models.manim_models.triangle_mesh import TriangleManim2DMesh


def get_triangle_circum_circle_params(
        pt1: np.ndarray,
        pt2: np.ndarray,
        pt3: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Calculate the circumscribed circle of a triangle defined by three points.

    Parameters
    ----------
    pt1 : np.ndarray
        First corner point of the triangle.
    pt2 : np.ndarray
        Second corner point of the triangle.
    pt3 : np.ndarray
        Third corner point of the triangle.

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        Centre point and radius of the circumscribed circle.
    """
    div = 2 * np.linalg.norm(np.cross(pt1 - pt2, pt2 - pt3)) ** 2
    alpha = np.linalg.norm(pt2 - pt3) ** 2 * (pt1 - pt2).dot(pt1 - pt3) / div
    beta = np.linalg.norm(pt1 - pt3) ** 2 * (pt2 - pt1).dot(pt2 - pt3) / div
    gamma = np.linalg.norm(pt1 - pt2) ** 2 * (pt3 - pt1).dot(pt3 - pt2) / div
    center = alpha * pt1 + beta * pt2 + gamma * pt3
    div = 2 * np.linalg.norm(np.cross(pt1 - pt2, pt2 - pt3))
    radius = np.linalg.norm(pt1 - pt2) * np.linalg.norm(pt2 - pt3) * np.linalg.norm(pt3 - pt1) / div
    return center, radius


def get_circum_circle(triangle_mesh: TriangleManim2DMesh, face_idx: int, **kwargs) -> m.Circle:
    """Create a Manim circle visualising the circumscribed circle of a face.

    Parameters
    ----------
    triangle_mesh : TriangleManim2DMesh
        The triangle mesh containing the face.
    face_idx : int
        Index of the face to draw the circle around.
    **kwargs
        Additional keyword arguments forwarded to :class:`~manim.mobject.geometry.arc.Circle`
        (e.g. ``stroke_width``).

    Returns
    -------
    :class:`~manim.mobject.geometry.arc.Circle`
        A Manim circle mobject positioned at the circumscribed centre.
    """
    face = triangle_mesh.mesh.faces[face_idx]
    vertices = [triangle_mesh.mesh.get_3d_vertices()[i] for i in face]
    center, radius = get_triangle_circum_circle_params(*vertices)
    if 'stroke_width' not in kwargs:
        kwargs['stroke_width'] = 2
    circ = m.Circle(radius, **kwargs)
    circ.shift(center)
    return circ


def get_point_indices_violating_delaunay(triangle_mesh: TriangleManim2DMesh, face_id: int) -> List[int]:
    """Return the indices of all vertices that violate the Delaunay criterion.

    A vertex violates the criterion when it lies inside the circumscribed
    circle of the triangle identified by *face_id*.

    Parameters
    ----------
    triangle_mesh : TriangleManim2DMesh
        The triangle mesh.
    face_id : int
        Index of the face (triangle) to test.

    Returns
    -------
    list of int
        Indices of vertices whose distance to the circumscribed centre
        is strictly less than the circumscribed radius.
    """
    indices: List[int] = []
    face = triangle_mesh.mesh.faces[face_id]
    center, radius = get_triangle_circum_circle_params(*[triangle_mesh.mesh.get_3d_vertices()[i] for i in face])

    # TODO: [improve to be faster] don't loop all vertices, only loop ones that are "close", how?
    #  should be possible to do using numpy functions, should be faster and more readable
    for idx, point in enumerate(triangle_mesh.mesh.get_3d_vertices()):
        if idx not in face:
            distance = np.linalg.norm(center - point)
            if distance < radius:  # inside circle
                indices.append(idx)
    return indices


def is_point_violating_delaunay(triangle_mesh: TriangleManim2DMesh, vertex_idx: int, face_idx) -> bool:
    """Check whether a vertex violates the Delaunay criterion for a given face.

    Parameters
    ----------
    triangle_mesh : TriangleManim2DMesh
        The triangle mesh.
    vertex_idx : int
        Index of the vertex to test.
    face_idx : int
        Index of the face (triangle) whose circumscribed circle is tested.

    Returns
    -------
    bool
        ``True`` if the vertex lies strictly inside the circumscribed
        circle of the triangle.
    """
    point = triangle_mesh.mesh.get_3d_vertices()[vertex_idx]
    face = triangle_mesh.mesh.faces[face_idx]
    center, radius = get_triangle_circum_circle_params(*[triangle_mesh.mesh.get_3d_vertices()[i] for i in face])
    distance = np.linalg.norm(center - point)
    return distance < radius
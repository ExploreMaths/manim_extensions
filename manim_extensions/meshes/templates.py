# SPDX-FileCopyrightText: 2022 bmmtstb, 99Vicky
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


"""
define a few basic mesh-structures to be used as examples or test.
"""

# python imports
# patched: lazy-import trimesh (meshes extra)
# patched: implement create_grid for 3D and 4-D meshes
import pathlib
from typing import List

# third-party imports
import numpy as np

# local imports
from .exceptions import InvalidRequestException
from .models.data_models.mesh import Mesh

from ..utils.deps import require


def create_triangle() -> Mesh:
    """
    create most basic triangle mesh.

    Returns
    -------
        The triangle mesh.
    """
    vertices = [
        [0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
    ]
    faces = [
        [0, 1, 2],
    ]
    return Mesh(
        vertices=vertices,
        faces=faces,
    )


def create_pyramid(triangles_only: bool = True) -> Mesh:
    """Create a basic 3D pyramid mesh.

    Parameters
    ----------
    triangles_only
        When ``True``, faces are triangulated; otherwise the square base is
        kept as a single quad face.

    Returns
    -------
        The pyramid mesh.
    """
    vertices = [
        [1, 1, 0],  # 0
        [1, -1, 0],  # 1
        [-1, -1, 0],  # 2
        [-1, 1, 0],  # 3
        [0, 0, 2],  # 4 - tip
    ]
    if triangles_only:
        faces = [
            [0, 4, 1],
            [1, 4, 2],
            [2, 4, 3],
            [3, 4, 0],
            [0, 1, 2],
            [2, 3, 0],
        ]
        parts = [
            [0, 1, 2, 3, 4, 5],
        ]
    else:
        faces = [
            [0, 4, 1],
            [1, 4, 2],
            [2, 4, 3],
            [3, 4, 0],
            [0, 1, 2, 3],
        ]
        parts = [
            [0, 1, 2, 3, 4],
        ]
    return Mesh(
        vertices=vertices,
        faces=faces,
        parts=parts,
    )


def create_cube(triangles_only: bool = True) -> Mesh:
    """Create an equal-sided cube mesh.

    Parameters
    ----------
    triangles_only
        When ``True``, each face is split into two triangles; otherwise
        quad faces are preserved.

    Returns
    -------
        The cube mesh.
    """
    vertices = [
        [0, 0, 0],  # V0
        [1, 0, 0],  # V1
        [0, 1, 0],  # V2
        [0, 0, 1],  # V3
        [0, 1, 1],  # V4
        [1, 0, 1],  # V5
        [1, 1, 0],  # V6
        [1, 1, 1],  # V7
    ]
    if triangles_only:
        faces = [
            [0, 1, 2],  # F0
            [1, 6, 2],  # F1
            [0, 2, 3],  # F2
            [2, 4, 3],  # F3
            [0, 3, 1],  # F4
            [1, 3, 5],  # F5
            [1, 5, 6],  # F6
            [5, 7, 6],  # F7
            [2, 6, 4],  # F8
            [4, 6, 7],  # F9
            [3, 4, 5],  # F10
            [4, 7, 5],  # F11
        ]
        parts = [
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
        ]
    else:
        faces = [
            [0, 1, 6, 2],  # F0
            [0, 2, 4, 3],  # F1
            [0, 3, 5, 1],  # F2
            [1, 5, 7, 6],  # F3
            [2, 6, 7, 4],  # F4
            [3, 4, 7, 5],  # F5
        ]
        parts = [
            [0, 1, 2, 3, 4, 5],
        ]

    return Mesh(
        vertices=vertices,
        faces=faces,
        parts=parts,
    )


def create_coplanar_triangles() -> Mesh:
    """
    create a basic 2D mesh consisting of triangles.

    Returns
    -------
        The 2D mesh consisting of triangles.
    """
    vertices = [
        [-1, 1],
        [1, 2],
        [1, 0],
        [0, 0],
        [-1, -1],
        [1, -1],
        [-1, 2],
    ]
    faces = [[0, 1, 2], [2, 3, 0], [3, 5, 4], [3, 2, 5], [4, 0, 3], [6, 1, 0]]
    return Mesh(
        vertices=vertices,
        faces=faces,
    )


def create_coplanar_points() -> Mesh:
    """
    create a basic 2D mesh without faces ~> exemplary 2D point cloud / set.

    Returns
    -------
        The 2D point cloud mesh without faces.
    """
    vertices = np.array(
        [
            [+1.77291731, -2.42097974],
            [+1.72006063, 2.77386102],
            [-2.47248328, -1.53451374],
            [+0.32320519, 2.34811395],
            [-0.83498357, 0.34056556],
            [+0.43649618, 0.79539595],
            [-0.24413860, -2.04571182],
            [+2.83770675, 2.33446802],
            [+1.27516666, -0.08275843],
            [+1.94458474, -2.79598506],
        ]
    )
    return Mesh(vertices=vertices, faces=[])


def create_grid(areas: List[tuple[float, float, int]]) -> Mesh:
    """Create a regular grid mesh in 1-D, 2-D, 3-D or 4-D.

    Parameters
    ----------
    areas
        One tuple per dimension: ``(min, max, point_count)``.

    Returns
    -------
        A grid mesh with vertices placed at the generated grid points and
        quad faces connecting them (2-D and up) or no faces (1-D).  The
        faces of a 3-D grid form the closed surface of the box spanned by
        the grid, with outward-facing vertex order.  A 4-D grid is a
        tesseract lattice whose faces are the squares of every cubic cell;
        draw it with
        :class:`~manim_extensions.meshes.models.manim_models.basic_mesh.ManimMesh`,
        which projects it onto three dimensions.

    Raises
    ------
    InvalidRequestException
        If more than 4 dimensions are requested.

    Examples
    --------
    .. manim:: GridTemplateExample
       :save_last_frame:

       from manim import *
       from manim_extensions.meshes.templates import create_grid
       from manim_extensions.meshes.models.manim_models.basic_mesh import ManimMesh

       class GridTemplateExample(ThreeDScene):
           def construct(self):
               self.set_camera_orientation(phi=70 * DEGREES, theta=30 * DEGREES)
               grid = ManimMesh(create_grid([(0, 2, 3), (0, 2, 3), (0, 2, 3)]))
               grid.scale_to_fit_height(4).move_to(ORIGIN)
               self.add(grid)

    A 4-D grid is projected onto three dimensions, so the tesseract can be
    drawn directly:

    .. manim:: GridTemplateExample4D
       :save_last_frame:

       from manim import *
       from manim_extensions.meshes.templates import create_grid
       from manim_extensions.meshes.models.manim_models.basic_mesh import ManimMesh

       class GridTemplateExample4D(ThreeDScene):
           def construct(self):
               self.set_camera_orientation(phi=70 * DEGREES, theta=30 * DEGREES)
               grid = ManimMesh(
                   create_grid([(0, 1, 2)] * 4),
                   display_faces=False,
                   edges_color=WHITE,
                   edges_width=2,
               )
               grid.scale_to_fit_height(4).move_to(ORIGIN)
               self.add(grid)
    """
    dim = len(areas)
    vertices = np.array(
        np.meshgrid(
            *[np.linspace(area[0], area[1], int(area[2])) for area in areas],
            indexing="ij",
        )
    ).T.reshape((-1, dim))

    if dim == 1:
        faces = None
        parts = None
    elif dim == 2:
        u, v = int(areas[0][2]), int(areas[1][2])
        faces = [
            np.array(
                [
                    i + j * u,  # bottom left
                    i + j * u + 1,  # bottom right
                    i + (j + 1) * u + 1,  # top right
                    i + (j + 1) * u,  # top left
                ]
            )
            for j in range(v - 1)
            for i in range(u - 1)
        ]
        parts = None
    elif dim == 3:
        u, v, w = (int(area[2]) for area in areas)
        uv = u * v
        faces = []
        for k in range(w - 1):
            for j in range(v - 1):
                for i in range(u - 1):
                    v000 = i + j * u + k * uv
                    v100, v010, v001 = v000 + 1, v000 + u, v000 + uv
                    v110 = v000 + u + 1
                    v101, v011 = v000 + uv + 1, v000 + uv + u
                    v111 = v000 + uv + u + 1
                    faces.extend(
                        [
                            np.array([v000, v010, v110, v100]),  # z = k
                            np.array([v001, v101, v111, v011]),  # z = k + 1
                            np.array([v000, v100, v101, v001]),  # y = j
                            np.array([v010, v011, v111, v110]),  # y = j + 1
                            np.array([v000, v001, v011, v010]),  # x = i
                            np.array([v100, v110, v111, v101]),  # x = i + 1
                        ]
                    )
        parts = None
    elif dim == 4:
        u, v, w, t = (int(area[2]) for area in areas)
        strides = (1, u, u * v, u * v * w)
        counts = (u, v, w, t)
        faces = []
        for first, second in ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)):
            remaining = [axis for axis in range(4) if axis not in (first, second)]
            for indices in np.ndindex(*(counts[axis] for axis in remaining)):
                base = sum(
                    index * strides[axis] for index, axis in zip(indices, remaining)
                )
                step_first, step_second = strides[first], strides[second]
                faces.append(
                    np.array(
                        [
                            base,
                            base + step_first,
                            base + step_first + step_second,
                            base + step_second,
                        ]
                    )
                )
        parts = None
    else:
        raise InvalidRequestException(
            "Only 1D, 2D, 3D and 4D meshes implemented."
        )
    return Mesh(
        vertices=vertices,
        faces=faces,
        parts=parts,
    )


def create_model(filepath: str | pathlib.Path = "", name: str = "") -> Mesh:
    """Load a model file from the ``data/models/`` directory.

    .. warning::

       Very large meshes (> 32 GB RAM, > 30 min) may not be displayable
       with the BasicMesh class.

    Parameters
    ----------
    filepath
        Full path to the model file (supports ``.ply`` and ``.stl``).
    name
        Shorthand for built-in models: ``"armadillo"``, ``"suzanne"``,
        or ``"tail_topper"``.

    Returns
    -------
        The loaded mesh.

    Raises
    ------
    FileNotFoundError
        If neither ``filepath`` nor ``name`` is provided, or if ``name`` is
        not a recognised built-in model.
    """
    if len(name) == 0 and len(filepath) == 0:
        raise FileNotFoundError("Either provide a name or a filepath.")
    trimesh = require("meshes", "trimesh")
    path_to_models = "data/models/"
    # load the ply files
    if name in ["armadillo", "suzanne"]:
        filepath = pathlib.Path(__file__).parent.joinpath(path_to_models, name + ".ply")
    # load the stl files
    elif name in ["tail_topper"]:
        filepath = pathlib.Path(__file__).parent.joinpath(path_to_models, name + ".stl")
    elif name != "":
        raise FileNotFoundError(f"{name} is not a valid object name.")
    # use trimesh to load the files, no parts?
    tmesh = trimesh.load(filepath, force="mesh")
    return Mesh(vertices=tmesh.vertices, faces=tmesh.faces)
# SPDX-FileCopyrightText: 2022 bmmtstb, 99Vicky
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


"""
custom exceptions
"""

# python imports
from typing import Any, Tuple, Union


class InvalidMeshException(Exception):
    """something with the mesh is generally wrong

    Raised by :class:`~manim_extensions.meshes.models.data_models.mesh.Mesh`
    (and related helpers) whenever the supplied mesh data is inconsistent,
    e.g. vertices with mixed dimensionality:

    Examples
    --------
    >>> from manim_extensions.meshes.models.data_models.mesh import Mesh
    >>> Mesh([[0, 0, 0], [1, 0]], None)
    Traceback (most recent call last):
    ...
    manim_extensions.meshes.exceptions.InvalidMeshException: Dimensional mismatch for vertices. ...
    """


class InvalidRequestException(InvalidMeshException):
    """a request was made that is not defined

    Raised when a mesh operation cannot be fulfilled as requested, e.g.
    broadcasting a 4-D mesh to 3-D vertices:

    Examples
    --------
    >>> import numpy as np
    >>> from manim_extensions.meshes.models.data_models.mesh import Mesh
    >>> mesh = Mesh(np.zeros((2, 4)), None)
    >>> mesh.get_3d_vertices()
    Traceback (most recent call last):
    ...
    manim_extensions.meshes.exceptions.InvalidRequestException: Can not Broadcast from 4-D Mesh to 3D Mesh.
    """


class MeshIndexException(IndexError):
    """invalid index

    Raised when a vertex, face, or part index is out of range, e.g.:

    Examples
    --------
    >>> import numpy as np
    >>> from manim_extensions.meshes.models.data_models.mesh import Mesh
    >>> mesh = Mesh(np.array([[0.0, 0, 0], [1, 0, 0]]), None)
    >>> mesh.update_vertex(5, np.array([1, 1, 1]))
    Traceback (most recent call last):
    ...
    manim_extensions.meshes.exceptions.MeshIndexException: Vertex index 5 out of range for vertices of length 2
    """


class InvalidTypeException(TypeError):
    """A mesh function did get a faulty type

    Raised when a parameter has the right container type but an unexpected
    shape, e.g. a 2-D array where a 1-D vertex position is expected:

    Examples
    --------
    >>> import numpy as np
    >>> from manim_extensions.meshes.models.data_models.mesh import Mesh
    >>> mesh = Mesh(np.array([[0.0, 0, 0], [1, 0, 0]]), None)
    >>> mesh.update_vertex(0, np.array([[1, 1, 1]]))
    Traceback (most recent call last):
    ...
    manim_extensions.meshes.exceptions.InvalidTypeException: Vertex [[1 1 1]] has incorrect shape, expected 1D-like array.
    """


class InvalidMeshDimensionsException(Exception):
    """Something with the Mesh Dimensions is not as expected

    Parameters
    ----------
    actual : int or tuple
        The actual dimension value that was found.
    expected : int or tuple
        The expected dimension value.
    name : str, optional
        Optional name of the parameter whose dimensions are invalid.

    Examples
    --------
    Raised when a parameter has the wrong dimensionality, e.g. adding 2-D
    vertices to a 3-D mesh:

    >>> import numpy as np
    >>> from manim_extensions.meshes.models.data_models.mesh import Mesh
    >>> mesh = Mesh(np.array([[0.0, 0, 0], [1, 0, 0]]), None)
    >>> mesh.add_vertices(np.array([[2.0, 0]]))
    Traceback (most recent call last):
    ...
    manim_extensions.meshes.exceptions.InvalidMeshDimensionsException: Dimensions of new_vertices is expected to be ('N', 3) but was (1, 2).
    """

    def __init__(
        self,
        actual: Union[int, Tuple[Any, Any]],
        expected: Union[int, Tuple[Any, Any]],
        name: str = "",
    ):
        """Initialize the InvalidMeshDimensionsException instance."""
        if name == "":
            super().__init__(
                f"Dimensions is expected to be {expected} but was {actual}."
            )
        else:
            super().__init__(
                f"Dimensions of {name} is expected to be {expected} but was {actual}."
            )


class InvalidShapeException(Exception):
    """A new parameter has invalid shape

    Parameters
    ----------
    name : str
        Name of the parameter with the invalid shape.
    actual : int
        The actual size that was found.
    expected : int
        The expected size.

    Examples
    --------
    Raised by :meth:`~manim_extensions.meshes.models.manim_models.basic_mesh.ManimMesh.move_vertices_to`
    when the target position list does not match the number of vertices:

    >>> import numpy as np
    >>> from manim import Scene
    >>> from manim_extensions.meshes.models.data_models.mesh import Mesh
    >>> from manim_extensions.meshes.models.manim_models.basic_mesh import Manim2DMesh
    >>> mm = Manim2DMesh(Mesh([[0, 0, 0], [1, 0, 0], [0, 1, 0]], [[0, 1, 2]]))
    >>> mm.move_vertices_to(Scene(), np.zeros((2, 3)))
    Traceback (most recent call last):
    ...
    manim_extensions.meshes.exceptions.InvalidShapeException: Size of new_positions is expected to be 3 but was 2.
    """

    def __init__(self, name: str, actual: int, expected: int):
        """Initialize the InvalidShapeException instance."""
        super().__init__(
            f"Size of {name} is expected to be {expected} but was {actual}."
        )


class BadParameterException(Exception):
    """Default Class for Parameter Exceptions

    Raised by :func:`~manim_extensions.meshes.params.get_param_or_default`
    when a user-supplied mesh display parameter cannot be cast to the
    expected type:

    Examples
    --------
    >>> from manim_extensions.meshes.params import get_param_or_default, BM2DM
    >>> get_param_or_default("edges_width", {"edges_width": "not a number"}, BM2DM)
    Traceback (most recent call last):
    ...
    manim_extensions.meshes.exceptions.BadParameterException: Value edges_width does not have correct type ...
    """


class FaultyVarArrayException(Exception):
    """The given object is no VarArray

    Base class for errors raised when an object that should be a
    :class:`~manim_extensions.meshes.types.VarArray` (faces, parts, edges)
    has an incompatible structure:

    Examples
    --------
    >>> from manim_extensions.meshes.exceptions import FaultyVarArrayException
    >>> try:
    ...     raise FaultyVarArrayException("The given object is no VarArray")
    ... except FaultyVarArrayException as e:
    ...     print(e)
    The given object is no VarArray
    """

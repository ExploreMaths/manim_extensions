# SPDX-FileCopyrightText: 2022 bmmtstb, 99Vicky
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""
custom exceptions.
"""

# unlinked-class-ok: Mesh

# python imports


class InvalidMeshException(Exception):
    """something with the mesh is generally wrong.

    Raised by :class:`~manim_extensions.meshes.models.data_models.mesh.Mesh`
    (and related helpers) whenever the supplied mesh data is inconsistent,
    e.g. vertices with mixed dimensionality:

    Examples
    --------
    .. nbcell::
       :output-language: pytb

       from manim_extensions.meshes.models.data_models.mesh import Mesh
       Mesh([[0, 0, 0], [1, 0]], None)
    """


class InvalidRequestException(InvalidMeshException):
    """a request was made that is not defined.

    Raised when a mesh operation cannot be fulfilled as requested, e.g.
    projecting a five-dimensional mesh to three dimensions:

    Examples
    --------
    .. nbcell::
       :output-language: pytb

       import numpy as np
       from manim_extensions.meshes.models.data_models.mesh import Mesh
       mesh = Mesh(np.zeros((2, 5)), None)
       mesh.get_3d_vertices()
    """


class MeshIndexException(IndexError):
    """Invalid index.

    Raised when a vertex, face, or part index is out of range, e.g.

    Examples
    --------
    .. nbcell::
       :output-language: pytb

       import numpy as np
       from manim_extensions.meshes.models.data_models.mesh import Mesh
       mesh = Mesh(np.array([[0.0, 0, 0], [1, 0, 0]]), None)
       mesh.update_vertex(5, np.array([1, 1, 1]))
    """


class InvalidTypeException(TypeError):
    """A mesh function did get a faulty type.

    Raised when a parameter has the right container type but an unexpected
    shape, e.g. a 2-D array where a 1-D vertex position is expected:

    Examples
    --------
    .. nbcell::
       :output-language: pytb

       import numpy as np
       from manim_extensions.meshes.models.data_models.mesh import Mesh
       mesh = Mesh(np.array([[0.0, 0, 0], [1, 0, 0]]), None)
       mesh.update_vertex(0, np.array([[1, 1, 1]]))
    """


class InvalidMeshDimensionsException(Exception):
    """Something with the Mesh Dimensions is not as expected.

    Parameters
    ----------
    actual
        The actual dimension value that was found.
    expected
        The expected dimension value.
    name
        Optional name of the parameter whose dimensions are invalid.

    Examples
    --------
    Raised when a parameter has the wrong dimensionality, e.g. adding 2-D
    vertices to a 3-D mesh:

    .. nbcell::
       :output-language: pytb

       import numpy as np
       from manim_extensions.meshes.models.data_models.mesh import Mesh
       mesh = Mesh(np.array([[0.0, 0, 0], [1, 0, 0]]), None)
       mesh.add_vertices(np.array([[2.0, 0]]))
    """

    def __init__(
        self,
        actual: int | tuple[int | str, int | str],
        expected: int | tuple[int | str, int | str],
        name: str = "",
    ):
        if name == "":
            super().__init__(
                f"Dimensions is expected to be {expected} but was {actual}."
            )
        else:
            super().__init__(
                f"Dimensions of {name} is expected to be {expected} but was {actual}."
            )


class InvalidShapeException(Exception):
    """A new parameter has invalid shape.

    Parameters
    ----------
    name
        Name of the parameter with the invalid shape.
    actual
        The actual size that was found.
    expected
        The expected size.

    Examples
    --------
    Raised by :meth:`~manim_extensions.meshes.models.manim_models.basic_mesh.ManimMesh.move_vertices_to`
    when the target position list does not match the number of vertices:

    .. nbcell::
       :output-language: pytb

       import numpy as np
       from manim import Scene
       from manim_extensions.meshes.models.data_models.mesh import Mesh
       from manim_extensions.meshes.models.manim_models.basic_mesh import Manim2DMesh
       mm = Manim2DMesh(Mesh([[0, 0, 0], [1, 0, 0], [0, 1, 0]], [[0, 1, 2]]))
       mm.move_vertices_to(Scene(), np.zeros((2, 3)))
    """

    def __init__(self, name: str, actual: int, expected: int):
        super().__init__(
            f"Size of {name} is expected to be {expected} but was {actual}."
        )


class BadParameterException(Exception):
    """Default Class for Parameter Exceptions.

    Raised by :func:`~manim_extensions.meshes.params.get_param_or_default`
    when a user-supplied mesh display parameter cannot be cast to the
    expected type:

    Examples
    --------
    .. nbcell::
       :output-language: pytb

       from manim_extensions.meshes.params import get_param_or_default, BM2DM
       get_param_or_default("edges_width", {"edges_width": "not a number"}, BM2DM)
    """


class FaultyVarArrayException(Exception):
    """The given object is no VarArray.

    Base class for errors raised when an object that should be a
    :class:`~manim_extensions.meshes.types.VarArray` (faces, parts, edges)
    has an incompatible structure:

    Examples
    --------
    .. nbcell::

       from manim_extensions.meshes.exceptions import FaultyVarArrayException
       try:
           raise FaultyVarArrayException("The given object is no VarArray")
       except FaultyVarArrayException as e:
           print(e)
    """

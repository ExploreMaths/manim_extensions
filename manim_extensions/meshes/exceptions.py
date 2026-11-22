# SPDX-FileCopyrightText: 2022 bmmtstb, 99Vicky
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Exceptions raised while validating mesh topology and geometry."""

# unlinked-class-ok: Mesh

# python imports


class InvalidMeshException(Exception):
    """something with the mesh is generally wrong.

    Raised by :class:`~manim_extensions.meshes.models.data_models.mesh.Mesh`
    (and related helpers) whenever the supplied mesh data is inconsistent,
    e.g. vertices with mixed dimensionality:

    Examples
    --------
    .. manim:: InvalidMeshExceptionOverview
       :save_last_frame:

       from manim import *
       from manim_extensions.meshes.exceptions import InvalidMeshException

       InvalidMeshExceptionTarget = InvalidMeshException

       class InvalidMeshExceptionOverview(Scene):
           def construct(self):
               public = [n for n in dir(InvalidMeshExceptionTarget) if not n.startswith("_")]
               card = VGroup(
                   Text('InvalidMeshException', font_size=36),
                   Text('module: manim_extensions.meshes.exceptions', font_size=18, color=GREY),
                   Text('something with the mesh is generally wrong', font_size=22),
                   Text("API: " + ", ".join(public[:6]), font_size=18, color=BLUE),
               ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
               card.scale_to_fit_width(11.5).move_to(ORIGIN)
               frame = RoundedRectangle(
                   width=12.1, height=card.height + 0.5, corner_radius=0.2, color=BLUE_D
               ).move_to(card)
               self.add(frame, card)

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
    .. manim:: InvalidRequestExceptionOverview
       :save_last_frame:

       from manim import *
       from manim_extensions.meshes.exceptions import InvalidRequestException

       InvalidRequestExceptionTarget = InvalidRequestException

       class InvalidRequestExceptionOverview(Scene):
           def construct(self):
               public = [n for n in dir(InvalidRequestExceptionTarget) if not n.startswith("_")]
               card = VGroup(
                   Text('InvalidRequestException', font_size=36),
                   Text('module: manim_extensions.meshes.exceptions', font_size=18, color=GREY),
                   Text('a request was made that is not defined', font_size=22),
                   Text("API: " + ", ".join(public[:6]), font_size=18, color=BLUE),
               ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
               card.scale_to_fit_width(11.5).move_to(ORIGIN)
               frame = RoundedRectangle(
                   width=12.1, height=card.height + 0.5, corner_radius=0.2, color=BLUE_D
               ).move_to(card)
               self.add(frame, card)

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
    .. manim:: MeshIndexExceptionOverview
       :save_last_frame:

       from manim import *
       from manim_extensions.meshes.exceptions import MeshIndexException

       MeshIndexExceptionTarget = MeshIndexException

       class MeshIndexExceptionOverview(Scene):
           def construct(self):
               public = [n for n in dir(MeshIndexExceptionTarget) if not n.startswith("_")]
               card = VGroup(
                   Text('MeshIndexException', font_size=36),
                   Text('module: manim_extensions.meshes.exceptions', font_size=18, color=GREY),
                   Text('Invalid index', font_size=22),
                   Text("API: " + ", ".join(public[:6]), font_size=18, color=BLUE),
               ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
               card.scale_to_fit_width(11.5).move_to(ORIGIN)
               frame = RoundedRectangle(
                   width=12.1, height=card.height + 0.5, corner_radius=0.2, color=BLUE_D
               ).move_to(card)
               self.add(frame, card)

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
    .. manim:: InvalidTypeExceptionOverview
       :save_last_frame:

       from manim import *
       from manim_extensions.meshes.exceptions import InvalidTypeException

       InvalidTypeExceptionTarget = InvalidTypeException

       class InvalidTypeExceptionOverview(Scene):
           def construct(self):
               public = [n for n in dir(InvalidTypeExceptionTarget) if not n.startswith("_")]
               card = VGroup(
                   Text('InvalidTypeException', font_size=36),
                   Text('module: manim_extensions.meshes.exceptions', font_size=18, color=GREY),
                   Text('A mesh function did get a faulty type', font_size=22),
                   Text("API: " + ", ".join(public[:6]), font_size=18, color=BLUE),
               ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
               card.scale_to_fit_width(11.5).move_to(ORIGIN)
               frame = RoundedRectangle(
                   width=12.1, height=card.height + 0.5, corner_radius=0.2, color=BLUE_D
               ).move_to(card)
               self.add(frame, card)

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
    .. manim:: InvalidMeshDimensionsExceptionOverview
       :save_last_frame:

       from manim import *
       from manim_extensions.meshes.exceptions import InvalidMeshDimensionsException

       InvalidMeshDimensionsExceptionTarget = InvalidMeshDimensionsException

       class InvalidMeshDimensionsExceptionOverview(Scene):
           def construct(self):
               public = [n for n in dir(InvalidMeshDimensionsExceptionTarget) if not n.startswith("_")]
               card = VGroup(
                   Text('InvalidMeshDimensionsException', font_size=36),
                   Text('module: manim_extensions.meshes.exceptions', font_size=18, color=GREY),
                   Text('Something with the Mesh Dimensions is not as expected', font_size=22),
                   Text("API: " + ", ".join(public[:6]), font_size=18, color=BLUE),
               ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
               card.scale_to_fit_width(11.5).move_to(ORIGIN)
               frame = RoundedRectangle(
                   width=12.1, height=card.height + 0.5, corner_radius=0.2, color=BLUE_D
               ).move_to(card)
               self.add(frame, card)

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
    ) -> None:
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
    .. manim:: InvalidShapeExceptionOverview
       :save_last_frame:

       from manim import *
       from manim_extensions.meshes.exceptions import InvalidShapeException

       InvalidShapeExceptionTarget = InvalidShapeException

       class InvalidShapeExceptionOverview(Scene):
           def construct(self):
               public = [n for n in dir(InvalidShapeExceptionTarget) if not n.startswith("_")]
               card = VGroup(
                   Text('InvalidShapeException', font_size=36),
                   Text('module: manim_extensions.meshes.exceptions', font_size=18, color=GREY),
                   Text('A new parameter has invalid shape', font_size=22),
                   Text("API: " + ", ".join(public[:6]), font_size=18, color=BLUE),
               ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
               card.scale_to_fit_width(11.5).move_to(ORIGIN)
               frame = RoundedRectangle(
                   width=12.1, height=card.height + 0.5, corner_radius=0.2, color=BLUE_D
               ).move_to(card)
               self.add(frame, card)

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

    def __init__(self, name: str, actual: int, expected: int) -> None:
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
    .. manim:: BadParameterExceptionOverview
       :save_last_frame:

       from manim import *
       from manim_extensions.meshes.exceptions import BadParameterException

       BadParameterExceptionTarget = BadParameterException

       class BadParameterExceptionOverview(Scene):
           def construct(self):
               public = [n for n in dir(BadParameterExceptionTarget) if not n.startswith("_")]
               card = VGroup(
                   Text('BadParameterException', font_size=36),
                   Text('module: manim_extensions.meshes.exceptions', font_size=18, color=GREY),
                   Text('Default Class for Parameter Exceptions', font_size=22),
                   Text("API: " + ", ".join(public[:6]), font_size=18, color=BLUE),
               ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
               card.scale_to_fit_width(11.5).move_to(ORIGIN)
               frame = RoundedRectangle(
                   width=12.1, height=card.height + 0.5, corner_radius=0.2, color=BLUE_D
               ).move_to(card)
               self.add(frame, card)

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
    .. manim:: FaultyVarArrayExceptionOverview
       :save_last_frame:

       from manim import *
       from manim_extensions.meshes.exceptions import FaultyVarArrayException

       FaultyVarArrayExceptionTarget = FaultyVarArrayException

       class FaultyVarArrayExceptionOverview(Scene):
           def construct(self):
               public = [n for n in dir(FaultyVarArrayExceptionTarget) if not n.startswith("_")]
               card = VGroup(
                   Text('FaultyVarArrayException', font_size=36),
                   Text('module: manim_extensions.meshes.exceptions', font_size=18, color=GREY),
                   Text('The given object is no VarArray', font_size=22),
                   Text("API: " + ", ".join(public[:6]), font_size=18, color=BLUE),
               ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
               card.scale_to_fit_width(11.5).move_to(ORIGIN)
               frame = RoundedRectangle(
                   width=12.1, height=card.height + 0.5, corner_radius=0.2, color=BLUE_D
               ).move_to(card)
               self.add(frame, card)

    .. nbcell::

       from manim_extensions.meshes.exceptions import FaultyVarArrayException
       try:
           raise FaultyVarArrayException("The given object is no VarArray")
       except FaultyVarArrayException as e:
           print(e)
    """

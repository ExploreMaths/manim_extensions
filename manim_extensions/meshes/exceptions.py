"""
custom exceptions
"""
# python imports
from typing import Any, Tuple, Union


class InvalidMeshException(Exception):
    """something with the mesh is generally wrong

    Examples
    --------
    .. manim:: InvalidMeshExceptionExample
       :save_last_frame:

       from manim import *
       from manim_extensions.meshes.exceptions import InvalidMeshException

       class InvalidMeshExceptionExample(Scene):
           def construct(self):
               try:
                   raise InvalidMeshException("Demo error")
               except InvalidMeshException as e:
                   label = Text(str(e), font_size=24).to_edge(UP)
                   self.add(label)
"""


class InvalidRequestException(InvalidMeshException):
    """a request was made that is not defined

    Examples
    --------
    .. manim:: InvalidRequestExceptionExample
       :save_last_frame:

       from manim import *
       from manim_extensions.meshes.exceptions import InvalidRequestException

       class InvalidRequestExceptionExample(Scene):
           def construct(self):
               try:
                   raise InvalidRequestException("Invalid request demo")
               except InvalidRequestException as e:
                   label = Text(str(e), font_size=24).to_edge(UP)
                   self.add(label)
"""


class MeshIndexException(IndexError):
    """invalid index

    Examples
    --------
    .. manim:: MeshIndexExceptionExample
       :save_last_frame:

       from manim import *
       from manim_extensions.meshes.exceptions import MeshIndexException

       class MeshIndexExceptionExample(Scene):
           def construct(self):
               try:
                   raise MeshIndexException("Invalid index demo")
               except MeshIndexException as e:
                   label = Text(str(e), font_size=24).to_edge(UP)
                   self.add(label)
"""


class InvalidTypeException(TypeError):
    """A mesh function did get a faulty type

    Examples
    --------
    .. manim:: InvalidTypeExceptionExample
       :save_last_frame:

       from manim import *
       from manim_extensions.meshes.exceptions import InvalidTypeException

       class InvalidTypeExceptionExample(Scene):
           def construct(self):
               try:
                   raise InvalidTypeException("Invalid type demo")
               except InvalidTypeException as e:
                   label = Text(str(e), font_size=24).to_edge(UP)
                   self.add(label)
"""


class InvalidMeshDimensionsException(Exception):
    """Something with the Mesh Dimensions is not as expected

    Examples
    --------
    .. manim:: InvalidMeshDimensionsExceptionExample
       :save_last_frame:

       from manim import *
       from manim_extensions.meshes.exceptions import InvalidMeshDimensionsException

       class InvalidMeshDimensionsExceptionExample(Scene):
           def construct(self):
               try:
                   raise InvalidMeshDimensionsException(3, 2, "test")
               except InvalidMeshDimensionsException as e:
                   label = Text(str(e), font_size=24).to_edge(UP)
                   self.add(label)
"""
    def __init__(self, actual: Union[int, Tuple[Any, Any]], expected: Union[int, Tuple[Any, Any]], name: str = ""):
        """Initialize the InvalidMeshDimensionsException instance."""
        if name == "":
            super().__init__(f'Dimensions is expected to be {expected} but was {actual}.')
        else:
            super().__init__(f'Dimensions of {name} is expected to be {expected} but was {actual}.')


class InvalidShapeException(Exception):
    """A new parameter has invalid shape

    Examples
    --------
    .. manim:: InvalidShapeExceptionExample
       :save_last_frame:

       from manim import *
       from manim_extensions.meshes.exceptions import InvalidShapeException

       class InvalidShapeExceptionExample(Scene):
           def construct(self):
               try:
                   raise InvalidShapeException("vertices", 3, 2)
               except InvalidShapeException as e:
                   label = Text(str(e), font_size=24).to_edge(UP)
                   self.add(label)
"""
    def __init__(self, name: str, actual: int, expected: int):
        """Initialize the InvalidShapeException instance."""
        super().__init__(f'Size of {name} is expected to be {expected} but was {actual}.')


class BadParameterException(Exception):
    """Default Class for Parameter Exceptions

    Examples
    --------
    .. manim:: BadParameterExceptionExample
       :save_last_frame:

       from manim import *
       from manim_extensions.meshes.exceptions import BadParameterException

       class BadParameterExceptionExample(Scene):
           def construct(self):
               try:
                   raise BadParameterException("Bad parameter demo")
               except BadParameterException as e:
                   label = Text(str(e), font_size=24).to_edge(UP)
                   self.add(label)
"""


class FaultyVarArrayException(Exception):
    """The given object is no VarArray

    Examples
    --------
    .. manim:: FaultyVarArrayExceptionExample
       :save_last_frame:

       from manim import *
       from manim_extensions.meshes.exceptions import FaultyVarArrayException

       class FaultyVarArrayExceptionExample(Scene):
           def construct(self):
               try:
                   raise FaultyVarArrayException("Faulty VarArray demo")
               except FaultyVarArrayException as e:
                   label = Text(str(e), font_size=24).to_edge(UP)
                   self.add(label)
"""
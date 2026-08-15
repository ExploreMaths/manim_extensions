"""Rubik's Cube helpers and scene objects.

The module exposes the main cube model and related animation utilities for
visualising cube states in Manim scenes.

Examples
--------
.. manim:: RubiksCubePackageDocExample
   :save_last_frame:

   from manim import *
   from manim_extensions.rubikscube import RubiksCube

   class RubiksCubePackageDocExample(Scene):
       def construct(self):
           cube = RubiksCube(dim=3).scale(0.5)
           self.add(cube)
"""

from .cube import *
from .cube_animations import *

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:  # pragma: no cover
    import importlib_metadata

try:
    __version__ = importlib_metadata.version(__name__)
except importlib_metadata.PackageNotFoundError:
    __version__ = "0.0.0"

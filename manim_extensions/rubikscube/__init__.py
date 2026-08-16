# SPDX-FileCopyrightText: 2021 KingWampy
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


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
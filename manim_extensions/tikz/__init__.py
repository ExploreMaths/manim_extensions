# SPDX-FileCopyrightText: 2023 Ralphie Raccoon
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


r"""TikZ integration helpers for Manim.

This package exposes the core TikZ mobject wrapper and templating support for
creating diagrammatic scenes based on TikZ input.

Examples
--------
.. manim:: TikzPackageDocExample
   :save_last_frame:

   from manim import *
   from manim_extensions.tikz import Tikz

   class TikzPackageDocExample(Scene):
       def construct(self):
           tikz = Tikz(
               r"\draw[fill=green!30, draw=blue, thick] (0,0) rectangle (2,1);",
               use_pdf=False,
           )
           self.add(tikz)
"""

from manim import *

from .tikz import Tikz
from .template import TikzTemplate
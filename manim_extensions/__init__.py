# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


"""Public entry point for the Manim extensions package.

This package bundles small utility functions and reusable Manim mobjects for
common geometry, animation, and visualisation tasks.

Examples
--------
.. manim:: PackageOverviewDocExample
   :save_last_frame:

   from manim import *
   from manim_extensions import CircleInt, LabelDot

   class PackageOverviewDocExample(Scene):
       def construct(self):
           circle = Circle(radius=1.5, color=BLUE)
           point = LabelDot("P", [0, 0, 0], label_pos=UP)
           self.add(circle, point)
"""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version(__name__)
except PackageNotFoundError:
    __version__ = "0.0.0"

from .mobjects import *
from .geometry import *
from .animations import *

from .algorithm import *
from .automata import *
from .circuit import *
from .compass import *
from .data_structures import *
from .gearbox import *
from .meshes import *
from .mindmap import *
from .neural_network import *
from .physics import *
from .rubikscube import *
from .sequence_diagram import *
from .tikz import *
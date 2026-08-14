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

from .mobjects import *
from .geometry import *
from .animations import *
from .data_structures import *
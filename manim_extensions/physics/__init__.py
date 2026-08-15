"""Physics utilities for Manim scenes.

This package contains tools for optics, electromagnetism, rigid mechanics, and
wave visualisations, all designed to be used directly in scene code.

Examples
--------
.. manim:: PhysicsPackageDocExample
   :save_last_frame:

   from manim import *
   from manim_extensions.physics import Lens

   class PhysicsPackageDocExample(Scene):
       def construct(self):
           lens = Lens(f=1.0, d=0.4)
           self.add(lens)
"""

__version__ = "0.2.3"

from manim import *

from .electromagnetism.electrostatics import *
from .electromagnetism.magnetostatics import *
from .optics.lenses import *
from .optics.rays import *
from .rigid_mechanics.pendulum import *
from .rigid_mechanics.rigid_mechanics import *
from .wave import *

"""Circuit drawing utilities.

This package exposes helper mobjects and utilities for circuit-style diagrams
in Manim scenes.

    Examples
    --------

.. manim:: CircuitPackageDocExample
      :save_last_frame:

   from manim import *
   from manim_extensions.circuit import VoltageSource, Resistor, Capacitor

   class CircuitPackageDocExample(Scene):
       def construct(self):
           vs = VoltageSource(value=5).shift(LEFT * 2)
           r = Resistor(label="10k").next_to(vs, RIGHT, buff=2)
           c = Capacitor(label="100n").next_to(r, RIGHT, buff=2)
           self.add(vs, r, c)
"""

from .mobjects import *
from .utils import *
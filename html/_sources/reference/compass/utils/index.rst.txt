.. SPDX-FileCopyrightText: 2026 jj-math
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

utils
=====

.. module:: manim_extensions.compass.utils

Usage
-----

Geometry helpers for arcs, distances, and angle orientation.

.. manim:: ArcAndDistance
   :save_last_frame:
   :ref_classes: get_arc get_distance

   from manim import *
   from manim_extensions.compass import get_arc, get_distance

   class ArcAndDistance(Scene):
       def construct(self):
           center = LEFT * 2
           arc = get_arc(center, ORIGIN, PI / 2)
           line = DashedLine(center, RIGHT * 2)
           distance = get_distance(center, RIGHT * 2)
           label = MathTex(f"{distance:.1f}").next_to(line, DOWN)
           self.add(line, arc, label)

Modules
-------

.. autosummary::
   :nosignatures:

   ~geometry_method

.. toctree::
   :hidden:
   :maxdepth: 1

   geometry_method

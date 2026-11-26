.. SPDX-FileCopyrightText: 2024 Matheart
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

optics
======

.. automodule:: manim_extensions.physics.optics

Usage
-----

Trace a ray through one or more lenses.

.. manim:: RayScene
   :save_last_frame:
   :ref_classes: Lens Ray

   from manim import *
   from manim_extensions.physics.optics.lenses import Lens
   from manim_extensions.physics.optics.rays import Ray

   class RayScene(Scene):
       def construct(self):
           lens = Lens(f=-5, d=1).shift(LEFT * 3)
           ray = Ray(LEFT * 5 + UP, RIGHT, 8, [lens], color=RED)
           self.add(VGroup(lens, ray).scale(0.85).move_to(ORIGIN))

Modules
-------

.. autosummary::
   :nosignatures:

   ~lenses
   ~rays

.. toctree::
   :hidden:
   :maxdepth: 1

   lenses
   rays

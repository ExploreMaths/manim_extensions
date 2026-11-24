.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

custom_mobjects
===============

.. module:: manim_extensions.pymunk.custom_mobjects

Usage
-----

Ready-made physical mobjects for demos: an apple, a gear, and a spring.

.. manim:: PhysicsMobjects
   :save_last_frame:
   :ref_classes: Apple Gear VSpring

   from manim import *
   from manim_extensions.pymunk.custom_mobjects import Apple, Gear, VSpring

   class PhysicsMobjects(Scene):
       def construct(self):
           apple = Apple(color=RED, fill_color=RED, fill_opacity=0.6).scale(0.5)
           apple.move_to(LEFT * 4 + UP * 2)
           gear = Gear(num_teeth=12, radius=1.0, color=BLUE).scale(0.6)
           gear.move_to(RIGHT * 3 + UP * 2)
           spring = VSpring(
               LEFT * 4 + DOWN * 2, RIGHT * 3 + DOWN * 2,
               turns=14, amplitude=0.2, color=YELLOW,
           )
           self.add(apple, gear, spring)

Modules
-------

.. autosummary::
   :nosignatures:

   ~apple
   ~gear
   ~v_spring

.. toctree::
   :hidden:
   :maxdepth: 1

   apple
   gear
   v_spring

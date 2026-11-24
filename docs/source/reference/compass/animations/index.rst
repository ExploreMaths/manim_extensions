.. SPDX-FileCopyrightText: 2026 jj-math
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

animations
==========

.. module:: manim_extensions.compass.animations

Usage
-----

Animate a compass, pencil, and ruler instead of adding them statically. Import the animation class and pass the mobject you built.

.. manim:: CompassScene
   :ref_classes: Compass PutCompass

   from manim import *
   from manim_extensions.compass import Compass, PutCompass

   class CompassScene(Scene):
       def construct(self):
           compass = Compass().to_edge(LEFT)
           self.play(PutCompass(compass, ORIGIN, 2 * RIGHT))
           self.wait()

Modules
-------

.. autosummary::
   :nosignatures:

   ~animation_compass
   ~animation_pencil
   ~animation_ruler

.. toctree::
   :hidden:
   :maxdepth: 1

   animation_compass
   animation_pencil
   animation_ruler

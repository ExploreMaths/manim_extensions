.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

manim_fontawesome
=================

.. automodule:: manim_extensions.fontawesome.manim_fontawesome

Functions
---------

.. autoall:: manim_extensions.fontawesome.manim_fontawesome
   :types: function

Usage
-----

Get a Font Awesome icon as an SVGMobject.

.. manim:: IconScene
   :save_last_frame:

   from manim import *
   from manim_extensions.fontawesome.manim_fontawesome import solid

   class IconScene(Scene):
       def construct(self):
           rocket = solid.rocket.set_color(ORANGE)
           self.add(rocket)

Constants
---------

.. autoall:: manim_extensions.fontawesome.manim_fontawesome
   :types: data

Classes
-------

.. autosummary::
   :nosignatures:

   ~Brand
   ~BrandEnum
   ~Regular
   ~RegularEnum
   ~Solid
   ~SolidEnum

.. toctree::
   :hidden:
   :maxdepth: 1

   Brand
   BrandEnum
   Regular
   RegularEnum
   Solid
   SolidEnum

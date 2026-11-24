.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

manim_fontawesome
=================

.. module:: manim_extensions.fontawesome.manim_fontawesome

Functions
---------

.. autoall:: manim_extensions.fontawesome.manim_fontawesome
   :types: function

Usage
-----

Get a Font Awesome icon as an SVGMobject.

.. code-block:: python

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

.. toctree::
   :hidden:
   :maxdepth: 1

   Brand
   Regular
   Solid

Classes
========

.. autoclass:: manim_extensions.fontawesome.manim_fontawesome.BrandEnum
   :show-inheritance:
.. autoclass:: manim_extensions.fontawesome.manim_fontawesome.RegularEnum
   :show-inheritance:
.. autoclass:: manim_extensions.fontawesome.manim_fontawesome.SolidEnum
   :show-inheritance:

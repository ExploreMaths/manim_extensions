.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Font Awesome
============

**Original author:** `Naveen M K <https://github.com/naveen521kk>`_

**Source repository:** `GitHub <https://github.com/naveen521kk/manim-fontawesome>`_

**License:** BSD-3-Clause

``manim-fontawesome`` brings `Font Awesome <https://fontawesome.com>`_ icons
into Manim. It bundles 2 000+ SVG icons in three styles — **brand**,
**regular**, and **solid** — and exposes them as Manim
:class:`~manim.mobject.svg.svg_mobject.SVGMobject` instances.

The code is bundled inside ``manim_extensions`` as the
``manim_extensions.fontawesome`` subpackage.

Usage
-----

Each style is a namespace whose attributes are the corresponding SVG
icons — attribute access returns a ready-made
:class:`~manim.mobject.svg.svg_mobject.SVGMobject`:

.. code-block:: python

   from manim import *
   from manim_extensions.fontawesome import solid, regular, brand

   icon = solid.heart          # an SVGMobject, ready to add to a scene
   icon.set_color(RED)
   self.play(FadeIn(icon))

Available styles:

- ``solid`` – solid (filled) icons (Font Awesome ``fas`` set).
- ``regular`` – regular (outline) icons (Font Awesome ``far`` set).
- ``brand`` – brand / logo icons (Font Awesome ``fab`` set).

The variable ``FONT_AWESOME_VERSION`` reports the bundled Font Awesome
version string.

Gallery
-------

A wall of solid icons, staggered in and spun like on the
`Font Awesome homepage <https://fontawesome.com>`_:

.. manim:: FontAwesomeWallExample

   from manim import *
   from manim_extensions.fontawesome import solid, list_icons

   class FontAwesomeWallExample(Scene):
       def construct(self):
           names = list_icons("solid")
           icons = VGroup(*[getattr(solid, n) for n in names[:210]])
           icons.set_color(WHITE)
           # fixed per-icon tilt from the golden angle — fully
           # deterministic, so every build shows the same wall
           for i, icon in enumerate(icons):
               icon.rotate(i * 137.5 * DEGREES)
           icons.arrange_in_grid(rows=14, cols=15, buff=0.32)
           # scale until the grid covers the whole frame (full bleed)
           cover = max(
               (config.frame_width + 0.5) / icons.width,
               (config.frame_height + 0.5) / icons.height,
           )
           icons.scale(cover)
           self.play(LaggedStartMap(FadeIn, icons, lag_ratio=0.01))
           self.play(LaggedStart(
               *[
                   Rotate(icon, angle=TAU, about_point=icon.get_center())
                   for icon in icons
               ],
               lag_ratio=0.01,
           ))
           self.wait()

.. toctree::
   :hidden:

   classes

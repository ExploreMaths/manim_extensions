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
   from manim_extensions.fontawesome import solid

   class FontAwesomeWallExample(Scene):
       def construct(self):
           names = ["heart", "camera", "music", "file", "globe", "house",
                    "bell", "gear", "gift", "user", "comment", "lightbulb",
                    "plane", "thumbs_up", "face_smile", "clock",
                    "headphones", "star", "truck", "clipboard",
                    "bookmark", "calendar", "envelope", "flag", "folder",
                    "image", "map", "paper-plane", "pen", "phone",
                    "camera-retro", "cart-shopping", "cloud", "code",
                    "dice", "feather", "fire", "key", "lock", "moon"]
           icons = VGroup(*[getattr(solid, name.replace("-", "_")) for name in names])
           icons.arrange_in_grid(rows=5, cols=8, buff=0.7)
           icons.set_color(WHITE)
           icons.scale_to_fit_width(config.frame_width - 3)
           self.play(LaggedStartMap(FadeIn, icons, lag_ratio=0.04))
           self.play(LaggedStart(
               *[
                   Rotate(icon, angle=TAU, about_point=icon.get_center())
                   for icon in icons
               ],
               lag_ratio=0.04,
           ))
           self.wait()

.. toctree::
   :hidden:

   classes

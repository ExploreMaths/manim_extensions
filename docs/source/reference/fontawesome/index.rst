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

.. manim:: FontAwesomeHeartExample

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
   from manim_extensions.fontawesome import solid, regular, brand, list_icons

   class FontAwesomeWallExample(Scene):
       def construct(self):
           config.background_color = WHITE  # so new icons default to black
           self.camera.background_color = WHITE  # render the frame white
           # near-square glyphs only — wide glyphs rotated sideways by the
           # tilt below would tower over their neighbours
           pools = {}
           for namespace, style in [(solid, "solid"), (regular, "regular"),
                                    (brand, "brand")]:
               pools[style] = [
                   name for name in list_icons(style)
                   if 0.8 <= getattr(namespace, name).width
                            / getattr(namespace, name).height <= 1.25
               ]
           # alternate the three styles round-robin so the wall mixes
           # filled, outline, and brand glyphs instead of one monotone set
           namespaces = {"solid": solid, "regular": regular, "brand": brand}
           styles = ["solid", "regular", "brand"]
           names = []
           for i in range(240):
               style = styles[i % len(styles)]
               names.append((namespaces[style], pools[style][i // len(styles)]))
           icons = VGroup(*[getattr(ns, n) for ns, n in names])
           # fixed per-icon tilt from the golden angle — fully
           # deterministic, so every build shows the same wall
           for i, icon in enumerate(icons):
               icon.rotate(i * 137.5 * DEGREES)
           icons.arrange_in_grid(rows=12, cols=20, buff=0.35)
           # shrink the glyphs in place (positions unchanged) so the gaps
           # open up — scaling the whole group would shrink the gaps too
           for icon in icons:
               icon.scale(0.75)
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
   functions
   constants

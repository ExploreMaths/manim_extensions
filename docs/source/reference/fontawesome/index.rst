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

Each style is an ``Enum`` whose members are paths to the corresponding SVG
file. Pass the enum member to ``SVGMobject`` to render the icon:

.. code-block:: python

   from manim import *
   from manim_extensions.fontawesome import solid, regular, brand

   icon = SVGMobject(solid.heart.value)
   icon.set_color(RED)

Available styles:

- ``solid`` – solid (filled) icons (Font Awesome ``fas`` set).
- ``regular`` – regular (outline) icons (Font Awesome ``far`` set).
- ``brand`` – brand / logo icons (Font Awesome ``fab`` set).

The variable ``FONT_AWESOME_VERSION`` reports the bundled Font Awesome
version string.

.. toctree::
   :hidden:

   classes

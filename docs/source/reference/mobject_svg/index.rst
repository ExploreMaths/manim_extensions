.. SPDX-FileCopyrightText: 2023 Naveen M K
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Mobject SVG
===========

.. module:: manim_extensions.mobject_svg

.. vendored-status:: naveen521kk/manim-mobject-svg

**Original author:** `Naveen M K <https://github.com/naveen521kk>`_

**Source repository:** `GitHub <https://github.com/naveen521kk/manim-mobject-svg>`_

**License:** MIT

``manim-mobject-svg`` writes a mobject to an SVG file through a Cairo
surface. It registers the helpers on manim's classes as VMobject.to_svg()
and VGroup.to_svg(), so any vectorised mobject can be exported as a
standalone SVG.

The code is bundled inside ``manim_extensions`` as the
``manim_extensions.mobject_svg`` package. ``pycairo`` is the only external
dependency and manim already requires it, so no extra is declared.

:mod:`~manim_extensions.svg_animations` uses it to stream frames as SVG
paths; the two are independent packages, and this one can be imported on
its own.

.. autoall:: manim_extensions.mobject_svg

.. autoall:: manim_extensions.mobject_svg.svg
   :types: function

.. toctree::
   :hidden:
   :maxdepth: 1

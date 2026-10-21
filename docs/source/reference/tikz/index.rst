.. SPDX-FileCopyrightText: 2023 Ralphie Raccoon
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

TikZ
====

.. vendored-status:: ralphieraccoon/manim-tikz

**Original author:** `Ralphie Raccoon <https://github.com/ralphieraccoon>`_

**Source repository:** `GitHub <https://github.com/ralphieraccoon/manim-tikz>`_

**License:** MIT (see the upstream repository for the full license text)

``manim-tikz`` converts TikZ markup into Manim-compatible SVG objects so that
existing LaTeX/TikZ diagrams can be reused in a scene without manually rebuilding
all shapes in Python.

The code is bundled inside ``manim_extensions`` as the
``manim_extensions.tikz`` subpackage.

Features
--------

- :class:`~manim_extensions.tikz.tikz.Tikz` wrapper for converting TikZ code into an :class:`~manim.mobject.svg.svg_mobject.SVGMobject`.
- :class:`~manim_extensions.tikz.template.TikzTemplate` support for reusable LaTeX/TikZ templates.
- integration for drawings that already exist in TikZ format.
- suitable for academic slides and diagram-heavy explanatory scenes.

.. toctree::
   :maxdepth: 1

   classes

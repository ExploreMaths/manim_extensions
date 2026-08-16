.. SPDX-FileCopyrightText: 2023 Ralphie Raccoon
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

TikZ
====

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

Quick start
-----------

.. manim:: TikzLibraryExample
   :save_last_frame:

   from manim import *
   from manim_extensions.tikz import Tikz

   class TikzLibraryExample(Scene):
       def construct(self):
           tikz = Tikz(r"\draw[magenta] (0,0) rectangle (1,1);")
           self.add(tikz)

This package is best for:

* reusing existing TikZ diagrams inside Manim,
* LaTeX-style technical visuals in an animated presentation,
* diagrams that are easier to author in TikZ than by hand in Python.

See the `original repository <https://github.com/ralphieraccoon/manim-tikz>`_
for implementation details and more advanced TikZ conversion examples.

.. toctree::
   :hidden:

   classes
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
all shapes in Python. It adds a :class:`~manim_extensions.tikz.tikz.Tikz`
subclass of Manim's :class:`~manim.mobject.svg.svg_mobject.SVGMobject`, together
with a :class:`~manim_extensions.tikz.template.TikzTemplate` subclass of
Manim's ``TexTemplate`` used behind the scenes. It targets Manim 0.17.0 and
above, which renders SVGs through the ``svgelements`` library.

The code is bundled inside ``manim_extensions`` as the
``manim_extensions.tikz`` subpackage.

Features
--------

- :class:`~manim_extensions.tikz.tikz.Tikz` wrapper for converting TikZ code into an :class:`~manim.mobject.svg.svg_mobject.SVGMobject`.
- :class:`~manim_extensions.tikz.template.TikzTemplate` support for reusable LaTeX/TikZ templates.
- integration for drawings that already exist in TikZ format.
- suitable for academic slides and diagram-heavy explanatory scenes.

Usage
-----

Import :class:`~manim_extensions.tikz.tikz.Tikz` and construct it with the
TikZ code to render inside a scene:

.. code-block:: python

   from manim import *
   from manim_extensions.tikz import Tikz


   class TikzScene(Scene):
       def construct(self):
           test_tex = Tikz(
               r"\draw[magenta, line width=10mm, fill=blue] (0,0) rectangle(1,1);",
               use_pdf=False,
           )
           self.add(test_tex)

The constructor accepts the following arguments (besides ``code``):

- ``code`` – the TikZ code to render, as a string.
- ``packages`` (optional) – a list of strings with extra LaTeX packages to
  include in the preamble via ``\\usepackage``; use this for special fonts or
  symbols your picture needs, e.g. ``marvosym``.
- ``libraries`` (optional) – a list of strings with the TikZ libraries to
  load, such as ``positioning``, ``arrows.meta`` or ``calc``; these are
  added to the preamble via ``\\usetikzlibrary``.
- ``tikzset`` (optional) – a list of strings with style definitions and
  similar to set before the picture (see the `TikZ/PGF manual
  <https://tikz.dev/>`_); added to the preamble via ``\\tikzset``.
- ``preamble`` (optional) – a string of any other commands to add to the
  preamble, such as setting up package options; a mistake here easily
  produces LaTeX errors.
- ``use_pdf`` (optional, default ``False``) – by default the TikZ markup is
  rendered to a DVI file which is then imported into Manim. Some drawing
  commands produced by TikZ do not render properly in DVI and require
  PostScript (PDF); set this to ``True`` to render to a PDF instead when you
  see problems with the output.

Animation
---------

Like any other :class:`~manim.mobject.svg.svg_mobject.SVGMobject`, the result
can be animated with Manim's usual animation functions. Depending on how the
drawing order is interpreted, the result can look a little unexpected, but the
animations generally look good.

Known issues
------------

Line thickness
^^^^^^^^^^^^^^

The default line thickness TikZ produces appears almost imperceptibly thin
when rendered in Manim. Consider increasing ``line width`` in your TikZ
picture; rendering through PDF (``use_pdf=True``) also tends to fix this.

Fadings, gradients, shadows
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Because ``svgelements`` cannot yet parse these features, they are not
currently supported. Attempting to use them will likely result in an
incorrect or empty shape.

.. toctree::
   :maxdepth: 1

   classes

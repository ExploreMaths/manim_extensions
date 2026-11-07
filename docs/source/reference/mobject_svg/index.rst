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
surface. It registers the helpers on manim's classes as a ``to_svg()``
method on ``VMobject`` and ``VGroup``, so any vectorised mobject can be
exported as a standalone SVG.

The code is bundled inside ``manim_extensions`` as the
``manim_extensions.mobject_svg`` package. ``pycairo`` is the only external
dependency and manim already requires it, so no extra is declared.

:mod:`~manim_extensions.svg_animations` uses it to stream frames as SVG
paths; the two are independent packages, and this one can be imported on
its own.

Features
--------

- a ``to_svg()`` method registered on ``VMobject`` and ``VGroup``.
- optional cropping and padding around the exported drawing.
- stroke widths, dashed strokes, gradients and subpaths are preserved.
- rich display of manim mobjects in Jupyter through ``_repr_svg_``.

Usage
-----

Call ``to_svg()`` on any vectorised mobject. Passing ``file_name`` writes the
SVG to that path; when it is omitted a temporary ``.svg`` file is created and
its path returned.

.. manim:: SvgExport
   :save_last_frame:

   from manim import *
   from manim_extensions.mobject_svg import create_svg_from_vmobject

   class SvgExport(Scene):
       def construct(self):
           circle = Circle(color=BLUE, fill_opacity=0.4)
           # writes circle.svg in the current working directory
           create_svg_from_vmobject(circle, "circle.svg")
           self.add(circle)

Pass ``crop=False`` to keep the full frame instead of cropping to the
mobject's bounding box, and ``padding`` to control the margin around the
cropped drawing (``0.05`` manim units by default).

Modules
-------

.. autosummary::
   :nosignatures:

   ~svg

.. toctree::
   :hidden:
   :maxdepth: 1

   svg

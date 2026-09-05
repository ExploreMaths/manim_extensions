.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

SVG Animations
==============

**Original author:** `MathLike <https://github.com/MathItYT>`_

**Source repository:** `GitHub <https://github.com/MathItYT/manim-svg-animations>`_

**License:** MIT

``manim-svg-animations`` exports Manim scenes as interactive HTML + SVG +
JavaScript animations. It converts each frame's mobjects to SVG paths and
generates an HTML file with JavaScript that replays the animation in a
browser.

The code is bundled inside ``manim_extensions`` as the
``manim_extensions.svg_animations`` subpackage.

.. note::

   This module requires the ``manim-mobject-svg`` plugin (it provides
   ``VMobject.to_svg()``). On Python 3.13+ install it with
   ``pip install --ignore-requires-python manim-mobject-svg``.

Features
--------

- :class:`~manim_extensions.svg_animations.html_parsed_vmobject.HTMLParsedVMobject`
  – converts a ``VMobject`` into an SVG-based HTML animation. Attaches to a
  scene as an updater, writes per-frame SVG paths, and produces a finished
  ``.html`` + ``.js`` pair on ``finish()``.

Quick start
-----------

.. code-block:: python

   from manim import *
   from manim_extensions.svg_animations.html_parsed_vmobject import HTMLParsedVMobject

   class SvgAnimationExample(Scene):
       def construct(self):
           square = Square()
           html = HTMLParsedVMobject(square, self)
           self.play(square.animate.rotate(PI))
           html.finish()

.. toctree::
   :hidden:

   classes

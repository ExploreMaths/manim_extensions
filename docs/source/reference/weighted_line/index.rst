.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Weighted Line
=============

**Original author:** `Mutable Learning <https://github.com/mutable-learning>`_

**Source repository:** `GitHub <https://github.com/mutable-learning/manim-weighted-line>`_

**License:** MIT

``manim-weighted-line`` provides a :class:`~manim_extensions.weighted_line.weighted_line.WeightedLine` mobject — a
:class:`~manim.mobject.geometry.line.Line` subclass that displays a
weight label at its midpoint with an optional background rectangle. Useful
for graph-theory and network-flow visualisations.

The code is bundled inside ``manim_extensions`` as the
``manim_extensions.weighted_line`` subpackage.

Features
--------

- :class:`~manim_extensions.weighted_line.weighted_line.WeightedLine` – a
  line with an attached weight label and background.

Quick start
-----------

.. manim:: WeightedLineExample
   :save_last_frame:

   from manim import *
   from manim_extensions.weighted_line import WeightedLine

   class WeightedLineExample(Scene):
       def construct(self):
           line = WeightedLine(LEFT, RIGHT, weight=5)
           self.add(line)

.. toctree::
   :hidden:

   classes

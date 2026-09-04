.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Quick Start
===========

This guide walks through the main parts of ``manim_extensions`` and shows how
to use them in a Manim scene.

Installation
------------

Install the latest stable release from PyPI:

.. code-block:: bash

   pip install manim_extensions

The only runtime dependency is `manim <https://pypi.org/project/manim/>`_.

If you want to use :class:`~manim_extensions.mobjects.ChineseMathTex`, make
sure ``xelatex`` and the ``xeCJK`` LaTeX package are available on your system.

Basic import
------------

Import the public API directly from ``manim_extensions``:

.. code-block:: python

   from manim_extensions import (
       ChineseMathTex,
       LabelDot,
       MathTexLine,
       MathTexBrace,
       MathTexDoublearrow,
       ExtendedLine,
       PerpendicularLine,
       PerpendicularSign,
       VMobjectInt,
       TangentPoint,
       TypeWriter,
   )

Annotated mobjects
------------------

:func:`~manim_extensions.geometry.VMobjectInt` and
:class:`~manim_extensions.mobjects.LabelDot` are useful when you want to label
key points or show intersections.  ``VMobjectInt`` works with any two
VMobjects — circles, lines, arcs, function graphs, text, and so on:

.. manim:: QuickstartAnnotatedScene
   :save_last_frame:

   from manim import *
   from manim_extensions import VMobjectInt, LabelDot

   class QuickstartAnnotatedScene(Scene):
       def construct(self):
           c1 = Circle(radius=2, color=BLUE).shift(LEFT)
           c2 = Circle(radius=2, color=GREEN).shift(RIGHT)
           pts = sorted(VMobjectInt(c1, c2), key=lambda p: p[1])

           self.add(c1, c2)
           self.add(LabelDot("P_1", pts[1], label_pos=UP, buff=0.1))
           self.add(LabelDot("P_2", pts[0], label_pos=DOWN, buff=0.1))

Geometry helpers
----------------

The geometry module provides helpers that return plain points, such as
:func:`~manim_extensions.geometry.VMobjectInt` for intersection points of
arbitrary VMobjects and :func:`~manim_extensions.geometry.TangentPoint` for
circle tangent points, so you can use the results with any Manim mobject:

.. manim:: QuickstartGeometry
   :save_last_frame:

   from manim import *
   from manim_extensions import PerpendicularLine, LabelDot

   class QuickstartGeometry(Scene):
       def construct(self):
           line = Line(LEFT * 3, RIGHT * 3)
           perp = PerpendicularLine(UP * 1.5, line, color=PURE_YELLOW)
           self.add(line, perp)

Animations
----------

:class:`~manim_extensions.animations.TypeWriter` reveals
:class:`~manim.Text` character by character:

.. manim:: QuickstartAnimations

   from manim import *
   from manim_extensions import TypeWriter

   class QuickstartAnimations(Scene):
       def construct(self):
           text = Text("Hello Extensions").shift(DOWN * 2)
           self.play(TypeWriter(text, interval=0.1))

Bundled plugins
---------------

``manim_extensions`` also ships several ready-to-use plugins. Each is documented
in the :doc:`../reference/index` section:

* :doc:`../reference/gearbox/index` – involute gears and gear trains.
* :doc:`../reference/compass/index` – compass, ruler, and pencil animations.
* :doc:`../reference/mindmap/index` – mind maps, timelines, and catalog trees.
* :doc:`../reference/algorithm/index` – algorithm visualization toolkit.
* :doc:`../reference/automata/index` – finite-state, pushdown, and Turing automata.
* :doc:`../reference/circuit/index` – circuit elements and diagrams.
* :doc:`../reference/data_structures/index` – array and variable visualization.
* :doc:`../reference/meshes/index` – 2D/3D mesh data structures and visualization.
* :doc:`../reference/neural_network/index` – neural network mobjects.
* :doc:`../reference/physics/index` – waves, mechanics, optics, and electromagnetism.
* :doc:`../reference/rubikscube/index` – Rubik's cube mobject and animations.
* :doc:`../reference/sequence_diagram/index` – UML sequence diagram helpers.
* :doc:`../reference/tikz/index` – TikZ diagram integration.

For example, a gear pair can be created with:

.. manim:: QuickstartGear

   from manim import *
   from manim_extensions.gearbox import Gear

   class QuickstartGear(Scene):
       def construct(self):
           gear1 = Gear(15, stroke_opacity=0, fill_color=WHITE, fill_opacity=1)
           gear2 = Gear(25, stroke_opacity=0, fill_color=RED, fill_opacity=1)
           gear1.shift(-gear1.rp * 1.5 * RIGHT)
           gear2.mesh_to(gear1)

           self.add(gear1, gear2)
           self.play(
               Rotate(gear1, gear1.pitch_angle, rate_func=linear),
               Rotate(gear2, -gear2.pitch_angle, rate_func=linear),
               run_time=4,
           )

See :doc:`../reference/gearbox/index` for more details.

Next steps
----------

* Browse the :doc:`../examples/index` gallery for more rendered snippets.
* Read the :doc:`../reference/index` for the complete API.
* Check the :doc:`../installation/index` page for development setup.
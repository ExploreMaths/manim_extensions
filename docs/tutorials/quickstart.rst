Quick Start
===========

Installation
------------

Install the latest stable release from PyPI:

.. code-block:: bash

   pip install manim_extensions

The only runtime dependency is `manim <https://pypi.org/project/manim/>`_.

If you want to use :class:`~manim_extensions.mobjects.ChineseMathTex`,
make sure ``xelatex`` and the ``xeCJK`` LaTeX package are available on your
system.

Basic Usage
-----------

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
       CircleInt,
       LineCircleInt,
       LineInt,
       LineArcInt,
       TangentPoint,
       VisDrawArc,
       TypeWriter,
   )

Mobjects Example
~~~~~~~~~~~~~~~~

.. code-block:: python

   from manim import *
   from manim_extensions import LabelDot, ExtendedLine

   class Demo(Scene):
       def construct(self):
           dot = LabelDot("A", [1, 2, 0], label_pos=UP, buff=0.2)
           base = Line(LEFT, RIGHT)
           extended = ExtendedLine(base, extend_distance=1.0, color=RED)
           self.add(dot, extended)

Geometry Example
~~~~~~~~~~~~~~~~

.. code-block:: python

   from manim import *
   from manim_extensions import CircleInt

   c1 = Circle(radius=2).shift(LEFT)
   c2 = Circle(radius=2).shift(RIGHT)
   result = CircleInt(c1, c2)
   if result:
       p1, p2 = result
       print(f"Intersections: {p1}, {p2}")

Animation Example
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from manim import *
   from manim_extensions import VisDrawArc, TypeWriter

   class Demo(Scene):
       def construct(self):
           arc = Arc(start_angle=0, angle=PI, radius=2)
           VisDrawArc(self, arc, axis=OUT, run_time=2)

           text = Text("Hello World")
           self.play(TypeWriter(text, interval=0.1))

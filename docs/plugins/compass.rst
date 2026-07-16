manim-compass
=============

**Original author:** `jj-math <https://github.com/jj-math>`_ (B站博主“**究尽数学**”)

**Source repository:** https://github.com/jj-math/manim-compass

This plugin provides compass-and-straightedge construction tools for Manim:
``Compass``, ``Ruler``, ``Pencil`` mobjects plus matching animation classes. It
is included in this repository as a Git submodule for reference and easy access.

Installation
------------

Install from PyPI:

.. code-block:: bash

   pip install manim-compass

Import in your scene:

.. code-block:: python

   from manim_compass import *

Compass animations
------------------

- ``MoveNiddleTipTo(compass, point)`` – move the compass so its needle tip lands
  at ``point``.
- ``RotateCompass(compass, angle)`` – rotate around the needle tip.
- ``SplitCompass(compass, span)`` – open/close the compass to ``span``.
- ``PutCompass(compass, niddle_pos, pen_pos)`` – place both tips at given
  positions.
- ``PutCompassAway(compass, point, span_buff)`` – put the compass away.
- ``DrawArc(compass, arc)`` – draw an arc with the compass.

Example: moving and opening a compass
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   class CompassExample(Scene):
       def construct(self):
           compass = Compass().to_edge(LEFT)
           self.play(MoveNiddleTipTo(compass, ORIGIN))
           self.play(SplitCompass(compass, 2))
           self.play(RotateCompass(compass, PI / 2))

Pencil and ruler animations
---------------------------

- ``MovePencilTipTo(pencil, point)`` – move the pencil by its tip.
- ``MovePencilAlongPath(pencil, path)`` – slide the pencil tip along a path.
- ``DrawPath(pencil, path)`` – draw a path with the pencil.
- ``PutRuler(ruler, start, end)`` – align a ruler between two points.
- ``PutRulerAway(ruler, point, is_flat)`` – put the ruler away.

Example: drawing a line with ruler and pencil
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   class DrawLineExample(Scene):
       def construct(self):
           ruler = Ruler().to_edge(LEFT)
           pencil = Pencil().to_edge(LEFT)
           path = Line(LEFT, UR)

           self.play(
               PutRuler(ruler, start=LEFT, end=UR),
               MovePencilTipTo(pencil, LEFT),
           )
           self.play(DrawPath(pencil, path))

``CompassScene``
----------------

For complete construction scenes, the plugin also provides ``CompassScene``, a
subclass of ``Scene`` that pre-loads a compass, ruler, and pencil and exposes
convenience methods such as ``draw_arc`` and ``draw_line``. See the demo file in
the upstream repository for a full example.

See the `original README <https://github.com/jj-math/manim-compass/blob/main/README.md>`_
for full details and animated examples.

.. SPDX-FileCopyrightText: 2026 jj-math
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Compass
=======

.. vendored-status:: jj-math/manim-compass

**Original author:** `jj-math <https://github.com/jj-math>`_ (Bilibili creator **Jiujin Math**)

**Source repository:** `GitHub <https://github.com/jj-math/manim-compass>`_

**License:** MIT (see the upstream repository for the full license text)

:class:`~manim_extensions.compass.compass.compass.Compass` provides compass-and-straightedge construction tools for
Manim. It includes :class:`~manim_extensions.compass.compass.compass.Compass`, :class:`~manim_extensions.compass.compass.ruler.Ruler` and :class:`~manim_extensions.compass.compass.pencil.Pencil` mobjects plus matching
animation classes. The code is bundled inside ``manim_extensions`` as the
``manim_extensions.compass`` subpackage.

Features
--------

- :class:`~manim_extensions.compass.compass.compass.Compass` mobject and compass animations:
  :class:`~manim_extensions.compass.animations.animation_compass.MoveNiddleTipTo`, :class:`~manim_extensions.compass.animations.animation_compass.RotateCompass`, :class:`~manim_extensions.compass.animations.animation_compass.SplitCompass`, :class:`~manim_extensions.compass.animations.animation_compass.PutCompass`,
  :class:`~manim_extensions.compass.animations.animation_compass.PutCompassAway`, :class:`~manim_extensions.compass.animations.animation_compass.DrawArc`.
- :class:`~manim_extensions.compass.compass.pencil.Pencil` mobject and pencil animations:
  :class:`~manim_extensions.compass.animations.animation_pencil.MovePencilTipTo`, :class:`~manim_extensions.compass.animations.animation_pencil.PutPencilAway`, :class:`~manim_extensions.compass.animations.animation_pencil.MovePencilAlongPath`, :class:`~manim_extensions.compass.animations.animation_pencil.DrawPath`.
- :class:`~manim_extensions.compass.compass.ruler.Ruler` mobject and ruler animations:
  :class:`~manim_extensions.compass.animations.animation_ruler.PutRuler`, :class:`~manim_extensions.compass.animations.animation_ruler.PutRulerAway`.
- :class:`~manim_extensions.compass.scene.compass_scene.CompassScene` – a convenience :class:`~manim.scene.scene.Scene` subclass pre-equipped with a
  compass, ruler, and pencil.

Using :class:`~manim_extensions.compass.scene.compass_scene.CompassScene`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For more involved constructions, inherit from :class:`~manim_extensions.compass.scene.compass_scene.CompassScene` instead of
:class:`~manim.scene.scene.Scene`. It exposes ready-to-use ``compass``, ``ruler`` and ``pencil``
attributes plus helper methods such as ``draw_arc`` and ``draw_line``. See the
``demo/compass_scene_demo.py`` file in the upstream repository for a complete
example.

Usage
-----

The upstream toolkit grew out of compass-and-straightedge construction
animations (for example, the construction of a regular 257-gon). The bundled
compass, pencil, and ruler mobjects are paired with animation classes that
move, place, and put away the tools.

Compass animations
^^^^^^^^^^^^^^^^^^

:class:`~manim_extensions.compass.animations.animation_compass.MoveNiddleTipTo`
moves the whole compass so that its needle tip reaches a target point;
:class:`~manim_extensions.compass.animations.animation_compass.RotateCompass`
rotates the compass about its needle tip;
:class:`~manim_extensions.compass.animations.animation_compass.SplitCompass`
opens (or closes) the two legs symmetrically until the span equals the given
distance:

.. code-block:: python

   from manim import *
   from manim_extensions.compass import (
       Compass, MoveNiddleTipTo, RotateCompass, SplitCompass)


   class CompassDemo(Scene):
       def construct(self):
           compass = Compass().to_edge(LEFT)
           self.play(MoveNiddleTipTo(compass, ORIGIN))
           self.play(RotateCompass(compass, PI / 2))
           self.play(SplitCompass(compass, 2))

:class:`~manim_extensions.compass.animations.animation_compass.PutCompass`
places the needle tip and pen tip at two given positions;
:class:`~manim_extensions.compass.animations.animation_compass.PutCompassAway`
contracts the legs to ``span_buff`` and parks the compass at a point:

.. code-block:: python

   self.play(PutCompass(compass, niddle_pos=LEFT, pen_pos=RIGHT))
   self.play(PutCompassAway(compass, point=4 * LEFT, span_buff=0.2))

:class:`~manim_extensions.compass.animations.animation_compass.DrawArc`
draws an existing :class:`~manim.mobject.geometry.arc.Arc` with the compass:
with the needle tip at the arc's center and the pen tip at the arc's start, it
rotates the compass while the arc is drawn (it combines the RotateCompass
animation with the arc's Create).

.. code-block:: python

   self.play(DrawArc(compass, arc))

Pencil animations
^^^^^^^^^^^^^^^^^

:class:`~manim_extensions.compass.animations.animation_pencil.MovePencilTipTo`
moves the pencil so its tip reaches a point;
:class:`~manim_extensions.compass.animations.animation_pencil.MovePencilAlongPath`
moves the pencil along a ``VMobject`` path (typically a ``Line`` in
constructions);
:class:`~manim_extensions.compass.animations.animation_pencil.DrawPath`
draws the path: the pen tip starts at the path's beginning and the pencil moves
along it while the path is created (it combines the MovePencilAlongPath
animation with Create).
:class:`~manim_extensions.compass.animations.animation_pencil.PutPencilAway`
parks the pencil at a point; it is equivalent to MovePencilTipTo and kept
for readability in construction scenes:

.. code-block:: python

   from manim import *
   from manim_extensions.compass import (
       Pencil, MovePencilTipTo, MovePencilAlongPath, DrawPath, PutPencilAway)


   class PencilDemo(Scene):
       def construct(self):
           pencil = Pencil().to_edge(LEFT)
           self.play(MovePencilTipTo(pencil, ORIGIN))
           self.play(MovePencilAlongPath(pencil, path))
           self.play(DrawPath(pencil, path))
           self.play(PutPencilAway(pencil, point=4 * LEFT))

Ruler animations
^^^^^^^^^^^^^^^^

:class:`~manim_extensions.compass.animations.animation_ruler.PutRuler`
aligns one edge of the ruler between a start and an end point;
:class:`~manim_extensions.compass.animations.animation_ruler.PutRulerAway`
parks the ruler at a point (``is_flat=True`` lays it out horizontally,
otherwise vertically):

.. code-block:: python

   from manim import *
   from manim_extensions.compass import Ruler, PutRuler, PutRulerAway


   class RulerDemo(Scene):
       def construct(self):
           ruler = Ruler().to_edge(LEFT)
           self.play(PutRuler(ruler, start=LEFT, end=UR))
           self.play(PutRulerAway(ruler, point=LEFT, is_flat=False))

To draw a straightedge line, place the ruler, move the pencil to the line's
start, and draw the path, then put the tools away:

.. code-block:: python

   self.play(
       PutRuler(ruler, start=LEFT, end=UR),
       MovePencilTipTo(pencil, LEFT),
   )
   self.play(DrawPath(pencil, path))
   self.play(
       PutRulerAway(ruler, point=LEFT),
       PutPencilAway(pencil, point=LEFT),
   )

The upstream repository also ships a :class:`~manim_extensions.compass.scene.ruler_scene.SingleRulerScene`
for single-ruler constructions (one ruler, one pencil, with a
:meth:`~manim_extensions.compass.scene.ruler_scene.SingleRulerScene.draw_line_with_pencil`
method); see ``demo/ruler_scene_demo.py``.

.. toctree::
   :hidden:
   :maxdepth: 1

   mobjects
   scene
   compass_animations
   pencil_animations
   ruler_animations
   utilities
   constants

See the `original README <https://github.com/jj-math/manim-compass>`_
for full animated examples and further details.

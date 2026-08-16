Compass
=======

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

Quick start
-----------

Import directly from ``manim_extensions`` (``from manim_extensions.compass import *``).

.. manim:: CompassExample

   from manim import *
   from manim_extensions.compass import Compass, MoveNiddleTipTo, SplitCompass, RotateCompass

   class CompassExample(Scene):
       def construct(self):
           compass = Compass().to_edge(LEFT)
           self.play(MoveNiddleTipTo(compass, ORIGIN))
           self.play(SplitCompass(compass, 2))
           self.play(RotateCompass(compass, PI / 2))

.. manim:: DrawLineExample

   from manim import *
   from manim_extensions.compass import Ruler, Pencil, PutRuler, MovePencilTipTo, DrawPath

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

Using :class:`~manim_extensions.compass.scene.compass_scene.CompassScene`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For more involved constructions, inherit from :class:`~manim_extensions.compass.scene.compass_scene.CompassScene` instead of
:class:`~manim.scene.scene.Scene`. It exposes ready-to-use ``compass``, ``ruler`` and ``pencil``
attributes plus helper methods such as ``draw_arc`` and ``draw_line``. See the
``demo/compass_scene_demo.py`` file in the upstream repository for a complete
example.

.. toctree::
   :hidden:

   mobjects
   scene
   compass_animations
   pencil_animations
   ruler_animations
   utilities

See the `original README <https://github.com/jj-math/manim-compass>`_
for full animated examples and further details.
manim-compass
=============

**Original author:** `jj-math <https://github.com/jj-math>`_ (B站博主“**究尽数学**”)

**Source repository:** https://github.com/jj-math/manim-compass

**License:** MIT (see the upstream repository for the full license text)

``manim-compass`` provides compass-and-straightedge construction tools for
Manim. It includes ``Compass``, ``Ruler`` and ``Pencil`` mobjects plus matching
animation classes. The code is included as a Git submodule under
``third_party/manim-compass``.

Features
--------

- ``Compass`` mobject and compass animations:
  ``MoveNiddleTipTo``, ``RotateCompass``, ``SplitCompass``, ``PutCompass``,
  ``PutCompassAway``, ``DrawArc``.
- ``Pencil`` mobject and pencil animations:
  ``MovePencilTipTo``, ``PutPencilAway``, ``MovePencilAlongPath``, ``DrawPath``.
- ``Ruler`` mobject and ruler animations:
  ``PutRuler``, ``PutRulerAway``.
- ``CompassScene`` – a convenience ``Scene`` subclass pre-equipped with a
  compass, ruler, and pencil.

Installation
------------

Install from PyPI:

.. code-block:: bash

   pip install manim-compass

Or use the local submodule:

.. code-block:: bash

   git submodule update --init third_party/manim-compass
   pip install -e third_party/manim-compass

Quick start
-----------

Import the plugin:

.. code-block:: python

   from manim import *
   from manim_compass import *

Compass example
^^^^^^^^^^^^^^^

.. code-block:: python

   class CompassExample(Scene):
       def construct(self):
           compass = Compass().to_edge(LEFT)
           self.play(MoveNiddleTipTo(compass, ORIGIN))
           self.play(SplitCompass(compass, 2))
           self.play(RotateCompass(compass, PI / 2))

Drawing a line with ruler and pencil
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

Using ``CompassScene``
^^^^^^^^^^^^^^^^^^^^^^

For more involved constructions, inherit from ``CompassScene`` instead of
``Scene``. It exposes ready-to-use ``compass``, ``ruler`` and ``pencil``
attributes plus helper methods such as ``draw_arc`` and ``draw_line``. See the
``demo/compass_scene_demo.py`` file in the upstream repository for a complete
example.

API reference
-------------

.. automodule:: manim_compass
   :members:
   :undoc-members:
   :show-inheritance:

See the `original README <https://github.com/jj-math/manim-compass/blob/main/README.md>`_
for full animated examples and further details.

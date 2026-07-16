manim-compass
=============

**Original author:** `jj-math <https://github.com/jj-math>`_ (B站博主“**究尽数学**”)

**Source repository:** https://github.com/jj-math/manim-compass

**License:** MIT (see the upstream repository for the full license text)

``manim-compass`` provides compass-and-straightedge construction tools for
Manim. It includes ``Compass``, ``Ruler`` and ``Pencil`` mobjects plus matching
animation classes. The code is bundled inside ``manim_extensions`` as the
``manim_extensions.compass`` subpackage and is also kept as a Git submodule
under ``third_party/manim-compass``.

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

Quick start
-----------

Import directly from ``manim_extensions``:

.. code-block:: python

   from manim import *
   from manim_extensions.compass import *

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

Mobjects
^^^^^^^^

.. autoclass:: manim_extensions.compass.Compass
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

.. autoclass:: manim_extensions.compass.Pencil
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

.. autoclass:: manim_extensions.compass.Ruler
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

Scene helper
^^^^^^^^^^^^

.. autoclass:: manim_extensions.compass.CompassScene
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

Compass animations
^^^^^^^^^^^^^^^^^^

.. autoclass:: manim_extensions.compass.MoveNiddleTipTo
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

.. autoclass:: manim_extensions.compass.RotateCompass
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

.. autoclass:: manim_extensions.compass.SplitCompass
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

.. autoclass:: manim_extensions.compass.PutCompass
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

.. autoclass:: manim_extensions.compass.PutCompassAway
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

.. autoclass:: manim_extensions.compass.DrawArc
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

Pencil animations
^^^^^^^^^^^^^^^^^

.. autoclass:: manim_extensions.compass.MovePencilTipTo
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

.. autoclass:: manim_extensions.compass.PutPencilAway
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

.. autoclass:: manim_extensions.compass.MovePencilAlongPath
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

.. autoclass:: manim_extensions.compass.DrawPath
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

Ruler animations
^^^^^^^^^^^^^^^^

.. autoclass:: manim_extensions.compass.PutRuler
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

.. autoclass:: manim_extensions.compass.PutRulerAway
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

Utilities
^^^^^^^^^

.. autofunction:: manim_extensions.compass.get_arc

See the `original README <https://github.com/jj-math/manim-compass/blob/main/README.md>`_
for full animated examples and further details.

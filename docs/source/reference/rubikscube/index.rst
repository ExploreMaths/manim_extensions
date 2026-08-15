Rubik's Cube
============

**Original author:** `KingWampy <https://github.com/WampyCakes>`_

**Source repository:** `GitHub <https://github.com/WampyCakes/manim-rubikscube>`_

**License:** MIT (see the upstream repository for the full license text)

``manim-rubikscube`` is a Manim implementation of the classic Rubik's Cube.
It is designed for puzzle demonstrations, cube-state tutorials, and move-by-move
explanations inside scene code.

The code is bundled inside ``manim_extensions`` as the
``manim_extensions.rubikscube`` subpackage.

Features
--------

- ``RubiksCube`` main cube model.
- cubie-based state and face logic.
- move- and rotation-related animation helpers.
- puzzle-style demos for teaching algorithms and turns.
- easy integration into Manim scenes as a standard mobject.

Quick start
-----------

.. code-block:: python

   from manim import *
   from manim_extensions.rubikscube import RubiksCube

   class RubiksCubeExample(Scene):
       def construct(self):
           cube = RubiksCube(dim=3).scale(0.5)
           self.add(cube)
           self.wait(0.5)

A simple cube scene
^^^^^^^^^^^^^^^^^^^

.. manim:: RubiksCubeLibraryExample
   :save_last_frame:

   from manim import *
   from manim_extensions.rubikscube import RubiksCube

   class RubiksCubeLibraryExample(Scene):
       def construct(self):
           cube = RubiksCube(dim=3).scale(0.5)
           self.add(cube)
           self.wait(0.5)

This package is especially useful for:

* cubing tutorials,
* algorithm explanations for cube solving,
* puzzle-state visualisations in lecture material.

See the `original project <https://github.com/WampyCakes/manim-rubikscube>`_
for the full spec, examples, and documentation.

.. toctree::
   :hidden:

   api
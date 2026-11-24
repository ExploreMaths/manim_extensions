.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

space
=====

.. module:: manim_extensions.pymunk.space

Usage
-----

Create a physics space and run it inside a scene.

.. code-block:: python

   from manim import *
   from manim_extensions.pymunk.space import SpaceScene, VSpace

   class PhysicsScene(SpaceScene):
       def construct(self):
           space = VSpace()
           self.add(space)

Modules
-------

.. autosummary::
   :nosignatures:

   ~SpaceScene
   ~VSpace

.. toctree::
   :hidden:
   :maxdepth: 1

   SpaceScene
   VSpace

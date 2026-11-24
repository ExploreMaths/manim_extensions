.. SPDX-FileCopyrightText: 2026 jj-math
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

scene
=====

.. module:: manim_extensions.compass.scene

Usage
-----

Compass scene classes provide the moving-camera rig used by the `straightedge-compass` examples.

.. code-block:: python

   from manim_extensions.compass.scene import CompassScene

   class Demo(CompassScene):
       def construct(self):
           super().construct()

Modules
-------

.. autosummary::
   :nosignatures:

   ~compass_scene
   ~ruler_scene

.. toctree::
   :hidden:
   :maxdepth: 1

   compass_scene
   ruler_scene

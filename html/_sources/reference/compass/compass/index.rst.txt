.. SPDX-FileCopyrightText: 2026 jj-math
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

compass
=======

.. automodule:: manim_extensions.compass.compass

Classes
-------

.. autosummary::
   :nosignatures:

   ~compass.Compass

Usage
-----

Create the drawing compass and place it in the scene.

.. manim:: CompassScene
   :save_last_frame:
   :ref_classes: Compass

   from manim import *
   from manim_extensions.compass.compass import Compass

   class CompassScene(Scene):
       def construct(self):
           compass = Compass(span=2)
           self.add(compass)

Modules
-------

.. autosummary::
   :nosignatures:

   ~compass
   ~pencil
   ~ruler

.. toctree::
   :hidden:
   :maxdepth: 1

   compass
   pencil
   ruler

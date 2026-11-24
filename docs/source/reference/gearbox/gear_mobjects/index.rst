.. SPDX-FileCopyrightText: 2020 GarryBGoode
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

gear_mobjects
=============

.. module:: manim_extensions.gearbox.gear_mobjects

Usage
-----

Create an involute gear by tooth count and module.

.. manim:: GearScene
   :save_last_frame:
   :ref_classes: Gear

   from manim import *
   from manim_extensions.gearbox.gear_mobjects import Gear

   class GearScene(Scene):
       def construct(self):
           gear = Gear(num_of_teeth=24, module=0.2)
           self.add(gear)

Modules
-------

.. autosummary::
   :nosignatures:

   ~gear_mobject

.. toctree::
   :hidden:
   :maxdepth: 1

   gear_mobject

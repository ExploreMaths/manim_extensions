.. SPDX-FileCopyrightText: 2024 Matheart
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

electromagnetism
================

.. automodule:: manim_extensions.physics.electromagnetism

Usage
-----

Combine point charges with the electric field they generate.

.. manim:: FieldScene
   :save_last_frame:
   :ref_classes: Charge ElectricField

   from manim import *
   from manim_extensions.physics.electromagnetism import Charge, ElectricField

   class FieldScene(Scene):
       def construct(self):
           positive = Charge(1, LEFT * 2)
           negative = Charge(-1, RIGHT * 2)
           field = ElectricField(positive, negative)
           self.add(VGroup(field, positive, negative).scale(0.7).move_to(ORIGIN))

Modules
-------

.. autosummary::
   :nosignatures:

   ~electrostatics
   ~magnetostatics

.. toctree::
   :hidden:
   :maxdepth: 1

   electrostatics
   magnetostatics

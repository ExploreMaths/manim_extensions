.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

constraints
===========

.. automodule:: manim_extensions.pymunk.constraints

Usage
-----

Constraints connect pymunk bodies inside a :class:`~manim_extensions.pymunk.space.VSpace`; choose the constraint class that matches the joint you need.

.. code-block:: python

   from manim_extensions.pymunk.constraints import (
       VPinJoint,
       VPivotJoint,
       VRotaryLimitJoint,
       VSimpleMotor,
   )

Modules
-------

.. autosummary::
   :nosignatures:

   ~constraint
   ~VDampedRotarySpring
   ~VDampedSpring
   ~VGearJoint
   ~VGrooveJoint
   ~VPinJoint
   ~VPivotJoint
   ~VRatchetJoint
   ~VRotaryLimitJoint
   ~VSimpleMotor
   ~VSlideJoint

.. toctree::
   :hidden:
   :maxdepth: 1

   constraint
   VDampedRotarySpring
   VDampedSpring
   VGearJoint
   VGrooveJoint
   VPinJoint
   VPivotJoint
   VRatchetJoint
   VRotaryLimitJoint
   VSimpleMotor
   VSlideJoint

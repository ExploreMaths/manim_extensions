.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Constraints
===========

Visual constraints that attach two bodies to each other. Add them via
:meth:`~manim_extensions.pymunk.space.SpaceScene.SpaceScene.add_constraints`
and the scene applies the Pymunk constraint on every physics step.

Joints
------

.. autoclass:: manim_extensions.pymunk.constraints.VPinJoint.VPinJoint
   :show-inheritance:

.. autoclass:: manim_extensions.pymunk.constraints.VPivotJoint.VPivotJoint
   :show-inheritance:

.. autoclass:: manim_extensions.pymunk.constraints.VGrooveJoint.VGrooveJoint
   :show-inheritance:

.. autoclass:: manim_extensions.pymunk.constraints.VSlideJoint.VSlideJoint
   :show-inheritance:

.. autoclass:: manim_extensions.pymunk.constraints.VRotaryLimitJoint.VRotaryLimitJoint
   :show-inheritance:

.. autoclass:: manim_extensions.pymunk.constraints.VGearJoint.VGearJoint
   :show-inheritance:

.. autoclass:: manim_extensions.pymunk.constraints.VRatchetJoint.VRatchetJoint
   :show-inheritance:

Springs
-------

.. autoclass:: manim_extensions.pymunk.constraints.VDampedSpring.VDampedSpring
   :show-inheritance:

.. autoclass:: manim_extensions.pymunk.constraints.VDampedRotarySpring.VDampedRotarySpring
   :show-inheritance:

Motors
------

.. autoclass:: manim_extensions.pymunk.constraints.VSimpleMotor.VSimpleMotor
   :show-inheritance:

Base class
----------

.. autoclass:: manim_extensions.pymunk.constraints.constraint.VConstraint
   :show-inheritance:

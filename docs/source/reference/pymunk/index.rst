.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Pymunk
======

**Original author:** `CoreKSets <https://github.com/HHP999>`_

**Source repository:** `GitHub <https://github.com/HHP999/manim_pymunk>`_

**License:** MIT

``manim-pymunk`` integrates the `Pymunk <http://www.pymunk.org>`_ 2-D physics
engine with Manim. It provides a physics :class:`~manim_extensions.physics.rigid_mechanics.rigid_mechanics.Space` mobject, a dedicated
:class:`~manim_extensions.physics.rigid_mechanics.rigid_mechanics.SpaceScene` with step-simulation support, and a collection of visual
constraint and mobject classes (springs, pin joints, gears, etc.).

The code is bundled inside ``manim_extensions`` as the
``manim_extensions.pymunk`` subpackage.

Features
--------

- :class:`~manim_extensions.pymunk.space.SpaceScene.SpaceScene` – a
  :class:`~manim.scene.zoomed_scene.ZoomedScene` subclass that steps the
  physics engine on each frame.
- :class:`~manim_extensions.pymunk.space.VSpace.VSpace` – the physics space
  mobject that holds bodies, shapes, and constraints.
- Visual constraints: :class:`~manim_extensions.pymunk.constraints.VPinJoint.VPinJoint`, :class:`~manim_extensions.pymunk.constraints.VPivotJoint.VPivotJoint`, :class:`~manim_extensions.pymunk.constraints.VDampedSpring.VDampedSpring`,
  :class:`~manim_extensions.pymunk.constraints.VGearJoint.VGearJoint`, :class:`~manim_extensions.pymunk.constraints.VGrooveJoint.VGrooveJoint`, :class:`~manim_extensions.pymunk.constraints.VRotaryLimitJoint.VRotaryLimitJoint`, :class:`~manim_extensions.pymunk.constraints.VSlideJoint.VSlideJoint`,
  :class:`~manim_extensions.pymunk.constraints.VSimpleMotor.VSimpleMotor`, :class:`~manim_extensions.pymunk.constraints.VRatchetJoint.VRatchetJoint`, :class:`~manim_extensions.pymunk.constraints.VDampedRotarySpring.VDampedRotarySpring`.
- Custom mobjects: :class:`~manim_extensions.pymunk.custom_mobjects.v_spring.VSpring`, :class:`~manim_extensions.pymunk.custom_mobjects.apple.Apple`, :class:`~manim_extensions.gearbox.gear_mobjects.gear_mobject.Gear`.

Quick start
-----------

.. manim:: PymunkExample
   :save_last_frame:

   from manim import *
   from manim_extensions.pymunk.space.SpaceScene import SpaceScene
   from manim_extensions.pymunk.space.VSpace import VSpace

   class PymunkExample(SpaceScene):
       def construct(self):
           space = VSpace()
           self.add(space)

.. toctree::
   :hidden:

   classes

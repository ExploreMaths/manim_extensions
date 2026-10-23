.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Pymunk
======

.. vendored-status:: HHP999/manim_pymunk

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

Usage
-----

Upstream shipped ``manim-pymunk`` on PyPI; here it is bundled inside
``manim_extensions.pymunk``. Write a scene subclassing
:class:`~manim_extensions.pymunk.space.SpaceScene.SpaceScene`, build ordinary
Manim mobjects, register them as static or dynamic bodies, optionally set
collision filters and constraints, and play — the scene steps the Pymunk space
on every frame.

.. code-block:: python

   from manim import *
   from manim_extensions.pymunk import SpaceScene
   from manim_extensions.pymunk.constraints import VPivotJoint


   class VPivotJointExample(SpaceScene):
       def construct(self):
           static_dot = Dot(ORIGIN)
           square = Square().move_to(static_dot)
           square2 = Square().move_to(static_dot.get_center() + UP * 2).scale(0.5)

           constraints = [
               VPivotJoint(static_dot, square),
               VPivotJoint(square, square2, pivot_world=UP * 3),
           ]

           # register the physics bodies (shapes, mass, angle, ...)
           self.add_static_body(static_dot)
           self.add_dynamic_body(square, square2, angular_velocity=PI * 2)

           # collision filter: which bodies may collide
           self.add_shapes_filter(static_dot, square, square2, group=2)

           # add the visual constraints, then step the simulation
           self.add_constraints(*constraints)
           self.wait(3)

.. note::

   Once an object is under physics control, any Manim animation on it steps the
   simulation until the object is removed from the physics space (or the
   scene updater is removed).

The scene also exposes collision filtering, collision-type and wildcard
collision handlers, force and impulse application, position / velocity query
helpers, and a Matplotlib debug draw of the space.

How it works
^^^^^^^^^^^^

The scene class subclasses
:class:`~manim.scene.zoomed_scene.ZoomedScene` and owns a
:class:`~manim_extensions.pymunk.space.VSpace.VSpace` physics mobject. Each
mobject runs an internal updater that copies Pymunk state back onto the visual;
``body``, ``shapes`` and ``angle`` are attached as mobject attributes. Collision
shapes are generated automatically from Manim geometry: solid shapes become
polygons, hollow shapes are built from line segments, non-convex shapes are
decomposed, and image shapes are extracted from pixel contours. Elasticity,
friction, density, sensor flags and collision callbacks are all configurable on
the body-adding calls, with sensible defaults provided.

.. toctree::
   :maxdepth: 1

   classes
   functions
   constants

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the constraint wrappers in the pymunk subpackage."""

import numpy as np
import pytest
from manim import Circle

from manim_extensions.pymunk.constraints import (
    VDampedRotarySpring,
    VDampedSpring,
    VGearJoint,
    VGrooveJoint,
    VPinJoint,
    VPivotJoint,
    VRatchetJoint,
    VRotaryLimitJoint,
    VSimpleMotor,
    VSlideJoint,
)
from manim_extensions.pymunk.space.SpaceScene import SpaceScene


@pytest.fixture(scope="module")
def physics():
    """A space scene with two dynamic bodies already registered."""
    scene = SpaceScene()
    scene.construct()
    body_a = Circle()
    body_b = Circle()
    scene.add_dynamic_body(body_a, body_b)
    return scene, body_a, body_b


CONSTRAINTS = [
    VDampedRotarySpring,
    VDampedSpring,
    VGearJoint,
    VGrooveJoint,
    VPinJoint,
    VPivotJoint,
    VRatchetJoint,
    VRotaryLimitJoint,
    VSimpleMotor,
    VSlideJoint,
]


@pytest.mark.parametrize("cls", CONSTRAINTS)
def test_constraint_installs(cls, physics):
    scene, body_a, body_b = physics
    constraint = cls(body_a, body_b)

    constraint.install(scene.vspace.space)

    assert constraint.constraint is not None


@pytest.mark.parametrize("cls", CONSTRAINTS)
def test_constraint_updater_runs(cls, physics):
    scene, body_a, body_b = physics
    constraint = cls(body_a, body_b)
    constraint.install(scene.vspace.space)

    constraint.mob_updater(body_a, 0.01)


def test_damped_rotary_spring_parameters(physics):
    scene, body_a, body_b = physics
    spring = VDampedRotarySpring(body_a, body_b, rest_angle=1.0, stiffness=5.0, damping=0.5)
    spring.install(scene.vspace.space)

    assert spring.rest_angle == 1.0
    assert spring.stiffness == 5.0
    assert spring.damping == 0.5


def test_pivot_joint_world_anchor(physics):
    scene, body_a, body_b = physics
    joint = VPivotJoint(body_a, body_b, pivot_world=[0.0, 0.0, 0.0])
    joint.install(scene.vspace.space)

    assert joint.pivot_connect_line_a is not None
    assert joint.pivot_connect_line_b is not None


def test_pivot_joint_local_anchors(physics):
    scene, body_a, body_b = physics
    joint = VPivotJoint(
        body_a,
        body_b,
        anchor_a_local=[0.0, 0.0, 0.0],
        anchor_b_local=[0.0, 0.0, 0.0],
    )
    joint.install(scene.vspace.space)

    assert joint.anchor_connect_line is not None


def test_pivot_joint_zero_length_anchor_is_none(physics):
    scene, body_a, body_b = physics
    joint = VPivotJoint(
        body_a,
        body_b,
        anchor_a_local=np.array([0.0, 0.0]),
        anchor_b_local=np.array([0.0, 0.0]),
        connect_line_class=None,
    )
    joint.install(scene.vspace.space)

    assert joint.anchor_connect_line is None

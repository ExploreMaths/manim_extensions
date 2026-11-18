# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for pymunk constraint guards and optional visual components."""

import pytest
from manim import Circle, Line

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


@pytest.fixture
def scene():
    scene = SpaceScene()
    scene.construct()
    return scene


@pytest.fixture
def bodies(scene):
    body_a = Circle().move_to([-1.0, 0.0, 0.0])
    body_b = Circle().move_to([1.0, 0.0, 0.0])
    scene.add_dynamic_body(body_a, body_b)
    return body_a, body_b


@pytest.mark.parametrize("cls", [VDampedRotarySpring, VPinJoint, VRatchetJoint])
def test_constraint_requires_both_mobjects(cls, scene, bodies):
    body_a, _ = bodies

    with pytest.raises(ValueError, match="without both"):
        cls(None, body_a)


@pytest.mark.parametrize(
    "cls",
    [VDampedRotarySpring, VPinJoint, VRatchetJoint],
)
def test_connect_line_rejects_coincident_points(cls, scene, bodies):
    body_a, body_b = bodies
    body_b.move_to(body_a.get_center())

    with pytest.raises(ValueError, match="same location"):
        cls(body_a, body_b, connect_line_class=Line)


@pytest.mark.parametrize("cls", CONSTRAINTS)
def test_updater_without_install_is_a_noop(cls, bodies):
    body_a, body_b = bodies
    constraint = cls(body_a, body_b)

    constraint.mob_updater(body_a, 0.01)


@pytest.mark.parametrize(
    "cls",
    [VDampedRotarySpring, VPinJoint, VRatchetJoint],
)
def test_optional_connect_line_is_created_and_updated(cls, scene, bodies):
    body_a, body_b = bodies
    constraint = cls(body_a, body_b, connect_line_class=Line)
    constraint.install(scene.vspace.space)

    line = getattr(constraint, "conn_line", None) or getattr(
        constraint, "connect_line", None
    )
    assert line is not None

    constraint.mob_updater(body_a, 0.01)


def test_pin_joint_explicit_distance_is_applied(scene, bodies):
    body_a, body_b = bodies
    joint = VPinJoint(body_a, body_b, distance=3.0)
    joint.install(scene.vspace.space)

    assert joint.constraint.distance == pytest.approx(3.0)


def test_install_without_registered_body_raises(scene):
    body_a = Circle().move_to([-1.0, 0.0, 0.0])
    body_b = Circle().move_to([1.0, 0.0, 0.0])
    constraint = VDampedSpring(body_a, body_b)

    with pytest.raises(ValueError, match="must have"):
        constraint.install(scene.vspace.space)


def test_rotary_limit_updater_runs(scene, bodies):
    body_a, body_b = bodies
    joint = VRotaryLimitJoint(body_a, body_b)
    joint.install(scene.vspace.space)

    joint.mob_updater(body_a, 0.01)


def test_simple_motor_updater_runs(scene, bodies):
    body_a, body_b = bodies
    motor = VSimpleMotor(body_a, body_b)
    motor.install(scene.vspace.space)

    motor.mob_updater(body_a, 0.01)

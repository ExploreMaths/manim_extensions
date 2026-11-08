# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for VSpace collision handlers and body removal."""

import pymunk
from manim import Circle, Square

from manim_extensions.pymunk.space.VSpace import VSpace

BODY_DEFAULTS = dict(
    elasticity=0.8,
    friction=0.8,
    density=1.0,
    sensor=False,
    surface_velocity=(0.0, 0.0),
    center_of_gravity=(0.0, 0.0),
    velocity=(0.0, 0.0),
    angular_velocity=0.0,
)


def test_static_body_registers_shapes_only():
    space = VSpace()
    square = Square()

    space.set_body_and_shapes(square, pymunk.Body.STATIC, is_solid=True, **BODY_DEFAULTS)

    assert getattr(square, "body", None) is not None


def test_shapes_can_be_removed_again():
    space = VSpace()
    circle = Circle()
    space.set_body_and_shapes(circle, pymunk.Body.KINEMATIC, is_solid=True, **BODY_DEFAULTS)

    space.remove_body_shapes_constraints(*circle.shapes)


def test_collision_handler_with_callbacks():
    space = VSpace()

    handler = space._collision_detection_handler(
        1,
        2,
        begin=lambda *args: True,
        pre_solve=lambda *args: True,
        post_solve=lambda *args: None,
        separate=lambda *args: None,
        data={"marker": 1},
    )

    assert handler is None  # pymunk >= 7 registers callbacks directly


def test_collision_handler_without_callbacks():
    space = VSpace()

    handler = space._collision_detection_handler(3, 4)

    assert handler is None  # pymunk >= 7 registers callbacks directly

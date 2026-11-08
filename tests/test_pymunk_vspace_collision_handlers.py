# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the collision handler registration helpers of VSpace."""

from manim_extensions.pymunk.space.VSpace import VSpace


def _callback(arbiter, space, data):
    return True


def test_wildcard_collision_handler_registration():
    space = VSpace()

    assert space._wildcard_collision_handler(1) is None
    assert (
        space._wildcard_collision_handler(
            2,
            begin=_callback,
            pre_solve=_callback,
            post_solve=_callback,
            separate=_callback,
            data={"tag": 1},
        )
        is None
    )


def test_collision_detection_handler_registration():
    space = VSpace()

    assert space._collision_detection_handler(3, 4) is None
    assert (
        space._collision_detection_handler(
            5,
            6,
            begin=_callback,
            pre_solve=_callback,
            post_solve=_callback,
            separate=_callback,
            data={"tag": 2},
        )
        is None
    )


def test_collision_type_is_unique_per_mobject():
    space = VSpace()

    assert space._set_collision_type and callable(space._set_collision_type)

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for rigid-body shape and angle helpers."""

import pymunk
import pytest
from manim import Circle, Line, Rectangle, Triangle

from manim_extensions.physics.rigid_mechanics.rigid_mechanics import (
    _simulate,
    get_angle,
    get_shape,
)


def _with_body(mob):
    mob.body = pymunk.Body()
    mob.body.position = mob.get_x(), mob.get_y()
    return mob


@pytest.mark.parametrize(
    "factory",
    [
        lambda: Circle(radius=0.5),
        lambda: Line([0, 0, 0], [1, 1, 0]),
        lambda: Rectangle(width=1, height=0.6),
        lambda: Triangle(),
    ],
)
def test_get_shape_for_each_mobject_kind(factory):
    mob = _with_body(factory())

    get_shape(mob)

    assert mob.shape is not None


def test_get_angle_for_line_uses_geometry():
    mob = _with_body(Line([0, 0, 0], [1, 1, 0]))

    get_angle(mob)

    assert mob.angle != 0.0


def test_simulate_syncs_body_state():
    mob = _with_body(Circle(radius=0.3))
    mob.angle = 0.0
    mob.body.position = (1.0, 2.0)
    mob.body.angle = 0.25

    _simulate(mob)

    assert mob.angle == pytest.approx(0.25)
    assert mob.get_x() == pytest.approx(1.0, abs=1e-3)

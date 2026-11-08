# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for pymunk pin joints and rod redrawing on the pendulum."""

import numpy as np
import pytest
from manim import tempconfig

from manim_extensions.physics.rigid_mechanics.pendulum import MultiPendulum
from manim_extensions.pymunk.space.SpaceScene import SpaceScene


@pytest.fixture(autouse=True)
def _config():
    with tempconfig({"dry_run": True, "disable_caching": True, "renderer": "cairo"}):
        yield


@pytest.fixture(scope="module")
def physics():
    scene = SpaceScene()
    scene.construct()
    return scene


@pytest.fixture()
def multi(physics):
    pendulum = MultiPendulum(
        np.array([0.0, -1.0, 0.0]),
        np.array([0.0, -2.0, 0.0]),
    )
    physics.add_dynamic_body(pendulum.bobs, family_members=True)
    for bob in pendulum.bobs:
        bob.spacescene = physics
    return pendulum


def test_multi_pendulum_builds_two_rods(multi):
    assert len(multi.rods) == 2


def test_redraw_rods_from_coordinate_pin(multi):
    rod = multi.rods[0]

    multi._redraw_rods(
        rod,
        [np.array([0.0, 2.0, 0.0]), multi.bobs[0]],
        0,
    )

    assert rod.get_start() is not None


def test_start_swinging_adds_joints(multi, physics):
    before = len(physics.vspace.space.constraints)

    multi.start_swinging()

    assert len(physics.vspace.space.constraints) > before


def test_end_swinging_calls_stop_rigidity(multi):
    class StubScene:
        stopped = None

        def stop_rigidity(self, mobs):
            self.stopped = mobs

    scene = StubScene()
    for bob in multi.bobs:
        bob.spacescene = scene

    multi.end_swinging()

    assert scene.stopped is multi.bobs

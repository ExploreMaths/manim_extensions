# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the compass drawing scene."""

import numpy as np
import pytest
from manim import LEFT, RIGHT, UP, tempconfig

from manim_extensions.compass.scene.compass_scene import CompassScene


@pytest.fixture()
def scene():
    with tempconfig({"dry_run": True, "disable_caching": True, "renderer": "cairo"}):
        instance = CompassScene()
        instance.setup()
        yield instance


def test_setup_places_instruments(scene):
    assert scene.compass is not None
    assert scene.ruler is not None


def test_draw_arc(scene):
    arc = scene.draw_arc(niddle_point=np.array([0.0, 0.0, 0.0]), pen_point=RIGHT, run_time=0.1)

    assert arc is not None


def test_draw_line(scene):
    line = scene.draw_line(LEFT, 2 * UP, run_time=0.1)

    assert line is not None


def test_rotate_compass_about_niddle_tip(scene):
    scene.rotate_compass_about_niddle_tip(0.5, run_time=0.1)

    assert scene.compass is not None


def test_put_instruments_aside(scene):
    scene.put_compass_aside(run_time=0.1)
    scene.put_ruler_aside(run_time=0.1)

    assert scene.compass is not None and scene.ruler is not None

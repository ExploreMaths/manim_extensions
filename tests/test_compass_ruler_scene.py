# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the ruler-and-pencil drawing scene."""

import pytest
from manim import LEFT, UP, tempconfig

from manim_extensions.compass.scene.ruler_scene import SingleRulerScene


@pytest.fixture()
def scene():
    with tempconfig({"dry_run": True, "disable_caching": True, "renderer": "cairo"}):
        instance = SingleRulerScene()
        instance.setup()
        yield instance


def test_setup_places_ruler_and_pencil(scene):
    assert scene.ruler is not None
    assert scene.pencil is not None


def test_draw_line_with_pencil(scene):
    line = scene.draw_line_with_pencil(LEFT, 3 * UP, run_time=0.1)

    assert line is not None


def test_put_ruler_back(scene):
    scene.draw_line_with_pencil(LEFT, 3 * UP, run_time=0.1)
    scene.put_ruler_back(run_time=0.1)

    assert scene.ruler is not None

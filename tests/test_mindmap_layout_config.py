# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for layout configuration validation and per-layout settings."""

import pytest
from manim import DOWN, LEFT, RIGHT, UP

from manim_extensions.mindmap.algorithms.layout_config import (
    LayoutConfig,
    LayoutDirection,
)


def test_defaults_produce_left_to_right_layout():
    config = LayoutConfig()

    assert config.layout_direction == LayoutDirection.LeftToRight
    assert config.sides == (LayoutDirection.BottomToTop, LayoutDirection.TopToBottom)


@pytest.mark.parametrize(
    "direction,expected",
    [
        (UP, LayoutDirection.BottomToTop),
        (DOWN, LayoutDirection.TopToBottom),
        (LEFT, LayoutDirection.RightToLeft),
        (RIGHT, LayoutDirection.LeftToRight),
    ],
)
def test_direction_mapping(direction, expected):
    assert LayoutConfig(direction=direction).get_layout_direction(direction) is expected


def test_invalid_direction_raises():
    with pytest.raises(ValueError):
        LayoutConfig(direction=[1.0, 1.0, 0.0])


def test_single_side_is_wrapped_into_tuple():
    config = LayoutConfig(sides=UP)

    assert config.sides == (LayoutDirection.BottomToTop,)


def test_invalid_side_raises():
    with pytest.raises(ValueError):
        LayoutConfig(sides=LEFT)


def test_catalog_setter_updates_spacing():
    config = LayoutConfig()
    config.catalog = {"node_spacing": 0.75, "level_spacing": 1.25}

    assert config.node_spacing == 0.75
    assert config.level_spacing == 1.25


def test_mindmap_setter_updates_direction_and_spacing():
    config = LayoutConfig()
    config.mindmap = {"direction": DOWN, "node_spacing": 0.8, "level_spacing": 0.9}

    assert config.layout_direction == LayoutDirection.TopToBottom
    assert config.node_spacing == 0.8


def test_mindmap_setter_rejects_bad_direction():
    config = LayoutConfig()

    with pytest.raises(ValueError):
        config.mindmap = {"direction": [1.0, 1.0, 0.0]}


def test_timeline_setter_updates_sides():
    config = LayoutConfig()
    config.timeline = {"sides": DOWN, "node_spacing": 0.6, "level_spacing": 0.4}

    assert config.sides == (LayoutDirection.TopToBottom,)
    assert config.node_spacing == 0.6


def test_timeline_setter_rejects_bad_side():
    config = LayoutConfig()

    with pytest.raises(ValueError):
        config.timeline = {"sides": (LEFT,)}

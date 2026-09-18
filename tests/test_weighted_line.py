# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the weighted_line module."""

import pytest
from manim import Line, LEFT, RIGHT, UP, DOWN, BLUE, RED

from manim_extensions.weighted_line import WeightedLine


class TestWeightedLine:
    def test_basic_construction_with_weight(self):
        """WeightedLine should be created with a weight label."""
        wl = WeightedLine(LEFT, RIGHT, weight=5)
        assert isinstance(wl, Line)
        assert wl.weight == 5

    def test_construction_without_weight(self):
        """WeightedLine should work without a weight (no label added)."""
        wl = WeightedLine(LEFT, RIGHT)
        assert isinstance(wl, Line)
        assert wl.weight is None

    def test_weight_alpha_parameter(self):
        """WeightedLine should respect the weight_alpha parameter."""
        wl = WeightedLine(LEFT, RIGHT, weight=3, weight_alpha=0.3)
        assert isinstance(wl, Line)
        assert wl.alpha == 0.3

    def test_custom_weight_config(self):
        """WeightedLine should accept custom weight_config."""
        wl = WeightedLine(
            LEFT * 2, RIGHT * 2,
            weight="test",
            weight_config={"color": BLUE, "font_size": 20},
        )
        assert isinstance(wl, Line)
        assert wl.weight_config["color"] == BLUE

    def test_add_bg_false(self):
        """WeightedLine should not add background when add_bg=False."""
        wl = WeightedLine(LEFT, RIGHT, weight=42, add_bg=False)
        assert isinstance(wl, Line)
        assert wl.add_bg is False

    def test_zero_weight(self):
        """WeightedLine should handle weight=0 correctly."""
        wl = WeightedLine(LEFT, RIGHT, weight=0)
        assert isinstance(wl, Line)
        assert wl.weight == 0

    def test_string_weight(self):
        """WeightedLine should accept string weights."""
        wl = WeightedLine(LEFT, RIGHT, weight="∞")
        assert isinstance(wl, Line)
        assert wl.weight == "∞"

    def test_custom_bg_config(self):
        """WeightedLine should accept custom bg_config."""
        wl = WeightedLine(
            LEFT, RIGHT,
            weight=10,
            bg_config={"color": RED, "opacity": 0.5},
        )
        assert isinstance(wl, Line)
        assert wl.bg_config["color"] == RED

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for generic economics supply/demand diagram shifting."""

import pytest

from manim_extensions.economics.base import EconDiagram


@pytest.fixture()
def diagram():
    d = EconDiagram(
        x_label="Q",
        y_label="P",
        x_range=[0, 10, 1],
        y_range=[0, 10, 1],
    )
    d.add_curve("demand", lambda q: 10 - q, [0, 10], "blue", "D")
    d.add_curve("supply", lambda q: q, [0, 10], "red", "S")
    d.mark_equilibrium("supply", "demand", label_x="Q1", label_y="P1")
    return d


def test_equilibrium_coordinates(diagram):
    coords = diagram._get_eq_coords()

    assert coords is not None


def test_shift_curve_animation(diagram):
    animation = diagram.get_shift_animation(
        "demand", lambda q: 10 - q, run_time=0.2, show_arrows=True
    )

    assert animation is not None


def test_clear_arrows_returns_fade_out(diagram):
    diagram.get_shift_animation("demand", lambda q: 9 - q, run_time=0.2, show_arrows=True)

    animation = diagram.clear_arrows()

    assert animation is not None

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the Solow growth model diagram."""

import pytest

from manim_extensions.economics.solow import SolowDiagram


@pytest.fixture(scope="module")
def diagram():
    return SolowDiagram()


def test_default_curves(diagram):
    assert diagram.production is not None
    assert diagram.savings is not None
    assert diagram.breakeven is not None


def test_steady_state(diagram):
    value = diagram._steady_state_k()

    assert value > 0


@pytest.mark.parametrize("s", [0.2, 0.45])
def test_shift_savings(diagram, s):
    animation = diagram.shift_savings(s=s, run_time=0.3, show_arrows=True)

    assert animation is not None


@pytest.mark.parametrize("delta", [0.05, 0.2])
def test_shift_breakeven(diagram, delta):
    animation = diagram.shift_breakeven(delta=delta, run_time=0.3, show_arrows=True)

    assert animation is not None


def test_increase_and_decrease_savings(diagram):
    up = diagram.increase_savings(0.4)
    down = diagram.decrease_savings(0.2)

    assert isinstance(up, list)
    assert isinstance(down, list)


def test_population_growth(diagram):
    animations = diagram.population_growth(0.1, show_arrows=True)

    assert isinstance(animations, list)


def test_increase_depreciation(diagram):
    animations = diagram.increase_depreciation(0.15)

    assert isinstance(animations, list)

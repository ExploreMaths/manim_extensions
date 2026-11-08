# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the capital-share and golden-rule helpers of the Solow diagram."""

import pytest

from manim_extensions.economics.solow import SolowDiagram


@pytest.fixture()
def diagram():
    return SolowDiagram()


def test_golden_rule_capital_is_above_steady_state(diagram):
    assert diagram._golden_rule_k() > diagram._steady_state_k()


def test_shares_can_be_shown_and_hidden(diagram):
    shown = diagram.show_shares()
    hidden = diagram.hide_shares()

    assert shown is not None
    assert hidden is not None


def test_shares_can_be_shown_at_a_given_capital_level(diagram):
    animation = diagram.show_shares(1.0)

    assert animation is not None


def test_shares_animate_along_the_curve(diagram):
    animation = diagram.animate_shares_along(0.2, 2.0)

    assert animation is not None


def test_golden_rule_can_be_shown_and_hidden(diagram):
    shown = diagram.show_golden_rule()
    hidden = diagram.hide_golden_rule()

    assert shown is not None
    assert hidden is not None

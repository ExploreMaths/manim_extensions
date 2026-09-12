# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the economics diagrams.

Includes the regression for ``ADASDiagram(numbered_eq=True)`` (9a12ddc),
where the unhandled kwarg leaked through **kwargs into Mobject.__init__.
"""

from manim import Animation
import pytest

from manim_extensions.economics import (
    ADASDiagram,
    ISLMDiagram,
    LinkedISLM_ADAS,
    SolowDiagram,
    SupplyDemandDiagram,
)


def _assert_animation_list(value):
    if isinstance(value, list):
        for anim in value:
            assert isinstance(anim, Animation)
    else:
        assert isinstance(value, Animation)


class TestISLMDiagram:
    def test_construct_defaults(self):
        diagram = ISLMDiagram()
        assert diagram.get_axes() is not None

    def test_construct_numbered_eq(self):
        diagram = ISLMDiagram(numbered_eq=True)
        assert diagram is not None

    def test_shift_is_returns_animations(self):
        diagram = ISLMDiagram()
        _assert_animation_list(diagram.shift_is(a=12))

    def test_shift_lm_returns_animations(self):
        diagram = ISLMDiagram()
        _assert_animation_list(diagram.shift_lm(ms=3))


class TestADASDiagram:
    def test_construct_defaults(self):
        diagram = ADASDiagram()
        assert diagram.get_axes() is not None

    def test_construct_numbered_eq(self):
        # Regression: numbered_eq must be consumed by ADASDiagram itself.
        diagram = ADASDiagram(numbered_eq=True)
        assert diagram is not None

    def test_positive_demand_shock(self):
        diagram = ADASDiagram()
        _assert_animation_list(diagram.positive_demand_shock(m=30))

    def test_negative_demand_shock(self):
        diagram = ADASDiagram()
        _assert_animation_list(diagram.negative_demand_shock(m=15))

    def test_positive_supply_shock(self):
        diagram = ADASDiagram(sras_slope=0.5)
        _assert_animation_list(diagram.positive_supply_shock(sras_price=3))

    def test_sras_only(self):
        diagram = ADASDiagram(sras_only=True)
        assert diagram is not None

    def test_lras_only(self):
        diagram = ADASDiagram(lras_only=True)
        assert diagram is not None

    def test_both_only_raises(self):
        with pytest.raises(ValueError):
            ADASDiagram(sras_only=True, lras_only=True)


class TestLinkedISLMADAS:
    def test_construct_with_numbered_eq(self):
        # Regression: LinkedISLM_ADAS forwards numbered_eq to both diagrams.
        linked = LinkedISLM_ADAS(numbered_eq=True, show_arrows=True)
        assert linked.is_lm is not None
        assert linked.ad_as is not None

    def test_monetary_expansion(self):
        linked = LinkedISLM_ADAS()
        _assert_animation_list(linked.monetary_expansion(ms=3))

    def test_monetary_contraction(self):
        linked = LinkedISLM_ADAS()
        _assert_animation_list(linked.monetary_contraction(ms=1))

    def test_fiscal_expansion(self):
        linked = LinkedISLM_ADAS()
        _assert_animation_list(linked.fiscal_expansion(a=12))

    def test_fiscal_contraction(self):
        linked = LinkedISLM_ADAS()
        _assert_animation_list(linked.fiscal_contraction(a=7))


class TestSolowDiagram:
    def test_construct_defaults(self):
        diagram = SolowDiagram()
        assert diagram is not None

    def test_construct_numbered_eq(self):
        diagram = SolowDiagram(numbered_eq=True)
        assert diagram is not None


class TestSupplyDemandDiagram:
    def test_construct_defaults(self):
        diagram = SupplyDemandDiagram()
        assert diagram is not None

    def test_construct_with_functions(self):
        diagram = SupplyDemandDiagram(
            demand_func=lambda x: 10 - x,
            supply_func=lambda x: x,
        )
        assert diagram is not None

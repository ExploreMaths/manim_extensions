# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Solow growth model diagram for Manim.

This module provides the Solow growth model diagram.

"""

import numpy as np
from manim import (
    BLUE, GREEN, ORANGE, PURPLE, RED, RIGHT, YELLOW,
    AnimationGroup, Brace, DashedLine, FadeIn, FadeOut,
    Line, ReplacementTransform, Text, UpdateFromAlphaFunc, VGroup,
)

from .base import EconDiagram


class SolowDiagram(EconDiagram):
    """Solow growth model diagram.

    Production function: y = k^α
    Savings/investment: sf(k) = s·k^α
    Break-even investment: (δ + n + g)·k

    Steady state where sf(k*) = (δ + n + g)·k*.

    Parameters:
        s: Savings rate (default 0.3)
        alpha: Capital share / production function exponent (default 0.5)
        delta: Depreciation rate (default 0.05)
        n: Population growth rate (default 0.02)
        g: Technological growth rate (default 0.03)
    """

    def __init__(
        self,
        s=0.3,
        alpha=0.5,
        delta=0.1,
        n=0.05,
        g=0.05,
        show_equilibrium=True,
        numbered_eq=False,
        show_production=True,
        **kwargs,
    ):
        kwargs.setdefault("x_range", [0, 10, 1])
        kwargs.setdefault("y_range", [0, 4, 1])
        super().__init__(x_label="k", y_label="y", **kwargs)

        self._s = s
        self._alpha = alpha
        self._delta = delta
        self._n = n
        self._g = g

        if show_production:
            prod_func = self._make_prod_func(alpha)
            self.production = self.add_curve(
                "production", prod_func, x_range=[0.01, 10],
                color=GREEN, label_text="f(k)",
            )

        savings_func = self._make_savings_func(s, alpha)
        breakeven_func = self._make_breakeven_func(delta, n, g)

        self.savings = self.add_curve(
            "savings", savings_func, x_range=[0.01, 10],
            color=BLUE, label_text="sf(k)",
        )
        self.breakeven = self.add_curve(
            "breakeven", breakeven_func, x_range=[0, 10],
            color=RED, label_text="(δ+n+g)k",
        )

        if show_equilibrium:
            self.mark_equilibrium("savings", "breakeven",
                                  label_x="k", label_y="y",
                                  numbered=numbered_eq)

    @staticmethod
    def _make_prod_func(alpha):
        """y = k^α"""
        return lambda k: k ** alpha

    @staticmethod
    def _make_savings_func(s, alpha):
        """sf(k) = s·k^α"""
        return lambda k: s * (k ** alpha)

    @staticmethod
    def _make_breakeven_func(delta, n, g):
        """(δ + n + g)·k"""
        rate = delta + n + g
        return lambda k: rate * k

    @property
    def _shares_visible(self):
        return hasattr(self, '_shares_group') and self._shares_group is not None

    def _shift_with_shares(self, curve_anim, run_time):
        """Bundle a curve shift with a shares update if shares are visible."""
        if not self._shares_visible:
            return curve_anim

        new_group = self._build_shares(
            self._steady_state_k(),
            self._shares_c_color, self._shares_i_color,
        )
        old = self._shares_group
        self._shares_group = new_group
        shares_anim = ReplacementTransform(old, new_group, run_time=run_time)
        return AnimationGroup(curve_anim, shares_anim)

    def shift_savings(self, s=None, run_time=1, show_arrows=False):
        """Animate savings curve shifting due to change in savings rate.

        If shares are visible, they update automatically.
        """
        self._s = s if s is not None else self._s
        new_func = self._make_savings_func(self._s, self._alpha)
        anim = self.get_shift_animation(
            "savings", new_func, run_time=run_time, show_arrows=show_arrows,
        )
        return self._shift_with_shares(anim, run_time)

    def shift_breakeven(self, delta=None, n=None, g=None, run_time=1,
                        show_arrows=False):
        """Animate break-even line shifting due to changes in δ, n, or g.

        If shares are visible, they update automatically.
        """
        self._delta = delta if delta is not None else self._delta
        self._n = n if n is not None else self._n
        self._g = g if g is not None else self._g
        new_func = self._make_breakeven_func(self._delta, self._n, self._g)
        anim = self.get_shift_animation(
            "breakeven", new_func, run_time=run_time, show_arrows=show_arrows,
        )
        return self._shift_with_shares(anim, run_time)

    # ---- Common shocks ----

    def increase_savings(self, s, show_arrows=False):
        """Higher savings rate → sf(k) shifts up → higher steady-state k."""
        return [self.shift_savings(s=s, show_arrows=show_arrows)]

    def decrease_savings(self, s, show_arrows=False):
        """Lower savings rate → sf(k) shifts down → lower steady-state k."""
        return [self.shift_savings(s=s, show_arrows=show_arrows)]

    def population_growth(self, n, show_arrows=False):
        """Higher population growth → break-even steeper → lower steady-state k."""
        return [self.shift_breakeven(n=n, show_arrows=show_arrows)]

    def increase_depreciation(self, delta, show_arrows=False):
        """Higher depreciation → break-even steeper → lower steady-state k."""
        return [self.shift_breakeven(delta=delta, show_arrows=show_arrows)]

    # ---- Consumption / Investment shares ----

    def _steady_state_k(self):
        """Compute steady-state capital: sf(k*) = (δ+n+g)k*."""
        from .base import find_intersection
        sf = self._make_savings_func(self._s, self._alpha)
        bf = self._make_breakeven_func(self._delta, self._n, self._g)
        return find_intersection(sf, bf, self.axes.x_range)

    def _build_shares(self, k, c_color=ORANGE, i_color=YELLOW):
        """Build the share annotation VGroup at capital level k."""
        prod = self._make_prod_func(self._alpha)
        sav = self._make_savings_func(self._s, self._alpha)

        y_total = prod(k)
        y_invest = sav(k)

        p_top = self.axes.c2p(k, y_total)
        p_mid = self.axes.c2p(k, y_invest)
        p_bot = self.axes.c2p(k, 0)

        stem = DashedLine(p_bot, p_top, color="#888888", dash_length=0.06)

        i_line = Line(p_bot, p_mid)
        i_brace = Brace(i_line, direction=RIGHT, buff=0.05, color=i_color)
        i_label = Text("i", font_size=16, color=i_color)
        i_label.next_to(i_brace, RIGHT, buff=0.1)

        c_line = Line(p_mid, p_top)
        c_brace = Brace(c_line, direction=RIGHT, buff=0.05, color=c_color)
        c_label = Text("c", font_size=16, color=c_color)
        c_label.next_to(c_brace, RIGHT, buff=0.1)

        return VGroup(stem, i_brace, i_label, c_brace, c_label)

    def show_shares(self, k=None, c_color=ORANGE, i_color=YELLOW, run_time=1):
        """Show or update consumption/investment share annotations.

        Call again after a shift to animate the braces to the new position.

        Parameters:
            k: Capital level. Defaults to current steady-state k*.
            c_color: Color for consumption brace/label.
            i_color: Color for investment brace/label.
        """
        if k is None:
            k = self._steady_state_k()
            if k is None:
                return None

        self._shares_c_color = c_color
        self._shares_i_color = i_color
        new_group = self._build_shares(k, c_color, i_color)

        if hasattr(self, '_shares_group') and self._shares_group is not None:
            old = self._shares_group
            self._shares_group = new_group
            return ReplacementTransform(old, new_group, run_time=run_time)

        self._shares_group = new_group
        return FadeIn(new_group, run_time=run_time)

    def hide_shares(self):
        """Return a FadeOut animation to remove the share annotations."""
        if hasattr(self, '_shares_group') and self._shares_group is not None:
            old = self._shares_group
            self._shares_group = None
            return FadeOut(old)
        return None

    def animate_shares_along(self, k_start, k_end,
                             c_color=ORANGE, i_color=YELLOW, run_time=3):
        """Animate the c/i share braces sliding from k_start to k_end.

        Shows how the consumption/investment split changes at different
        capital levels along the production function.
        """
        self._shares_c_color = c_color
        self._shares_i_color = i_color

        # Build initial group
        initial = self._build_shares(k_start, c_color, i_color)
        if not self._shares_visible:
            self._shares_group = initial

        container = self._shares_group

        def updater(mob, alpha):
            k = k_start + (k_end - k_start) * alpha
            new = self._build_shares(k, c_color, i_color)
            mob.become(new)

        anim = UpdateFromAlphaFunc(container, updater, run_time=run_time)
        return anim

    # ---- Golden rule ----

    def _golden_rule_k(self):
        """Compute golden-rule capital: MPK = δ+n+g.

        f'(k) = α·k^(α-1) = δ+n+g  →  k_gold = (α / (δ+n+g))^(1/(1-α))
        """
        rate = self._delta + self._n + self._g
        return (self._alpha / rate) ** (1 / (1 - self._alpha))

    def show_golden_rule(self, color=PURPLE, run_time=1):
        """Mark the golden-rule capital level where consumption is maximized.

        Draws a vertical dashed line at k_gold with a label. The golden rule
        is where MPK = δ+n+g, giving the savings rate that maximizes
        steady-state consumption.

        Returns a FadeIn animation.
        """
        k_gold = self._golden_rule_k()
        s_gold = (self._delta + self._n + self._g) * k_gold / (k_gold ** self._alpha)

        y_min = self.axes.y_range[0]
        y_max = self.axes.y_range[1]
        gold_line = DashedLine(
            self.axes.c2p(k_gold, y_min),
            self.axes.c2p(k_gold, y_max),
            color=color, dash_length=0.08,
        )
        gold_label = Text(f"k*gold", font_size=16, color=color)
        gold_label.next_to(gold_line, RIGHT + np.array([0, 0.5, 0]), buff=0.1)

        s_text = Text(f"s = {s_gold:.2f}", font_size=14, color=color)
        s_text.next_to(gold_label, RIGHT, buff=0.15)

        self._golden_group = VGroup(gold_line, gold_label, s_text)
        return FadeIn(self._golden_group, run_time=run_time)

    def hide_golden_rule(self):
        """Return a FadeOut animation to remove the golden-rule marker."""
        if hasattr(self, '_golden_group') and self._golden_group is not None:
            old = self._golden_group
            self._golden_group = None
            return FadeOut(old)
        return None
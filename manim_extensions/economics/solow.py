# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Solow growth model diagram for Manim.

This module provides the Solow growth model diagram.

"""

from manim import (
    AnimationGroup,
    BLUE,
    Brace,
    DashedLine,
    FadeIn,
    FadeOut,
    GREEN,
    Line,
    ManimColor,
    Mobject,
    ORANGE,
    PURPLE,
    RED,
    RIGHT,
    ReplacementTransform,
    Text,
    UpdateFromAlphaFunc,
    VGroup,
    YELLOW,
)
from typing import Any, Optional

import numpy as np

from .base import EconDiagram


class SolowDiagram(EconDiagram):
    """Solow growth model diagram.

    Production function: :math:`y = k^{\\alpha}`
    Savings/investment: :math:`sf(k) = s \\cdot k^{\\alpha}`
    Break-even investment: :math:`(\\delta + n + g) \\cdot k`

    Steady state where :math:`sf(k^*) = (\\delta + n + g) \\cdot k^*`.

    Parameters
    ----------
    s
        Savings rate.
    alpha
        Capital share / production function exponent.
    delta
        Depreciation rate.
    n
        Population growth rate.
    g
        Technological growth rate.
    show_equilibrium
        If True, mark the steady-state equilibrium.
    numbered_eq
        If True, label equilibria with subscripts that increment on each shift.
    show_production
        If True, also draw the production function f(k).
    **kwargs
        Additional keyword arguments passed to :class:`~manim_extensions.economics.base.EconDiagram`.

    Examples
    --------
    .. manim:: SolowDiagramDocExample

       from manim import *
       from manim_extensions.economics import SolowDiagram

       class SolowDiagramDocExample(Scene):
           def construct(self):
               diagram = SolowDiagram(s=0.3, alpha=0.5, delta=0.1,
                                      n=0.05, g=0.05, show_production=True)
               self.play(Create(diagram))
               self.wait()

               label = Text("Increase in savings rate: s up",
                            font_size=28).to_edge(UP)
               self.play(Write(label))
               for anim in diagram.increase_savings(s=0.5, show_arrows=True):
                   self.play(anim)
                   self.wait(0.5)
               self.play(diagram.show_shares())
               self.wait()
    """

    def __init__(
        self,
        s: float = 0.3,
        alpha: float = 0.5,
        delta: float = 0.1,
        n: float = 0.05,
        g: float = 0.05,
        show_equilibrium: bool = True,
        numbered_eq: bool = False,
        show_production: bool = True,
        **kwargs,
    ):
        """Initializes the Solow growth model diagram with production, savings, and breakeven curves."""
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
    def _make_prod_func(alpha: Any):
        """:math:`y = k^\\alpha`"""
        return lambda k: k ** alpha

    @staticmethod
    def _make_savings_func(s: Any, alpha: Any):
        """:math:`sf(k) = s \\cdot k^\\alpha`"""
        return lambda k: s * (k ** alpha)

    @staticmethod
    def _make_breakeven_func(delta: Any, n: Optional[np.ndarray], g: Any):
        """:math:`(\\delta + n + g) \\cdot k`"""
        rate = delta + n + g
        return lambda k: rate * k

    @property
    def _shares_visible(self):
        return hasattr(self, '_shares_group') and self._shares_group is not None

    def _shift_with_shares(self, curve_anim: Any, run_time: float):
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

    def shift_savings(self, s: Optional[Any]=None, run_time: float = 1, show_arrows: bool = False) -> Any:
        """Animate savings curve shifting due to change in savings rate.

        Parameters
        ----------
        s
            New savings rate. If ``None``, keeps the current value.
            
        run_time
            Duration of the shift animation. 
        show_arrows
            If True, draw arrows on the axes showing the direction of
            equilibrium change. 

            If shares are visible, they update automatically.

        Returns
        -------
            The curve-shift animation, together with the share update
            if shares are visible.
        """
        self._s = s if s is not None else self._s
        new_func = self._make_savings_func(self._s, self._alpha)
        anim = self.get_shift_animation(
            "savings", new_func, run_time=run_time, show_arrows=show_arrows,
        )
        return self._shift_with_shares(anim, run_time)

    def shift_breakeven(self, delta: Optional[Any]=None, n: Optional[Any]=None, g: Optional[Any]=None, run_time: float = 1,
                        show_arrows: bool = False) -> Any:
        """Animate break-even line shifting due to changes in :math:`\\delta`, n, or g.

        Parameters
        ----------
        delta
            New depreciation rate. If ``None``, keeps the current value.
            
        n
            New population growth rate. If ``None``, keeps the current
            value. 
        g
            New technological growth rate. If ``None``, keeps the current
            value. 
        run_time
            Duration of the shift animation. 
        show_arrows
            If True, draw arrows on the axes showing the direction of
            equilibrium change. 

            If shares are visible, they update automatically.

        Returns
        -------
            The curve-shift animation, together with the share update
            if shares are visible.
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

    def increase_savings(self, s: Any, show_arrows: bool = False) -> list[AnimationGroup]:
        """Higher savings rate → sf(k) shifts up → higher steady-state k.

        Parameters
        ----------
        s
            New savings rate (higher than current).
        show_arrows
            If True, draw arrows on the axes showing the direction of
            equilibrium change. 

        Returns
        -------
        :class:`~typing.List` of :class:`~manim.animation.animation.Animation`
            A list of animations to play in sequence.
        """
        return [self.shift_savings(s=s, show_arrows=show_arrows)]

    def decrease_savings(self, s: Any, show_arrows: bool = False) -> list[AnimationGroup]:
        """Lower savings rate → sf(k) shifts down → lower steady-state k.

        Parameters
        ----------
        s
            New savings rate (lower than current).
        show_arrows
            If True, draw arrows on the axes showing the direction of
            equilibrium change. 

        Returns
        -------
        :class:`~typing.List` of :class:`~manim.animation.animation.Animation`
            A list of animations to play in sequence.
        """
        return [self.shift_savings(s=s, show_arrows=show_arrows)]

    def population_growth(self, n: Optional[np.ndarray], show_arrows: bool = False) -> list[AnimationGroup]:
        """Higher population growth → break-even steeper → lower steady-state k.

        Parameters
        ----------
        n
            New population growth rate (higher than current).
        show_arrows
            If True, draw arrows on the axes showing the direction of
            equilibrium change. 

        Returns
        -------
        :class:`~typing.List` of :class:`~manim.animation.animation.Animation`
            A list of animations to play in sequence.
        """
        return [self.shift_breakeven(n=n, show_arrows=show_arrows)]

    def increase_depreciation(self, delta: Any, show_arrows: bool = False) -> list[AnimationGroup]:
        """Higher depreciation → break-even steeper → lower steady-state k.

        Parameters
        ----------
        delta
            New depreciation rate (higher than current).
        show_arrows
            If True, draw arrows on the axes showing the direction of
            equilibrium change. 

        Returns
        -------
        :class:`~typing.List` of :class:`~manim.animation.animation.Animation`
            A list of animations to play in sequence.
        """
        return [self.shift_breakeven(delta=delta, show_arrows=show_arrows)]

    # ---- Consumption / Investment shares ----

    def _steady_state_k(self):
        """Compute steady-state capital: :math:`sf(k^*) = (\\delta+n+g)k^*`."""
        from .base import find_intersection
        sf = self._make_savings_func(self._s, self._alpha)
        bf = self._make_breakeven_func(self._delta, self._n, self._g)
        return find_intersection(sf, bf, self.axes.x_range)

    def _build_shares(self, k: Any, c_color: ManimColor = ORANGE, i_color: ManimColor = YELLOW):
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

    def show_shares(self, k: Optional[Any]=None, c_color: ManimColor = ORANGE, i_color: ManimColor = YELLOW, run_time: float = 1) -> FadeIn | ReplacementTransform | None:
        """Show or update consumption/investment share annotations.

        Call again after a shift to animate the braces to the new position.

        Parameters
        ----------
        k
            Capital level. *.
        c_color
            Color for consumption brace/label. 
        i_color
            Color for investment brace/label. 
        run_time
            Duration of the animation. 

        Returns
        -------
        :class:`~manim.animation.fading.FadeIn` or :class:`~manim.animation.transform.ReplacementTransform` or ``None``
            The animation revealing the consumption/investment shares, or
            ``None`` if there is no steady-state capital.
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

    def hide_shares(self) -> FadeOut | None:
        """Remove the share annotations.

        Returns
        -------
        :class:`~manim.animation.fading.FadeOut` or ``None``
            A FadeOut animation removing the shares, or ``None`` if the
            shares are not visible.
        """
        if hasattr(self, '_shares_group') and self._shares_group is not None:
            old = self._shares_group
            self._shares_group = None
            return FadeOut(old)
        return None

    def animate_shares_along(self, k_start: Any, k_end: Any,
                             c_color: ManimColor = ORANGE, i_color: ManimColor = YELLOW, run_time: float = 3) -> UpdateFromAlphaFunc:
        """Animate the c/i share braces sliding from ``k_start`` to ``k_end``.

        Parameters
        ----------
        k_start
            Capital level where the animation starts.
        k_end
            Capital level where the animation ends.
        c_color
            Color for consumption brace/label. 
        i_color
            Color for investment brace/label. 
        run_time
            Duration of the animation. 

        Returns
        -------
        :class:`~manim.animation.updaters.update.UpdateFromAlphaFunc`
            The animation sliding the consumption/investment shares along
            the capital axis.
        """
        self._shares_c_color = c_color
        self._shares_i_color = i_color

        # Build initial group
        initial = self._build_shares(k_start, c_color, i_color)
        if not self._shares_visible:
            self._shares_group = initial

        container = self._shares_group

        def updater(mob: Mobject, alpha: Any):
            """Rebuilds the consumption/investment shares mobject at capital level k."""
            k = k_start + (k_end - k_start) * alpha
            new = self._build_shares(k, c_color, i_color)
            mob.become(new)

        anim = UpdateFromAlphaFunc(container, updater, run_time=run_time)
        return anim

    # ---- Golden rule ----

    def _golden_rule_k(self):
        """Compute golden-rule capital: :math:`MPK = \\delta + n + g`.

        :math:`f'(k) = \\alpha k^{\\alpha-1} = \\delta+n+g \\to k_{\\mathrm{gold}} = (\\alpha/(\\delta+n+g))^{1/(1-\\alpha)}`
        """
        rate = self._delta + self._n + self._g
        return (self._alpha / rate) ** (1 / (1 - self._alpha))

    def show_golden_rule(self, color: ManimColor = PURPLE, run_time: float = 1) -> FadeIn:
        """Mark the golden-rule capital level where consumption is maximized.

        Parameters
        ----------
        color
            Color of the golden-rule line and labels. 
        run_time
            Duration of the FadeIn animation. 

            Draws a vertical dashed line at ``k_gold`` with a label. The golden rule
            is where :math:`MPK = \\delta + n + g`, giving the savings rate that
            maximizes steady-state consumption.

        Returns
        -------
        :class:`~manim.animation.fading.FadeIn`
            A FadeIn animation of the golden-rule line and labels.
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

    def hide_golden_rule(self) -> FadeOut | None:
        """Remove the golden-rule marker.

        Returns
        -------
        :class:`~manim.animation.fading.FadeOut` or ``None``
            A FadeOut animation removing the marker, or ``None`` if the
            marker is not present.
        """
        if hasattr(self, '_golden_group') and self._golden_group is not None:
            old = self._golden_group
            self._golden_group = None
            return FadeOut(old)
        return None
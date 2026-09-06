# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Linked IS-LM and AD-AS diagrams for Manim.

This module provides linked IS-LM and AD-AS diagrams for policy analysis.

"""


from manim import *
from .ad_as import ADASDiagram
from .is_lm import ISLMDiagram


class LinkedISLM_ADAS(VGroup):
    """Side-by-side IS-LM and AD-AS diagrams with linked policy shifts.

    A policy change (monetary or fiscal) shifts curves in both diagrams
    simultaneously:

      - Monetary expansion: LM right + AD right
      - Fiscal expansion:   IS right + AD right

    Parameters
    ----------
    is_lm_kwargs
        Extra keyword arguments forwarded to :class:`~manim_extensions.economics.is_lm.ISLMDiagram`.
    ad_as_kwargs
        Extra keyword arguments forwarded to :class:`~manim_extensions.economics.ad_as.ADASDiagram`.
    spacing
        Horizontal gap between the two diagrams (default 1.0).
    numbered_eq
        Use numbered equilibrium labels in both diagrams.
    show_arrows
        Show axis arrows on shifts in both diagrams.
    **kwargs
        Additional keyword arguments passed to :class:`~manim.mobject.types.vectorized_mobject.VGroup`.

    Examples
    --------
    .. manim:: LinkedISLMADASDocExample

       from manim import *
       from manim_extensions.economics import LinkedISLM_ADAS

       class LinkedISLMADASDocExample(Scene):
           def construct(self):
               linked = LinkedISLM_ADAS(numbered_eq=True, show_arrows=True)
               self.play(Create(linked))
               self.wait()

               label = Text("Monetary expansion: Ms up",
                            font_size=28).to_edge(UP)
               self.play(Write(label))
               for anim in linked.monetary_expansion(ms=5, m=30):
                   self.play(anim)
                   self.wait(0.5)
    """

    def __init__(
        self,
        is_lm_kwargs=None,
        ad_as_kwargs=None,
        spacing=1.0,
        numbered_eq=False,
        show_arrows=False,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self._show_arrows = show_arrows

        is_lm_kw = dict(
            x_length=4, y_length=3,
            numbered_eq=numbered_eq,
        )
        if is_lm_kwargs:
            is_lm_kw.update(is_lm_kwargs)

        ad_as_kw = dict(
            x_length=4, y_length=3,
            numbered_eq=numbered_eq,
        )
        if ad_as_kwargs:
            ad_as_kw.update(ad_as_kwargs)

        self.is_lm = ISLMDiagram(**is_lm_kw)
        self.ad_as = ADASDiagram(**ad_as_kw)

        self.ad_as.next_to(self.is_lm, RIGHT, buff=spacing)

        self.add(self.is_lm, self.ad_as)
        self.center()

    # ---- Monetary policy ----

    def monetary_expansion(self, ms, m=None, v=None):
        """Monetary expansion: LM shifts right, AD shifts right.

        Parameters:
            ms: New money supply for IS-LM (shifts LM).
            m: New money supply for AD-AS (shifts AD). If None, uses ms * 4.
            v: New velocity for AD-AS. If None, unchanged.
        """
        ad_m = m if m is not None else ms * 4
        arrows = self._show_arrows
        return [AnimationGroup(
            self.is_lm.shift_lm(ms=ms, show_arrows=arrows),
            self.ad_as.shift_ad(m=ad_m, v=v, show_arrows=arrows),
        )]

    def monetary_contraction(self, ms, m=None, v=None):
        """Monetary contraction: LM shifts left, AD shifts left."""
        ad_m = m if m is not None else ms * 4
        arrows = self._show_arrows
        return [AnimationGroup(
            self.is_lm.shift_lm(ms=ms, show_arrows=arrows),
            self.ad_as.shift_ad(m=ad_m, v=v, show_arrows=arrows),
        )]

    # ---- Fiscal policy ----

    def fiscal_expansion(self, a, m=None, v=None):
        """Fiscal expansion: IS shifts right, AD shifts right.

        Parameters:
            a: New autonomous spending for IS-LM (shifts IS).
            m: New money supply for AD-AS (shifts AD). If None, uses a * 2.
            v: New velocity for AD-AS. If None, unchanged.
        """
        ad_m = m if m is not None else a * 2
        arrows = self._show_arrows
        return [AnimationGroup(
            self.is_lm.shift_is(a=a, show_arrows=arrows),
            self.ad_as.shift_ad(m=ad_m, v=v, show_arrows=arrows),
        )]

    def fiscal_contraction(self, a, m=None, v=None):
        """Fiscal contraction: IS shifts left, AD shifts left."""
        ad_m = m if m is not None else a * 2
        arrows = self._show_arrows
        return [AnimationGroup(
            self.is_lm.shift_is(a=a, show_arrows=arrows),
            self.ad_as.shift_ad(m=ad_m, v=v, show_arrows=arrows),
        )]

    # ---- Supply shocks (AD-AS only, IS-LM unaffected) ----

    def adverse_supply_shock(self, sras_price, long_run=True):
        """Adverse supply shock in AD-AS (IS-LM unchanged in short run)."""
        return self.ad_as.adverse_supply_shock(
            sras_price, long_run=long_run, show_arrows=self._show_arrows
        )

    def positive_supply_shock(self, sras_price, long_run=True):
        """Positive supply shock in AD-AS (IS-LM unchanged in short run)."""
        return self.ad_as.positive_supply_shock(
            sras_price, long_run=long_run, show_arrows=self._show_arrows
        )
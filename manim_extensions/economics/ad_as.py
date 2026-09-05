# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""AD-AS diagram for Manim.

This module provides the Aggregate Demand-Aggregate Supply diagram.

"""


from manim import *
from .base import EconDiagram

# Default long-run adjustment duration (seconds)
_LR_RUN_TIME = 2


class ADASDiagram(EconDiagram):
    """Aggregate Demand — Aggregate Supply diagram.

    AD is derived from the quantity theory of money: MV = PY, so P = MV/Y.

    SRAS comes in two flavours controlled by ``sras_slope``:

    * ``sras_slope=None`` (default) — flat/horizontal Keynesian SRAS at
      ``sras_price``.
    * ``sras_slope=<positive number>`` — upward-sloping SRAS using the
      Mankiw formulation::

          P = Pᵉ + slope · (Y − Ȳ)

      where *Pᵉ* is the expected price level (``sras_price``), *Ȳ* is
      potential output (``lras_y``), and *slope* captures the cost
      structure ``(1−s)a/s``.  Shifts in SRAS correspond to changes in
      *Pᵉ*: when firms revise expectations the curve shifts up/down
      while keeping the same slope.

    LRAS is a vertical line at potential output.

    Parameters
    ----------
    m
        Money supply (default 20).
    v
        Velocity of money (default 1).
    sras_price
        Short-run price level / expected price Pᵉ (default 4).
    sras_slope
        SRAS slope.  ``None`` → flat.  Positive → upward-sloping
        ``P = Pᵉ + slope·(Y − Ȳ)``.
    lras_y
        Potential output / natural rate of output (default 5).
    show_equilibrium
        If True (default), mark the AD–SRAS intersection as the equilibrium.
    sras_only
        If True, draw only the SRAS curve (no LRAS line).
    lras_only
        If True, draw only the LRAS line (no SRAS curve).
    **kwargs
        Additional keyword arguments passed to :class:`~manim_extensions.economics.base.EconDiagram`.
    """

    def __init__(
        self,
        m=20,
        v=1,
        sras_price=4,
        sras_slope=None,
        lras_y=5,
        show_equilibrium=True,
        sras_only=False,
        lras_only=False,
        **kwargs,
    ):
        if sras_only and lras_only:
            raise ValueError("sras_only and lras_only cannot both be True")

        super().__init__(x_label="Y", y_label="P", **kwargs)

        self._m = m
        self._v = v
        self._sras_price = sras_price
        self._sras_slope = sras_slope
        self._lras_y = lras_y

        ad_func = self._make_ad_func(m, v)
        sras_func = self._make_sras_func(sras_price, sras_slope, lras_y)

        y_max = kwargs.get("y_range", [0, 10, 1])[1]
        ad_x_min = self._ad_x_min(m, v, y_max)
        self.ad = self.add_curve(
            "ad", ad_func, x_range=[ad_x_min, 10], color=BLUE, label_text="AD"
        )

        if not lras_only:
            self.sras = self.add_curve(
                "sras", sras_func, x_range=[0, 10], color=RED, label_text="SRAS"
            )

        if not sras_only:
            self.lras = self.add_vertical_line(
                "lras", lras_y, color=GREEN, label_text="LRAS"
            )

        if show_equilibrium and not lras_only:
            self.mark_equilibrium("ad", "sras", label_x="Y*", label_y="P*")

    @staticmethod
    def _make_ad_func(m, v):
        """P = MV / Y (quantity theory of money)."""
        mv = m * v
        return lambda y: mv / y

    @staticmethod
    def _ad_x_min(m, v, y_max):
        """Minimum x so AD stays within the visible y range."""
        # P = MV/Y ≤ y_max  →  Y ≥ MV/y_max
        return max((m * v) / y_max, 0.1)

    @staticmethod
    def _make_sras_func(price, slope=None, y_bar=None):
        """SRAS curve.

        Flat when slope is None: P = price.
        Upward-sloping: P = Pᵉ + slope·(Y − Ȳ), where price = Pᵉ and
        y_bar = Ȳ (potential output).
        """
        if slope is None:
            return lambda y: price
        return lambda y: price + slope * (y - y_bar)

    @property
    def _lr_price(self):
        """Long-run equilibrium expected price Pᵉ.

        In long-run equilibrium expectations are correct: Pᵉ = P = MV/Ȳ.
        For the sloped SRAS P = Pᵉ + slope·(Y − Ȳ), at Y = Ȳ the
        deviation term vanishes, so Pᵉ = MV/Ȳ regardless of slope.
        """
        return (self._m * self._v) / self._lras_y

    def shift_ad(self, m=None, v=None, run_time=1, show_arrows=False):
        """Animate AD shifting due to changes in M and/or V."""
        self._m = m if m is not None else self._m
        self._v = v if v is not None else self._v
        new_func = self._make_ad_func(self._m, self._v)
        y_max = self.axes.y_range[1]
        x_min = self._ad_x_min(self._m, self._v, y_max)
        return self.get_shift_animation(
            "ad", new_func, new_x_range=[x_min, 10], run_time=run_time,
            show_arrows=show_arrows,
        )

    def shift_sras(self, sras_price=None, sras_slope=None, run_time=1,
                   show_arrows=False):
        """Animate SRAS shifting to a new expected price Pᵉ and/or slope."""
        if sras_price is not None:
            self._sras_price = sras_price
        if sras_slope is not None:
            self._sras_slope = sras_slope
        new_func = self._make_sras_func(
            self._sras_price, self._sras_slope, self._lras_y,
        )
        return self.get_shift_animation(
            "sras", new_func, run_time=run_time, show_arrows=show_arrows,
        )

    def shift_lras(self, new_y, run_time=1):
        """Animate LRAS moving to a new potential output."""
        old_line = self.curves["lras"]
        y_min = self.axes.y_range[0]
        y_max = self.axes.y_range[1]
        new_line = Line(
            self.axes.c2p(new_y, y_min),
            self.axes.c2p(new_y, y_max),
            color=old_line.get_color(),
        )
        self.curves["lras"] = new_line
        self._lras_y = new_y

        anims = [Transform(old_line, new_line, run_time=run_time)]

        if "lras" in self._curve_labels:
            old_label = self._curve_labels["lras"]
            new_label = old_label.copy().next_to(new_line, UP, buff=0.15)
            anims.append(Transform(old_label, new_label, run_time=run_time))

        return AnimationGroup(*anims)

    def long_run_adjust(self, run_time=_LR_RUN_TIME, show_arrows=False):
        """SRAS slowly shifts to restore long-run equilibrium.

        After a shock moves output away from LRAS, SRAS gradually adjusts
        to P = MV / Y_potential, bringing the economy back to potential output.
        The animation is slow by default (2s) to show the gradual adjustment.
        """
        return self.shift_sras(sras_price=self._lr_price, run_time=run_time,
                               show_arrows=show_arrows)

    # ---- Demand shocks ----

    def _append_long_run(self, anims, lr_run_time, show_arrows):
        """Helper: clear old arrows then append long-run adjustment."""
        clear = self.clear_arrows()
        if clear is not None:
            anims.append(clear)
        anims.append(self.long_run_adjust(run_time=lr_run_time,
                                          show_arrows=show_arrows))

    def positive_demand_shock(self, m=None, v=None, long_run=True,
                              lr_run_time=_LR_RUN_TIME, show_arrows=False):
        """Positive demand shock (e.g. increase in M or V).

        Short run: AD shifts right → output rises above potential, price unchanged.
        Long run: SRAS slowly shifts up → output returns to potential at higher price.

        Returns a list of animations to play in sequence.
        """
        anims = [self.shift_ad(m=m, v=v, show_arrows=show_arrows)]
        if long_run:
            self._append_long_run(anims, lr_run_time, show_arrows)
        return anims

    def negative_demand_shock(self, m=None, v=None, long_run=True,
                              lr_run_time=_LR_RUN_TIME, show_arrows=False):
        """Negative demand shock (e.g. decrease in M or V).

        Short run: AD shifts left → output falls below potential, price unchanged.
        Long run: SRAS slowly shifts down → output returns to potential at lower price.

        Returns a list of animations to play in sequence.
        """
        anims = [self.shift_ad(m=m, v=v, show_arrows=show_arrows)]
        if long_run:
            self._append_long_run(anims, lr_run_time, show_arrows)
        return anims

    # ---- Supply shocks ----

    def adverse_supply_shock(self, sras_price, long_run=True,
                             lr_run_time=_LR_RUN_TIME, show_arrows=False):
        """Adverse supply shock (e.g. oil price spike, cost push).

        Short run: SRAS shifts up → price rises, output falls (stagflation).
        Long run: SRAS slowly shifts back down as economy self-corrects.

        Returns a list of animations to play in sequence.
        """
        anims = [self.shift_sras(sras_price=sras_price, show_arrows=show_arrows)]
        if long_run:
            self._append_long_run(anims, lr_run_time, show_arrows)
        return anims

    def positive_supply_shock(self, sras_price, long_run=True,
                              lr_run_time=_LR_RUN_TIME, show_arrows=False):
        """Positive supply shock

        Short run: SRAS shifts down → price falls, output rises.
        Long run: SRAS slowly shifts back up as economy self-corrects.

        Returns a list of animations to play in sequence.
        """
        anims = [self.shift_sras(sras_price=sras_price, show_arrows=show_arrows)]
        if long_run:
            self._append_long_run(anims, lr_run_time, show_arrows)
        return anims
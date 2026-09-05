# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""IS-LM diagram for Manim.

This module provides the IS-LM model diagram.

"""

from manim import BLUE, RED

from .base import EconDiagram


class ISLMDiagram(EconDiagram):
    """IS-LM model diagram.

    IS curve (goods market equilibrium):
        Y = a - b*r  =>  r = a/b - Y/b

    LM curve (money market equilibrium):
        Ms = k*Y - h*r  =>  r = (k*Y - Ms) / h

    Parameters:
        a: Autonomous spending (default 10)
        b: Interest sensitivity of investment (default 2)
        ms: Real money supply (default 5)
        k: Income sensitivity of money demand (default 0.5)
        h: Interest sensitivity of money demand (default 1)
    """

    def __init__(
        self,
        a=9.5,
        b=1.5,
        ms=2,
        k=1,
        h=1,
        show_equilibrium=True,
        numbered_eq=False,
        **kwargs,
    ):
        kwargs.setdefault("y_range", [-2, 8, 1])
        super().__init__(x_label="Y", y_label="r", **kwargs)

        self._a = a
        self._b = b
        self._ms = ms
        self._k = k
        self._h = h

        y_range = kwargs.get("y_range", [0, 10, 1])
        self._y_min = y_range[0]
        self._y_max = y_range[1]
        self._x_max = kwargs.get("x_range", [0, 10, 1])[1]

        is_func = self._make_is_func(a, b)
        lm_func = self._make_lm_func(ms, k, h)

        self.is_curve = self.add_curve(
            "is", is_func,
            x_range=self._clamp_is(a, b),
            color=BLUE, label_text="IS",
        )
        self.lm_curve = self.add_curve(
            "lm", lm_func,
            x_range=self._clamp_lm(ms, k, h),
            color=RED, label_text="LM",
        )

        if show_equilibrium:
            self.mark_equilibrium("is", "lm", label_x="Y", label_y="r",
                                  numbered=numbered_eq)

    @staticmethod
    def _make_is_func(a, b):
        """r = a/b - Y/b"""
        return lambda y: a / b - y / b

    @staticmethod
    def _make_lm_func(ms, k, h):
        """r = (k*Y - Ms) / h"""
        return lambda y: (k * y - ms) / h

    def _clamp_is(self, a, b):
        """X range so IS (r = a/b - Y/b) stays within visible y range."""
        # r = a/b - Y/b => Y = a - b*r
        x_at_ymax = a - b * self._y_max
        x_at_ymin = a - b * self._y_min
        lo = max(x_at_ymax, 0)
        hi = min(x_at_ymin, self._x_max)
        return [lo, hi]

    def _clamp_lm(self, ms, k, h):
        """X range so LM (r = (kY - Ms)/h) stays within visible y range."""
        # r = (kY - Ms)/h => Y = (h*r + Ms) / k
        x_at_ymin = (h * self._y_min + ms) / k
        x_at_ymax = (h * self._y_max + ms) / k
        lo = max(x_at_ymin, 0)
        hi = min(x_at_ymax, self._x_max)
        return [lo, hi]

    def shift_is(self, a=None, b=None, run_time=1, show_arrows=False):
        """Animate IS shifting due to changes in autonomous spending or interest sensitivity."""
        self._a = a if a is not None else self._a
        self._b = b if b is not None else self._b
        new_func = self._make_is_func(self._a, self._b)
        return self.get_shift_animation(
            "is", new_func, new_x_range=self._clamp_is(self._a, self._b),
            run_time=run_time, show_arrows=show_arrows,
        )

    def shift_lm(self, ms=None, k=None, h=None, run_time=1, show_arrows=False):
        """Animate LM shifting due to changes in money supply or money demand parameters."""
        self._ms = ms if ms is not None else self._ms
        self._k = k if k is not None else self._k
        self._h = h if h is not None else self._h
        new_func = self._make_lm_func(self._ms, self._k, self._h)
        return self.get_shift_animation(
            "lm", new_func, new_x_range=self._clamp_lm(self._ms, self._k, self._h),
            run_time=run_time, show_arrows=show_arrows,
        )

    # ---- Monetary policy ----

    def monetary_expansion(self, ms, show_arrows=False):
        """Increase in money supply → LM shifts right → lower r, higher Y."""
        return [self.shift_lm(ms=ms, show_arrows=show_arrows)]

    def monetary_contraction(self, ms, show_arrows=False):
        """Decrease in money supply → LM shifts left → higher r, lower Y."""
        return [self.shift_lm(ms=ms, show_arrows=show_arrows)]

    # ---- Fiscal policy ----

    def fiscal_expansion(self, a, show_arrows=False):
        """Increase in government spending → IS shifts right → higher r, higher Y."""
        return [self.shift_is(a=a, show_arrows=show_arrows)]

    def fiscal_contraction(self, a, show_arrows=False):
        """Decrease in government spending → IS shifts left → lower r, lower Y."""
        return [self.shift_is(a=a, show_arrows=show_arrows)]
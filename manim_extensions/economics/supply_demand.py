# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Supply and demand diagram for Manim.

This module provides the supply and demand diagram.

"""


from manim import *
from .base import EconDiagram


class SupplyDemandDiagram(EconDiagram):
    """A supply-and-demand diagram.

    Parameters
    ----------
    demand_func
        Demand function ``P = D(Q)`` (default ``8 - 0.5·Q``).
    supply_func
        Supply function ``P = S(Q)`` (default ``2 + 0.5·Q``).
    show_equilibrium
        If True (default), mark the supply–demand intersection as the equilibrium.
    **kwargs
        Additional keyword arguments passed to :class:`~manim_extensions.economics.base.EconDiagram`.
    """

    def __init__(
        self,
        demand_func=None,
        supply_func=None,
        show_equilibrium=True,
        **kwargs,
    ):
        super().__init__(x_label="Q", y_label="P", **kwargs)

        demand_func = demand_func or (lambda x: 8 - 0.5 * x)
        supply_func = supply_func or (lambda x: 2 + 0.5 * x)

        self.demand = self.add_curve(
            "demand", demand_func, x_range=[0, 10], color=BLUE, label_text="D"
        )
        self.supply = self.add_curve(
            "supply", supply_func, x_range=[0, 10], color=RED, label_text="S"
        )

        if show_equilibrium:
            self.mark_equilibrium("demand", "supply", label_x="Q*", label_y="P*")
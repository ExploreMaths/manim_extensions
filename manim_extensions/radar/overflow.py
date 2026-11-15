# SPDX-FileCopyrightText: 2026 FTZ-OPUS
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""The overflow chart (越界雷达图): :class:`~manim_extensions.radar.overflow.OverflowRadarChart`.

Values above the full scale are no longer clamped to a ``"10+"`` read-out —
they stab beyond the outer ring as filled spikes, with a dashed track along
the spoke, a glowing breach where the polygon pierces the ring, and burst
transitions whose overshoot makes the escape visible.
"""

from __future__ import annotations

from typing import Any, Optional, Sequence, Union

from .animations import RadarBurstIn
from .chart import RadarChart
from .config import RadarConfig, get_style
from .data import RadarData
from .theme import RadarTheme

__all__ = ["OverflowRadarChart"]


class OverflowRadarChart(RadarChart):
    """A radar chart whose data may break through the outer ring.

    The outer ring sits at the full scale; any value above it escapes as a
    filled spike. Everything from :class:`~manim_extensions.radar.overflow.OverflowRadarChart.RadarChart` works here too
    (``reveal`` / ``morph_to`` / ``disappear``), but morphs default to the
    ``"burst"`` transition and the entrance of choice is :meth:`~manim_extensions.radar.overflow.OverflowRadarChart.burst_in`.

    Comparison mode works as well — pass ``datasets=[...]`` and *every*
    dataset gets its own spikes, dashed tracks, breach glows and unclamped
    read-outs::

        chart = OverflowRadarChart(datasets=[holder, basic], max_value=10)

    Examples
    --------
    ::

        chart = OverflowRadarChart(
            axes=AXES,
            values=[8, 6, 14, 9, 5, 8],   # 14 escapes the 10 ring
            max_value=10,
        )
        self.play(chart.burst_in())                       # stab out of the ring
        self.play(chart.morph_to([7, 9, 17, 6, 8, 5]))    # burst to new spikes
    """

    def __init__(
        self,
        data: Optional[RadarData] = None,
        *,
        axes: Optional[Sequence[str]] = None,
        values: Optional[Sequence[float]] = None,
        datasets: Optional[Sequence] = None,
        name: Optional[str] = None,
        color: Optional[str] = None,
        max_value: Optional[float] = None,
        compare_numbers: Optional[str] = None,
        legend: Optional[bool] = None,
        style: Union[str, RadarConfig, None] = "neo",
        theme: Union[str, RadarTheme, None] = "midnight",
        config: Optional[RadarConfig] = None,
        radius: Optional[float] = None,
        position: Optional[Sequence[float]] = None,
        title: Optional[str] = None,
        levels: Optional[int] = None,
        numbers: Optional[str] = None,
        sweep: Optional[bool] = None,
        rim: Optional[bool] = None,
        opacity: Optional[float] = None,
        **kwargs,
    ) -> None:
        base = config if config is not None else get_style(style)
        base = base.evolved(overflow=True)
        if radius is None and config is None:
            # spikes need headroom: the subclass ships a slightly smaller grid
            radius = 2.55
        if position is None and config is None:
            # a touch higher than RadarChart, so bottom spikes stay in frame
            position = (0.0, 0.10)
        super().__init__(
            data,
            axes=axes,
            values=values,
            datasets=datasets,
            name=name,
            color=color,
            max_value=max_value,
            compare_numbers=compare_numbers,
            legend=legend,
            config=base,
            theme=theme,
            radius=radius,
            position=position,
            title=title,
            levels=levels,
            numbers=numbers,
            sweep=sweep,
            rim=rim,
            opacity=opacity,
            **kwargs,
        )

    # ------------------------------------------------------------------
    def morph_to(self, data: Any, **kwargs) -> Any:
        """Morph with the ``"burst"`` transition unless told otherwise.

        Pass ``transition=`` explicitly (e.g. ``"smooth"``) to opt out.
        """
        kwargs.setdefault("transition", "burst")
        return super().morph_to(data, **kwargs)

    def burst_in(self, run_time: float = 1.1, **kwargs) -> Any:
        """Entrance: values stab out of the centre and overshoot their target."""
        return RadarBurstIn(self, run_time=run_time, **kwargs)

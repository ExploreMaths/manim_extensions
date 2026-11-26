# SPDX-FileCopyrightText: 2026 FTZ-OPUS
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""The overflow radar chart: :class:`~manim_extensions.radar.overflow.OverflowRadarChart`.

Values above the full scale are no longer clamped to a ``"10+"`` read-out.
They stab beyond the outer ring as filled spikes, with a dashed track along
the spoke, a glowing breach where the polygon pierces the ring, and burst
transitions whose overshoot makes the escape visible.
"""

from __future__ import annotations
from collections.abc import Sequence
from typing import Any, Optional, Union

from manim import Animation

from .animations import RadarBurstIn
from .chart import RadarChart, RadarInputList
from .config import RadarConfig, get_style
from .data import RadarData
from .theme import RadarTheme

__all__ = ["OverflowRadarChart"]


class OverflowRadarChart(RadarChart):
    """A radar chart whose data may break through the outer ring.

    .. doc-example-covers: burst_in, morph_to


    The outer ring sits at the full scale; any value above it escapes as a
    filled spike. Everything from :class:`~manim_extensions.radar.overflow.OverflowRadarChart.RadarChart` works here too
    (``reveal`` / ``morph_to`` / ``disappear``), but morphs default to the
    ``"burst"`` transition and the entrance of choice is :meth:`~manim_extensions.radar.overflow.OverflowRadarChart.burst_in`.

    Comparison mode works as well — pass ``datasets=[...]`` and *every*
    dataset gets its own spikes, dashed tracks, breach glows and unclamped
    read-outs::

        chart = OverflowRadarChart(datasets=[holder, basic], max_value=10)

    Parameters
    ----------
    data
        Optional snapshot built elsewhere.
    axes
        Axis labels.
    values
        Values for one dataset.
    datasets
        Multiple datasets for comparison mode.
    name
        Dataset name.
    color
        Dataset colour.
    max_value
        Full scale of the outer ring.
    compare_numbers
        Number placement mode in comparison mode.
    legend
        Whether to draw a legend.
    style
        Style preset name or configuration.
    theme
        The theme name or theme object.
    config
        Complete configuration overriding the style preset.
    radius
        Outer-ring radius.
    position
        Chart centre in scene coordinates.
    title
        Chart title.
    levels
        Number of grid rings.
    numbers
        Read-out mode.
    sweep
        Whether to draw the sweep highlight.
    rim
        Whether to draw the emphasis outline.
    opacity
        Chart opacity.
    kwargs
        Further keyword arguments forwarded to
        :class:`~manim_extensions.radar.chart.RadarChart`.

    Examples
    --------
    .. manim:: OverflowRadarScene

       from manim import *
       from manim_extensions.radar.overflow import OverflowRadarChart

       class OverflowRadarScene(Scene):
           def construct(self):
               chart = OverflowRadarChart(
                   axes=["A", "B", "C", "D", "E", "F"],
                   values=[8, 6, 14, 9, 5, 8],
                   max_value=10,
               )
               chart.scale_to_fit_height(5.2).move_to(ORIGIN)
               self.add(chart)
               self.play(chart.burst_in())
               self.play(chart.morph_to([7, 9, 17, 6, 8, 5]))
    """

    def __init__(
        self,
        data: Optional[RadarData] = None,
        *,
        axes: Optional[Sequence[str]] = None,
        values: Optional[Sequence[float]] = None,
        datasets: Optional[Sequence[Any]] = None,
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
        **kwargs: Any,
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
    def morph_to(self, data: RadarInputList, **kwargs: Any) -> Animation:
        """Morph with the burst transition unless told otherwise.

        Parameters
        ----------
        data
            Destination snapshot or list of snapshots.
        kwargs
            Further keyword arguments forwarded to
            :meth:`~manim_extensions.radar.chart.RadarChart.morph_to`.

        Returns
        -------
            The morph animation.
        """

        kwargs.setdefault("transition", "burst")
        return super().morph_to(data, **kwargs)

    def burst_in(self, run_time: float = 1.1, **kwargs: Any) -> Animation:
        """Play the overflow entrance.

        Parameters
        ----------
        run_time
            Duration of the entrance.
        kwargs
            Further keyword arguments forwarded to
            :class:`~manim_extensions.radar.animations.RadarBurstIn`.

        Returns
        -------
            The entrance animation.
        """

        return RadarBurstIn(self, run_time=run_time, **kwargs)

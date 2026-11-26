# SPDX-FileCopyrightText: 2026 FTZ-OPUS
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""The core objects: :class:`~manim_extensions.radar.chart.RadarChart` (single- or multi-dataset).

New in 0.1.1: several datasets can share one grid (comparison mode), with a
legend, four per-vertex number modes, focus dimming, a difference highlight
(:meth:`~manim_extensions.radar.chart.RadarChart.highlight_gap`) and overflow-aware painting used by
:class:`~manim_extensions.radar.overflow.OverflowRadarChart`.
"""

from __future__ import annotations
from collections.abc import Sequence
from typing import Any, Optional, TYPE_CHECKING, Union, cast

import math
from dataclasses import replace

import numpy as np
from manim import (
    DOWN,
    Create,
    ORIGIN,
    RIGHT,
    WHITE,
    Circle,
    Dot,
    Line,
    ManimColor,
    Polygon,
    RoundedRectangle,
    Animation,
    Mobject,
    Scene,
    Text,
    VGroup,
    config as manim_config,
)

from manim.utils.color import ParsableManimColor
from manim.mobject.mobject import _AnimationBuilder
from .config import RadarConfig, get_style
from .data import RadarData
from .numbers import RollingNumber
from .theme import RadarTheme, get_theme
from .utils import lighten, mix, pick_font

if TYPE_CHECKING:
    from .camera import CameraRig


RadarInput = Union[RadarData, dict[Any, Any], Sequence[float]]
RadarInputList = Union[RadarInput, Sequence[RadarInput]]

__all__ = ["RadarChart"]

#: Full circle in radians (two times pi).
TAU = 2.0 * math.pi

_CJK_FONTS = (
    "PingFang SC",
    "Heiti SC",
    "Hiragino Sans GB",
    "Noto Sans CJK SC",
    "Source Han Sans SC",
    "Microsoft YaHei",
    "SimHei",
    "WenQuanYi Micro Hei",
)
_MONO_FONTS = (
    "Menlo",
    "Consolas",
    "DejaVu Sans Mono",
    "Liberation Mono",
    "Courier New",
)


class Series:
    """One dataset: its polygon family, its live tween state, its numbers.

    Parameters
    ----------
    chart
        The owning chart, used for configuration, theme and axis count.
    index
        Position of this dataset in the chart's series list.
    data
        Snapshot supplying the values, axes and dataset metadata.
    color
        Fill and stroke colour for the polygon family.
    rim
        Emphasis rim strength in the range 0 to 1.
    primary
        Whether this is the first dataset, which owns the glow and halo.

    Examples
    --------
    .. manim:: SeriesScene
       :save_last_frame:

       from manim import *
       from manim_extensions.radar.chart import RadarChart

       class SeriesScene(Scene):
           def construct(self):
               chart = RadarChart(axes=["Speed", "Power", "Range", "Comfort", "Safety"], values=[8, 6, 7, 9, 5])
               chart.scale_to_fit_height(5.0).move_to(ORIGIN)
               series = chart._series[0]
               assert series.values == [8.0, 6.0, 7.0, 9.0, 5.0]
               self.add(chart)
    """

    def __init__(
        self,
        chart: RadarChart,
        index: int,
        data: RadarData,
        color: ParsableManimColor,
        rim: float,
        primary: bool,
    ) -> None:
        self.index = index
        self.data = data
        self.values = [float(v) for v in data.values]
        self.color = ManimColor(color)
        self.rim = float(rim)
        self.opacity = 1.0
        self.opacity_target = 1.0
        self.numbers: Optional[VGroup] = None  # per-axis RollingNumbers (compare modes)

        # overflow decorations, owned per dataset (lazily built on first spike)
        self.fx_group: Optional[VGroup] = None  # dash tracks, in the chart's fx layer
        self.dash_pool: list[Optional[VGroup]] = []  # per axis
        self.breach: list[Optional[VGroup]] = []  # per axis
        self.big_numbers: dict[Any, Any] = {}  # axis -> unclamped RollingNumber
        self.big_numbers_group: Optional[VGroup] = None

        cfg = chart.config
        n = chart._n
        self.group = VGroup()
        ph = Polygon(ORIGIN, ORIGIN + RIGHT, ORIGIN + RIGHT)

        # glow / halo / inner tint: the halo & tint only make sense for a lone
        # dataset; with several datasets sharing the grid they are switched off
        # per frame (the mobjects stay, so morphing in/out never rebuilds).
        self.halo = (
            ph.copy().set_stroke(width=cfg.halo_width, opacity=0).set_fill(opacity=0)
            if primary and cfg.glow_layers >= 2
            else None
        )
        self.glow = (
            ph.copy().set_stroke(width=cfg.glow_width, opacity=0).set_fill(opacity=0)
            if cfg.glow_layers >= 1
            else None
        )
        self.fill = (
            ph.copy()
            .set_stroke(width=0)
            .set_fill(color=self.color, opacity=cfg.fill_opacity)
        )
        self.inner = (
            ph.copy().set_stroke(width=0) if primary and cfg.inner_tint else None
        )

        self.edges = None
        self.outline = ph.copy().set_fill(opacity=0).set_stroke(width=cfg.line_width)
        if primary and cfg.rainbow_edges:
            # series 0 carries both: the rainbow edges for the solo look and a
            # plain outline for the comparison look; _refresh picks per frame.
            self.edges = VGroup()
            for _ in range(n * max(1, cfg.edge_segments)):
                self.edges.add(
                    Line(ORIGIN, ORIGIN + RIGHT, stroke_width=cfg.line_width)
                )

        self.dots = VGroup()
        if cfg.vertex_dots:
            factor = 1.0 if primary else 0.72
            for i in range(n):
                col = chart.theme.axis_color(i)
                for radius, opacity in (
                    (cfg.dot_radius * factor * 3.2, 0.10),
                    (cfg.dot_radius * factor, 0.90),
                    (cfg.dot_radius * factor * 0.55, 0.95),
                ):
                    dot = Circle(radius=radius, stroke_width=0, fill_color=col)
                    dot.base_op = opacity  # type: ignore[attr-defined]
                    self.dots.add(dot)

        self.rim_outer = (
            ph.copy()
            .set_fill(opacity=0)
            .set_stroke(
                width=cfg.rim_width_outer, color=chart.theme.rim_outer, opacity=0
            )
        )
        self.rim_inner = (
            ph.copy()
            .set_fill(opacity=0)
            .set_stroke(
                width=cfg.rim_width_inner, color=chart.theme.rim_inner, opacity=0
            )
        )
        self.glitch_outer = (
            ph.copy()
            .set_fill(opacity=0)
            .set_stroke(
                width=cfg.line_width, color=chart.theme.glitch_split[0], opacity=0
            )
        )
        self.glitch_inner = (
            ph.copy()
            .set_fill(opacity=0)
            .set_stroke(
                width=cfg.line_width, color=chart.theme.glitch_split[1], opacity=0
            )
        )

        for m in (
            self.halo,
            self.glow,
            self.fill,
            self.inner,
            self.edges if self.edges is not None else self.outline,
            self.dots,
            self.rim_outer,
            self.rim_inner,
            self.glitch_outer,
            self.glitch_inner,
        ):
            if m is not None:
                self.group.add(m)


class RadarChart(VGroup):
    """An animated radar (spider) chart that morphs into other radar charts.

    .. doc-example-covers: attach_backdrop, disappear, glitch_in, morph_to, reveal, shockwave, trace_web


    The chart is a plain Manim mobject, so ``shift`` / ``move_to`` / ``scale`` /
    ``rotate`` behave as usual: every piece of geometry is recomputed in the
    chart's own coordinate frame on each frame.

    Parameters
    ----------
    data
        Initial snapshot; its axes define the grid when ``axes`` is omitted.
    axes
        Names of the axes, in clockwise order.
    values
        One numeric value per axis for the first dataset.
    name
        Nameplate shown above a single dataset.
    color
        Main polygon colour for the first dataset.
    max_value
        Fixed full-scale value; otherwise derived from the data.
    datasets
        Snapshots or mappings describing several datasets at once.
    style
        Named radar style or a prepared configuration.
    theme
        Named colour theme or a prepared theme object.
    config
        Configuration overriding the style defaults.
    radius
        Grid radius in Manim units.
    position
        Centre point of the grid.
    title
        Chart title drawn above the grid.
    levels
        Number of concentric grid rings.
    numbers
        Per-vertex number mode, such as ``"none"`` or ``"value"``.
    web_rainbow
        Whether grid segments use the rainbow palette.
    compare_numbers
        Number mode used while several datasets are visible.
    legend
        Whether a legend is shown for multiple datasets.
    sweep
        Whether the rotating sweep beam is visible.
    rim
        Whether the emphasis rim is enabled.
    overflow
        Whether values above the full scale trigger overflow effects.
    opacity
        Initial opacity of the whole chart.
    kwargs
        Further keyword arguments forwarded to ``VGroup``.

    Examples
    --------
    .. manim:: RadarChartScene

       from manim import *
       from manim_extensions.radar.chart import RadarChart

       class RadarChartScene(Scene):
           def construct(self):
               chart = RadarChart(
                   axes=["Speed", "Power", "Range", "Comfort", "Price", "Safety"],
                   values=[8, 6, 7, 9, 5, 8],
               )
               self.play(chart.reveal())
               self.wait(1)

    Minimal chart::

        chart = RadarChart(
            axes=["Speed", "Power", "Range", "Comfort", "Price", "Safety"],
            values=[8, 6, 7, 9, 5, 8],
        )
        self.play(chart.reveal())

    One command to morph into another snapshot::

        self.play(chart.morph_to(RadarData(axes=..., values=[...])))

    Comparison mode (new in 0.1.1) — several datasets share one grid::

        chart = RadarChart(datasets=[holder_data, basic_data], theme="midnight")
        self.play(chart.reveal())
        self.play(chart.morph_to([holder_next, basic_next]))   # morph them all
        chart.focus(0)                                          # dim dataset 1
        chart.highlight_gap(0, 1)                               # tint the gap

    The chart repaints every frame, so all of the calls above can be chained
    before the next animation.
    """

    def __init__(
        self,
        data: Optional[RadarData] = None,
        *,
        axes: Optional[Sequence[str]] = None,
        values: Optional[Sequence[float]] = None,
        name: Optional[str] = None,
        color: Optional[str] = None,
        max_value: Optional[float] = None,
        datasets: Optional[Sequence[Any]] = None,
        style: Union[str, RadarConfig, None] = "neo",
        theme: Union[str, RadarTheme, None] = "midnight",
        config: Optional[RadarConfig] = None,
        radius: Optional[float] = None,
        position: Optional[Sequence[float]] = None,
        title: Optional[str] = None,
        levels: Optional[int] = None,
        numbers: Optional[str] = None,
        web_rainbow: Optional[bool] = None,
        compare_numbers: Optional[str] = None,
        legend: Optional[bool] = None,
        sweep: Optional[bool] = None,
        rim: Optional[bool] = None,
        overflow: Optional[bool] = None,
        opacity: Optional[float] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)

        # ---- config / theme -----------------------------------------------
        base = config if config is not None else get_style(style)
        self.config = base.evolved(
            radius=radius,
            position=tuple(position) if position is not None else None,
            title=title,
            levels=levels,
            numbers=numbers,
            web_rainbow=web_rainbow,
            compare_numbers=compare_numbers,
            legend=legend,
            sweep=sweep,
            rim=rim,
            overflow=overflow,
            opacity=opacity,
        ).validated()
        self.theme = get_theme(theme)
        cfg = self.config

        # ---- data ----------------------------------------------------------
        if datasets is not None and data is not None:
            raise ValueError("pass either ``data`` or ``datasets``, not both")
        if datasets is None:
            if data is None:
                if axes is None or values is None:
                    raise ValueError(
                        "pass a RadarData, ``datasets``, or both ``axes`` and ``values``"
                    )
                data = RadarData(
                    axes=axes,
                    values=values,
                    name=name,
                    color=color,
                    max_value=max_value,
                )
            elif axes is not None or values is not None:
                raise ValueError("pass either a RadarData or axes/values, not both")
            self._initial = [data]
        else:
            self._initial = list(datasets)
        self._multi = len(self._initial) > 1

        # ---- fonts & axes --------------------------------------------------
        # Manim 0.21 cannot hash a Text object whose font is None.  Minimal
        # Linux CI images may not contain any of our preferred families, so
        # fall back to Pango's generic families instead of passing None.
        self._font_name: str = (
            cfg.name_font or pick_font(_CJK_FONTS, default="sans") or "sans"
        )
        self._font_number: str = (
            cfg.number_font or pick_font(_MONO_FONTS, default="monospace") or "sans"
        )
        self._font_title: str = cfg.title_font or self._font_name

        first = (
            self._coerce_item(self._initial[0])
            if not isinstance(self._initial[0], RadarData)
            else self._initial[0]
        )
        n = self._n = first.n_axes
        step = 360.0 / n
        sign = -1.0 if cfg.clockwise else 1.0
        self._angles = [cfg.start_angle + sign * step * i for i in range(n)]

        # ---- invisible transform anchors -----------------------------------
        home = np.array([cfg.position[0], cfg.position[1], 0.0])
        self._anchor = VGroup(
            Dot(radius=1e-4, fill_opacity=0, stroke_opacity=0).move_to(home),
            Dot(radius=1e-4, fill_opacity=0, stroke_opacity=0).move_to(home + RIGHT),
        )
        self.add(self._anchor)

        # ---- grid ----------------------------------------------------------
        self.web = VGroup()
        self.grid_glow = VGroup()
        for lvl in range(1, cfg.levels + 1):
            outer = lvl == cfg.levels
            ring = Polygon(
                ORIGIN,
                ORIGIN + RIGHT,
                ORIGIN + RIGHT,  # placeholder, set below
                stroke_color=self.theme.grid,
                stroke_width=cfg.ring_width_outer if outer else cfg.ring_width,
                stroke_opacity=cfg.ring_opacity_outer if outer else cfg.ring_opacity,
            )
            ring.base_so = cfg.ring_opacity_outer if outer else cfg.ring_opacity  # type: ignore[attr-defined]
            self.web.add(ring)
            if cfg.grid_glow:
                g = ring.copy().set_stroke(
                    color=self.theme.grid,
                    width=cfg.grid_glow_width,
                    opacity=cfg.grid_glow_opacity,
                )
                g.base_so = cfg.grid_glow_opacity  # type: ignore[attr-defined]
                self.grid_glow.add(g)
        for i in range(n):
            spoke = Line(
                ORIGIN,
                ORIGIN + RIGHT,
                stroke_color=self.theme.axis_color(i),
                stroke_width=cfg.spoke_width,
                stroke_opacity=cfg.spoke_opacity,
            )
            spoke.base_so = cfg.spoke_opacity  # type: ignore[attr-defined]
            self.web.add(spoke)
            if cfg.grid_glow:
                glow_spoke = spoke.copy().set_stroke(
                    color=self.theme.axis_color(i),
                    width=cfg.grid_glow_width,
                    opacity=cfg.grid_glow_opacity,
                )
                glow_spoke.base_so = cfg.grid_glow_opacity  # type: ignore[attr-defined]
                self.grid_glow.add(glow_spoke)
        self.add(self.grid_glow, self.web)

        # ---- level scale numbers -------------------------------------------
        self.level_labels = VGroup()
        if cfg.show_level_labels:
            self.add(self.level_labels)

        # ---- sweep ---------------------------------------------------------
        self.sweep = VGroup()
        if cfg.sweep:
            self.sweep.add(
                Polygon(ORIGIN, ORIGIN + RIGHT, fill_opacity=0, stroke_width=0),
                Line(ORIGIN, ORIGIN + RIGHT, stroke_width=cfg.sweep_edge_width),
            )
            self.add(self.sweep)

        # ---- polygon layers (one group per dataset) + gap lobes -------------
        # ---- rainbow web (web_rainbow): segmented coloured lines replace the built-in grid ----
        self._rainbow_web = None
        if cfg.web_rainbow:
            web = VGroup()
            for k in range(1, cfg.levels + 1):
                for i in range(n):
                    hue = ((i + 0.5) / n) % 1.0  # half-step offset avoids axis colours
                    col = ManimColor.from_hsv((hue, 0.85, 1.0))
                    web.add(
                        Line(
                            ORIGIN,
                            ORIGIN,
                            stroke_width=3.2,
                            color=col,
                            stroke_opacity=0.0,
                        )
                    )
            for i in range(n):
                web.add(
                    Line(
                        ORIGIN,
                        ORIGIN,
                        stroke_width=2.8,
                        color=self.theme.axis_color(i),
                        stroke_opacity=0.0,
                    )
                )
            web.set_opacity(0.0)  # visible when trace_web runs
            self._rainbow_web = web
            self.add(web)
            web.add_updater(lambda m: self._place_rainbow_web())
            # after thickening/brightening the rainbow web, axis names need extra spacing; hide tick numbers to avoid clutter
            if cfg.label_offset == 1.10:
                cfg.label_offset = 1.24
            if cfg.show_level_labels:
                cfg.show_level_labels = False

        # z-order: grid -> [gap lobes -> series 0 -> series 1 ...] -> labels
        self._poly_layers = VGroup()
        self.gap_group: Optional[VGroup] = None
        self._gap_spec: Optional[dict[Any, Any]] = None
        self._series: list[Series] = []
        self.add(self._poly_layers)

        # ---- axis names & value numbers ------------------------------------
        self.axis_names = VGroup()
        self.value_numbers = VGroup()
        for i in range(n):
            label = Text(
                str(first.axes[i]),
                font=self._font_name,
                weight=cfg.name_weight,
                font_size=cfg.name_size,
                color=(
                    self.theme.axis_color(i)
                    if cfg.colored_axis_names
                    else self.theme.number
                ),
            )
            self.axis_names.add(label)
            self.value_numbers.add(
                RollingNumber(
                    font=self._font_number,
                    size=cfg.number_size,
                    color=self.theme.number,
                    template=cfg.number_format,
                    max_value=1.0,  # synced below once the scale is known
                    suffix=cfg.overflow_suffix,
                    roll_height=cfg.roll_height,
                    mode=cfg.numbers,
                )
            )
        self.add(self.axis_names, self.value_numbers)

        # per-series vertex numbers (comparison modes) and overflow read-outs
        self._compare_numbers = VGroup()
        self._overflow_numbers_group = VGroup()
        self.add(self._compare_numbers, self._overflow_numbers_group)

        # ---- overflow decorations (dashed tracks + breach glows) -----------
        # lives ABOVE the polygons (added after the series, see below); the
        # per-dataset pieces are built lazily by _paint_overflow
        self._overflow_fx = VGroup()

        # ---- nameplate & header & legend ------------------------------------
        self._name_holder = VGroup()
        self._name_text: Optional[Text] = None
        self._name_old: Optional[Text] = None
        self._name_alpha = 1.0
        self._name_old_alpha = 0.0
        self._name_dy = 0.0
        self._name_old_dy = 0.0
        self.add(self._name_holder)
        self.header: Optional[Text] = None
        self._title_visible = False
        if cfg.title:
            self.header = self._make_title(cfg.title)
            self.add(self.header)

        self.legend = VGroup()
        self._legend_content: Optional[VGroup] = None
        self._legend_old: Optional[VGroup] = None
        self._legend_alpha = 1.0
        self._legend_old_alpha = 0.0
        self._legend_dy = 0.0
        self._legend_old_dy = 0.0
        self.add(self.legend)

        # ---- datasets --------------------------------------------------------
        self._focus: Optional[int] = None
        self._rig: Optional[CameraRig] = None  # set by attach_camera
        self._install_datasets(self._initial)
        if cfg.overflow:
            # above every series polygon, below the labels & numbers
            self.add(self._overflow_fx)

        # ---- local geometry + first paint ----------------------------------
        self._rebuild_local_geometry()
        self.add_updater(self._refresh)
        self._refresh(self, 0.0)

    # ==================================================================
    # dataset plumbing
    # ==================================================================
    def _coerce_item(self, item: RadarInput) -> RadarData:
        """Convert one constructor-level dataset into a validated snapshot.

        Parameters
        ----------
        item
            A :class:`~manim_extensions.radar.data.RadarData`, a mapping with
            ``axes`` and value keys, or a plain sequence of values.

        Returns
        -------
            Snapshot whose axis layout matches this chart.

        Raises
        ------
        ValueError
            If axes are missing, the axis count differs, or the layout changes.
        """
        if isinstance(item, RadarData):
            out = item
        elif isinstance(item, dict):
            payload = dict(item)
            axes = payload.pop("axes", None)
            if axes is None:
                raise ValueError("dataset dict needs ``axes``")
            out = RadarData(axes=axes, **payload)
        else:
            if self._initial and isinstance(self._initial[0], RadarData):
                base = self._initial[0]
            else:
                raise ValueError("plain value lists need a RadarData first")
            out = base.with_values(item)
        if out.n_axes != self._n:
            raise ValueError(f"all datasets need {self._n} axes, got {out.n_axes}")
        if (
            tuple(out.axes)
            != tuple(self._series[0].data.axes if self._series else out.axes)
            and self._series
        ):
            raise ValueError("all datasets must share the same axis layout")
        return out

    def _install_datasets(self, items: Sequence[Any]) -> None:
        """Rebuild the visible series from a sequence of snapshots.

        Parameters
        ----------
        items
            Snapshots, mappings or value sequences to display.

        Raises
        ------
        ValueError
            If a snapshot has a different axis count or axis layout.
        """
        cfg = self.config
        datasets = []
        for it in items:
            if isinstance(it, RadarData):
                datasets.append(it)
            elif isinstance(it, dict):
                datasets.append(self._coerce_item(it))
            else:
                datasets.append(self._coerce_item(it))
        for d in datasets:
            if d.n_axes != self._n:
                raise ValueError(f"all datasets need {self._n} axes, got {d.n_axes}")
        if self._series:
            ref_axes = self._series[0].data.axes
            if any(tuple(d.axes) != tuple(ref_axes) for d in datasets):
                raise ValueError("all datasets must share the same axis layout")

        # shared full scale: the largest of the snapshots' scales
        self._scale = max(d.scale_for(cfg.levels) for d in datasets)
        self._multi = len(datasets) > 1

        # drop surplus series
        while len(self._series) > len(datasets):
            self._drop_series(len(self._series) - 1)

        for i, d in enumerate(datasets):
            color = self._resolve_color(d.color, i)
            rim = 1.0 if (d.rim or d.emphasis == "rim" or cfg.rim) else 0.0
            if i < len(self._series):
                s = self._series[i]
                s.data = d
                s.values = [float(v) for v in d.values]
                s.color = color
                s.rim = rim
            else:
                s = Series(self, i, d, color, rim, primary=(i == 0))
                self._poly_layers.add(s.group)
                self._series.append(s)

        # legacy top-level aliases -> series 0 (0.1.0 code pokes these)
        s0 = self._series[0]
        self.halo = s0.halo
        self.glow = s0.glow
        self.fill = s0.fill
        self.inner = s0.inner
        self.edges = s0.edges
        self.outline = s0.outline
        self.dots = s0.dots
        self.rim_outer = s0.rim_outer
        self.rim_inner = s0.rim_inner
        self.glitch_outer = s0.glitch_outer
        self.glitch_inner = s0.glitch_inner

        self._values = list(self._series[0].values)
        self._color = self._series[0].color
        self._rim = self._series[0].rim
        self._glitch = getattr(self, "_glitch", 0.0)
        self._opacity = float(cfg.opacity)
        self._phase = getattr(self, "_phase", 0.0)
        self._time = getattr(self, "_time", 0.0)

        self._sync_number_scale()
        content = self._rebuild_legend(self._legend_pairs(datasets))
        for old in list(self.legend.submobjects):
            self.legend.remove(old)
        if len(content):
            self._legend_content = content
            self.legend.add(content)
        else:
            self._legend_content = None
        if self._multi:
            self._name_old = None
            self._name_text = None
            self._name_holder.remove(*list(self._name_holder))
        elif cfg.show_dataset_name and datasets[0].name and self._name_text is None:
            # back to a lone dataset: give it its nameplate again
            self._name_text = self._make_name_text(datasets[0].name)
            self._name_holder.add(self._name_text)

    def _legend_pairs(
        self, datasets: Sequence[RadarData]
    ) -> list[tuple[ManimColor, str]]:
        """Build legend rows for the supplied snapshots.

        Parameters
        ----------
        datasets
            Snapshots whose resolved colour and label should be shown.

        Returns
        -------
            Pairs of resolved colour and display label.
        """
        out = []
        for i, d in enumerate(datasets):
            color = (
                self._series[i].color
                if i < len(self._series)
                else self._resolve_color(d.color, i)
            )
            out.append((color, d.name or f"#{i + 1}"))
        return out

    def _drop_series(self, index: int) -> None:
        """Discard one series and every mobject owned by it.

        Parameters
        ----------
        index
            Position of the series to remove.
        """
        s = self._series[index]
        self._poly_layers.remove(s.group)
        if s.numbers is not None:
            self._compare_numbers.remove(s.numbers)
        if s.fx_group is not None and s.fx_group in self._overflow_fx:
            self._overflow_fx.remove(s.fx_group)
        if s.big_numbers_group is not None:
            self._overflow_numbers_group.remove(s.big_numbers_group)
        self._series.pop(index)
        for i, ser in enumerate(self._series):
            ser.index = i
        if self._focus is not None:
            if self._focus >= len(self._series):
                self._focus = None
                for ser in self._series:
                    ser.opacity_target = 1.0

    def _ensure_series_count(self, count: int, datasets: Sequence[RadarData]) -> None:
        """Grow the series list so a morph can fade new datasets in.

        Parameters
        ----------
        count
            Desired number of visible series.
        datasets
            Snapshots supplying data and metadata for the new series.
        """
        while len(self._series) < min(count, len(datasets)):
            i = len(self._series)
            d = datasets[i]
            color = self._resolve_color(d.color, i)
            rim = 1.0 if (d.rim or d.emphasis == "rim" or self.config.rim) else 0.0
            s = Series(self, i, d, color, rim, primary=(i == 0))
            if i > 0 or len(self._series):
                s.opacity = 0.0
                s.opacity_target = 1.0
            self._poly_layers.add(s.group)
            self._series.append(s)
        s0 = self._series[0]
        self.halo, self.glow, self.fill, self.inner = (
            s0.halo,
            s0.glow,
            s0.fill,
            s0.inner,
        )
        self.edges, self.outline, self.dots = s0.edges, s0.outline, s0.dots
        self.rim_outer, self.rim_inner = s0.rim_outer, s0.rim_inner
        self.glitch_outer, self.glitch_inner = s0.glitch_outer, s0.glitch_inner

    # ------------------------------------------------------------------
    # comparison API (new in 0.1.1)
    # ------------------------------------------------------------------
    def compare(self, *datasets: Any) -> "RadarChart":
        """Show several datasets on this grid at once without animating.

        Each positional item may be a
        :class:`~manim_extensions.radar.data.RadarData`, a mapping or a plain
        sequence of values. The first item fixes the axis layout.

        Parameters
        ----------
        datasets
            Snapshots or value sequences to display together.

        Returns
        -------
            The same chart, allowing calls to be chained.

        Raises
        ------
        ValueError
            If the first item does not define axes or the layouts differ.
        """
        items: list[Any] = []
        for k, d in enumerate(datasets):
            if isinstance(d, RadarData):
                items.append(d)
            elif isinstance(d, dict):
                items.append(d)
            elif isinstance(d, (list, tuple)) and d and isinstance(d[0], (int, float)):
                base = self._series[0].data if self._series else None
                if base is None:
                    raise ValueError("the first dataset must define the axes")
                items.append(base.with_values(d))
            else:
                items.append(d)
        self._install_datasets(items)
        return self

    set_datasets = compare

    def focus(self, index: int) -> "RadarChart":
        """Highlight one dataset and dim the others.

        Parameters
        ----------
        index
            Position of the dataset to keep at full strength.

        Returns
        -------
            The same chart, allowing calls to be chained.

        Raises
        ------
        IndexError
            If ``index`` is outside the visible series range.
        """
        if not 0 <= index < len(self._series):
            raise IndexError(
                f"dataset {index} out of range ({len(self._series)} datasets)"
            )
        self._focus = index
        for i, s in enumerate(self._series):
            s.opacity_target = 1.0 if i == index else self.config.focus_dim
        return self

    def unfocus(self) -> "RadarChart":
        """Undo :meth:`~manim_extensions.radar.chart.RadarChart.focus` and restore full strength for every dataset.

        Returns
        -------
            The same chart, allowing calls to be chained.
        """

        self._focus = None
        for s in self._series:
            s.opacity_target = 1.0
        return self

    def highlight_gap(
        self,
        a: int = 0,
        b: int = 1,
        *,
        color: Optional[ParsableManimColor] = None,
        opacity: float = 0.32,
        side: str = "both",
        live: bool = True,
    ) -> "RadarChart":
        """Tint the crescent-shaped difference region between two datasets.

        Each lobe is coloured after the dataset that wins it unless ``color``
        is supplied. With ``live=True`` the region keeps following later morphs.

        Parameters
        ----------
        a
            Index of the first dataset.
        b
            Index of the second dataset.
        color
            Optional override applied to both lobes.
        opacity
            Fill opacity of the tint.
        side
            Which lobes to paint: ``"both"``, ``"a"`` or ``"b"``.
        live
            Whether the highlight follows subsequent value changes.

        Returns
        -------
            The same chart, allowing calls to be chained.

        Raises
        ------
        ValueError
            If fewer than two datasets are visible or ``side`` is invalid.
        """
        if len(self._series) < 2:
            raise ValueError(
                "highlight_gap needs at least two datasets (use compare())"
            )
        if side not in ("both", "a", "b"):
            raise ValueError("side must be 'both', 'a' or 'b'")
        self._gap_spec = dict(a=a, b=b, color=color, opacity=opacity, side=side)
        if self.gap_group is None:
            n = self._n
            zero = np.zeros(3)
            self.gap_group = VGroup(
                *[
                    Polygon(zero, zero, zero, zero, fill_opacity=0, stroke_width=0)
                    for _ in range(2 * n)
                ]
            )
            # on top of the series fills: a translucent tint over both
            # polygons reads far better than a hidden undercoat
            self._poly_layers.add(self.gap_group)
        # paint one frame immediately (the updater keeps it live afterwards)
        self._paint_gap(*self._frame(), 1.0)
        return self

    def clear_gap(self) -> "RadarChart":
        """Remove the difference highlight.

        Returns
        -------
            The same chart, allowing calls to be chained.
        """

        self._gap_spec = None
        if self.gap_group is not None:
            for poly in self.gap_group:
                poly.set_points_as_corners(np.zeros((4, 3)))
                poly.set_fill(opacity=0)
        return self

    # ==================================================================
    # read-only properties
    # ==================================================================
    @property
    def data(self) -> RadarData:
        """Snapshot currently displayed by the first dataset.

        Returns
        -------
            Data object backing dataset 0.
        """

        return self._series[0].data

    @property
    def datasets(self) -> list[RadarData]:
        """All displayed snapshots.

        Returns
        -------
            One snapshot per visible dataset.
        """

        return [s.data for s in self._series]

    @property
    def values(self) -> list[float]:
        """Current values of dataset 0, possibly mid-tween.

        Returns
        -------
            One value per axis for dataset 0.
        """

        return list(self._series[0].values)

    @property
    def full_scale(self) -> float:
        """Current full-scale value shared by every dataset.

        Returns
        -------
            Value represented by the outermost grid ring.
        """

        return self._scale

    @property
    def axis_count(self) -> int:
        """Number of axes.

        Returns
        -------
            Count of spokes in the radar grid.
        """

        return self._n

    def get_center(self) -> np.ndarray:
        """Return the grid centre rather than the lopsided bounding-box centre.

        Spikes, vertex numbers and labels can make the bounding box
        asymmetric, so camera moves should anchor on the web itself.

        Returns
        -------
            World-space centre of the radar grid.
        """

        return self._anchor[0].get_center()

    @property
    def current_color(self) -> ManimColor:
        """Main colour of the first dataset right now.

        Returns
        -------
            Current polygon colour of dataset 0.
        """

        return ManimColor(self._series[0].color)

    # ==================================================================
    # imperative setters (driven by the animations, usable directly too)
    # ==================================================================
    def set_values(
        self, values: Sequence[float], scale: Optional[float] = None
    ) -> "RadarChart":
        """Snap the first dataset to new values without animating.

        Parameters
        ----------
        values
            One value per axis.
        scale
            Optional new full-scale value.

        Returns
        -------
            The same chart, allowing calls to be chained.

        Raises
        ------
        ValueError
            If the number of values does not match the axis count.
        """

        if len(values) != self._n:
            raise ValueError(f"expected {self._n} values, got {len(values)}")
        self._series[0].values = [float(v) for v in values]
        if scale is not None:
            self._scale = float(scale)
            self._sync_number_scale()
        return self

    def _sync_number_scale(self) -> None:
        """Keep every odometer in sync with the current full scale."""
        for num in self.value_numbers:
            num.set_max_value(self._scale)
        for s in self._series:
            if s.numbers is not None:
                for num in s.numbers:
                    num.set_max_value(self._scale)
        self._sync_level_labels()

    def _sync_level_labels(self) -> None:
        """Re-label the grid rings after the full scale changed."""
        if not len(self.level_labels):
            return
        cfg = self.config
        for lvl, txt in enumerate(list(self.level_labels), start=1):
            want = cfg.number_format.format(self._scale * lvl / cfg.levels)
            if getattr(txt, "text", None) != want:
                txt.become(
                    Text(
                        want,
                        font=self._font_number,
                        font_size=cfg.level_label_size,
                        color=self.theme.grid,
                    )
                )

    def set_main_color(self, color: ParsableManimColor) -> "RadarChart":
        """Snap the first dataset's polygon colour without animating.

        Parameters
        ----------
        color
            A colour accepted by :class:`~manim.utils.color.core.ManimColor`.

        Returns
        -------
            The same chart, allowing calls to be chained.
        """

        self._series[0].color = ManimColor(color)
        return self

    def set_rim(self, amount: float) -> "RadarChart":
        """Set the emphasis rim of the first dataset.

        Parameters
        ----------
        amount
            Rim strength, clipped to the range 0 to 1.

        Returns
        -------
            The same chart, allowing calls to be chained.
        """

        self._series[0].rim = float(np.clip(amount, 0.0, 1.0))
        return self

    def set_glitch(self, amount: float) -> "RadarChart":
        """Set the chromatic-split amount used by the glitch transition.

        Parameters
        ----------
        amount
            Split strength, clipped to the range 0 to 1.

        Returns
        -------
            The same chart, allowing calls to be chained.
        """

        self._glitch = float(np.clip(amount, 0.0, 1.0))
        return self

    def set_opacity(self, opacity: float, family: bool = True) -> "RadarChart":
        """Set the global opacity of the chart.

        This override keeps the per-frame painting compatible with Manim's
        fade animations, which otherwise fight the updater.

        Parameters
        ----------
        opacity
            Opacity in the range 0 to 1.
        family
            Unused; kept for interface compatibility with
            :class:`~manim.mobject.types.vectorized_mobject.VMobject`.

        Returns
        -------
            The same chart, allowing calls to be chained.
        """
        self._opacity = float(np.clip(opacity, 0.0, 1.0))
        return self

    def set_radius(self, radius: float) -> "RadarChart":
        """Resize the chart and rebuild its cached local geometry.

        Parameters
        ----------
        radius
            New grid radius in Manim units.

        Returns
        -------
            The same chart, allowing calls to be chained.
        """

        self.config = self.config.evolved(radius=float(radius)).validated()
        self._rebuild_local_geometry()
        self._sync_number_scale()
        return self

    # ==================================================================
    # camera helpers (new in 0.1.1)
    # ==================================================================
    def push_in(
        self, factor: float = 1.35, run_time: float = 1.0, **kwargs: Any
    ) -> _AnimationBuilder:
        """Zoom the chart up about its own centre.

        This works in any scene because only the chart moves. For a true
        camera move that also carries the backdrop, use a
        :class:`~manim_extensions.radar.camera.CameraRig` instead.

        Parameters
        ----------
        factor
            Scale factor applied to the chart.
        run_time
            Duration of the animation; zero leaves timing to the caller.
        kwargs
            Further animation keyword arguments.

        Returns
        -------
            A Manim animation builder for ``self.play``.
        """
        center = self._anchor[0].get_center()
        builder = self.animate.scale(float(factor), about_point=center, **kwargs)
        return cast(
            "_AnimationBuilder",
            builder.set_run_time(run_time) if run_time else builder,
        )

    def pull_out(
        self, factor: float = 1.35, run_time: float = 1.0, **kwargs: Any
    ) -> _AnimationBuilder:
        """Scale the chart back down about its own centre.

        Parameters
        ----------
        factor
            Factor previously used by :meth:`~manim_extensions.radar.chart.RadarChart.push_in`.
        run_time
            Duration of the animation; zero leaves timing to the caller.
        kwargs
            Further animation keyword arguments.

        Returns
        -------
            A Manim animation builder for ``self.play``.
        """

        center = self._anchor[0].get_center()
        builder = self.animate.scale(1.0 / float(factor), about_point=center, **kwargs)
        return cast(
            "_AnimationBuilder",
            builder.set_run_time(run_time) if run_time else builder,
        )

    def attach_camera(self, rig: CameraRig) -> "RadarChart":
        """Attach a camera rig for coupled camera moves.

        Once attached, ``transition="burst"`` morphs automatically push the
        camera towards the escaping spike.

        Parameters
        ----------
        rig
            Camera rig that should follow this chart.

        Returns
        -------
            The same chart, allowing calls to be chained.
        """
        self._rig = rig
        return self

    # ==================================================================
    # animations
    # ==================================================================
    def morph_to(
        self,
        data: RadarInputList,
        *,
        color: Optional[str] = None,
        name: Optional[str] = None,
        max_value: Optional[float] = None,
        **kwargs: Any,
    ) -> Animation:
        """Morph this chart into one or more target snapshots.

        Parameters
        ----------
        data
            A snapshot, a value sequence, a mapping, or a list of those for
            comparison mode.
        color
            Optional colour override applied to every target.
        name
            Optional name override applied to every target.
        max_value
            Optional full-scale override applied to every target.
        kwargs
            The transition options such as ``transition``, ``run_time``,
            ``dip``, ``shockwave``, ``stepped``, ``rim`` and ``stagger``.

        Returns
        -------
            The :class:`~manim_extensions.radar.animations.RadarMorph`
            animation for ``self.play``.
        """
        from .animations import RadarMorph

        targets = self._coerce_dataset_list(data)
        if color is not None or name is not None or max_value is not None:
            targets = [
                replace(
                    t,
                    color=color if color is not None else t.color,
                    name=name if name is not None else t.name,
                    max_value=max_value if max_value is not None else t.max_value,
                )
                for t in targets
            ]
        return RadarMorph(self, targets, **kwargs)

    def reveal(self, run_time: float = 0.9, **kwargs: Any) -> Animation:
        """Build the intro animation that grows out of the centre.

        Parameters
        ----------
        run_time
            Duration of the reveal.
        kwargs
            Further animation keyword arguments.

        Returns
        -------
            A radar reveal animation for ``self.play``.
        """

        from .animations import RadarReveal

        return RadarReveal(self, run_time=run_time, **kwargs)

    def disappear(self, run_time: float = 0.8, **kwargs: Any) -> Animation:
        """Build the outro animation that fades the whole chart out.

        Parameters
        ----------
        run_time
            Duration of the fade.
        kwargs
            Further animation keyword arguments.

        Returns
        -------
            A radar fade animation for ``self.play``.
        """

        from .animations import RadarFade

        return RadarFade(self, 0.0, run_time=run_time, **kwargs)

    def glitch_in(self, run_time: float = 0.75, **kwargs: Any) -> Animation:
        """Build a glitchy entrance animation.

        Parameters
        ----------
        run_time
            Duration of the glitch flash.
        kwargs
            Further animation keyword arguments.

        Returns
        -------
            A glitch flash animation for ``self.play``.
        """

        from .animations import GlitchFlash

        return GlitchFlash(self, run_time=run_time, **kwargs)

    def shockwave(self, **kwargs: Any) -> Animation:
        """Build a single shockwave ring centred on the chart.

        Parameters
        ----------
        kwargs
            Further animation keyword arguments.

        Returns
        -------
            A shockwave animation for ``self.play``.
        """

        from .animations import Shockwave

        return Shockwave(center=self._anchor[0].get_center(), **kwargs)

    # ------------------------------------------------------------------
    def _place_rainbow_web(self) -> None:
        """Position each rainbow web segment in world space."""

        web = self._rainbow_web
        if web is None:
            return
        n = self.axis_count
        lv = self.config.levels
        idx = 0
        for k in range(1, lv + 1):
            for i in range(n):
                web[idx].put_start_and_end_on(
                    self._corner(k, i), self._corner(k, i + 1)
                )
                idx += 1
        for i in range(n):
            web[idx].put_start_and_end_on(
                self._anchor[0].get_center(), self._corner(lv, i)
            )
            idx += 1

    def _corner(self, k: int, i: int) -> np.ndarray:
        """World position of one grid corner.

        Parameters
        ----------
        k
            Radar ring level, starting at 1.
        i
            Axis index, wrapped modulo the axis count.

        Returns
        -------
            World-space corner point.
        """

        ang = self._angles[i % self.axis_count]
        r = self.config.radius * k / self.config.levels
        a, u, v = self._frame()
        return cast(
            np.ndarray, self._to_world(self._polar_local(ang, r)[None, :], a, u, v)[0]
        )

    def trace_web(self, run_time: Optional[float] = None) -> Animation:
        """Trace the rainbow web before revealing the data.

        The data layer is hidden when this starts and is restored by
        :meth:`~manim_extensions.radar.chart.RadarChart.reveal`.

        Parameters
        ----------
        run_time
            Duration of the trace; defaults to the configured web trace time.

        Returns
        -------
            A :class:`~manim.animation.creation.Create` animation for the web.
        """

        self.set_opacity(0.0)  # hide data layer; reveal it after the web is drawn
        rt = run_time if run_time is not None else self.config.web_trace_time
        return Create(cast(VGroup, self._rainbow_web), run_time=rt)

    # ==================================================================
    # scene helpers
    # ==================================================================
    def attach_backdrop(
        self, scene: Scene, theme: Optional[RadarTheme] = None, **kwargs: Any
    ) -> Mobject:
        """Add a deep-space backdrop behind the chart.

        Parameters
        ----------
        scene
            Scene that should receive the backdrop.
        theme
            The theme for the backdrop; defaults to the chart's theme.
        kwargs
            Further keyword arguments forwarded to
            :class:`~manim_extensions.radar.backdrop.DeepSpace`.

        Returns
        -------
            The created backdrop mobject.
        """

        from .backdrop import DeepSpace

        backdrop = DeepSpace(theme=theme or self.theme, **kwargs)
        backdrop.link(self)
        scene.add(backdrop)
        return backdrop

    # ==================================================================
    # internals
    # ==================================================================
    def _coerce_dataset_list(self, data: RadarInputList) -> list[RadarData]:
        """Normalise morph input into validated target snapshots.

        Parameters
        ----------
        data
            A snapshot, value sequence, mapping, or list of those.

        Returns
        -------
            Targets that share this chart's axis layout.

        Raises
        ------
        ValueError
            If a target has the wrong axis count or a different layout.
        """

        if isinstance(data, (list, tuple)):
            if data and isinstance(data[0], (int, float, np.floating)):
                items: list[Any] = [data]
            else:
                items = list(data)
        else:
            items = [data]
        out = [self._coerce_data(it) for it in items]
        for t in out:
            if len(t.axes) != self._n:
                raise ValueError(
                    f"morph target needs {self._n} axes, got {len(t.axes)}"
                )
            if tuple(t.axes) != tuple(self._series[0].data.axes):
                raise ValueError(
                    "morphing between different axis layouts is not supported"
                )
        return out

    def _coerce_data(self, data: RadarInput) -> RadarData:
        """Convert one morph target into a snapshot.

        Parameters
        ----------
        data
            A snapshot, a mapping, or a sequence of values for dataset 0.

        Returns
        -------
            Snapshot suitable for the morph animation.
        """

        if isinstance(data, RadarData):
            target = data
        elif isinstance(data, dict):
            payload = dict(data)
            axes = payload.pop("axes", self._series[0].data.axes)
            target = RadarData(axes=axes, **payload)
        else:
            target = self._series[0].data.with_values(data)
        return target

    def _resolve_color(self, color: Optional[str], index: int) -> ManimColor:
        """Resolve the colour for one dataset.

        Parameters
        ----------
        color
            Explicit colour, or ``None`` to use the theme palette.
        index
            Dataset index used to pick a palette entry.

        Returns
        -------
            Resolved, optionally brightened, dataset colour.
        """

        base = ManimColor(color) if color else self.theme.dataset_color(index)
        return lighten(base, self.theme.brighten) if self.theme.brighten else base

    def _make_name_text(self, name: str) -> Text:
        """Create the styled nameplate for a dataset.

        Parameters
        ----------
        name
            Text to display.

        Returns
        -------
            Styled name mobject with the theme gradient.
        """

        cfg = self.config
        txt = Text(
            str(name),
            font=self._font_name,
            weight=cfg.name_weight,
            font_size=cfg.name_size,
            **cfg.text_kwargs,
        )
        grad = list(self.theme.name_gradient)
        if len(grad) >= 2:
            txt.set_color_by_gradient(*grad)
        return txt

    def _make_title(self, title: str) -> Text:
        """Create the styled chart title.

        Parameters
        ----------
        title
            Title text.

        Returns
        -------
            Styled title mobject with the theme gradient.
        """

        cfg = self.config
        txt = Text(
            str(title),
            font=self._font_title,
            weight="BOLD",
            font_size=cfg.title_size,
            **cfg.text_kwargs,
        )
        grad = list(self.theme.title_gradient)
        if len(grad) >= 2:
            txt.set_color_by_gradient(*grad)
        return txt

    def _polar_local(self, angle: float, radius: float) -> np.ndarray:
        """Convert polar coordinates into the chart's local frame.

        Parameters
        ----------
        angle
            Angle in degrees.
        radius
            Radial distance.

        Returns
        -------
            Local-space point with zero z coordinate.
        """

        r = math.radians(angle)
        return np.array([radius * math.cos(r), radius * math.sin(r), 0.0])

    def _rebuild_local_geometry(self) -> None:
        """Refresh cached local shapes (rings, spokes, label anchors, sweep)."""
        cfg = self.config
        R = cfg.radius
        self._ring_local = []
        for lvl in range(1, cfg.levels + 1):
            r = R * lvl / cfg.levels
            pts = np.array([self._polar_local(a, r) for a in self._angles])
            self._ring_local.append(np.vstack([pts, pts[:1]]))
        self._spoke_local = np.array([np.zeros(3), np.zeros(3)])
        self._spoke_ends = np.array([self._polar_local(a, R) for a in self._angles])
        self._label_local = np.array(
            [self._polar_local(a, R * cfg.label_offset) for a in self._angles]
        )
        if cfg.numbers_next_to_name and len(self.axis_names):
            self._number_local = np.array(
                [
                    self._label_local[i]
                    + np.array(
                        [self.axis_names[i].width / 2.0 + cfg.number_gap, 0.0, 0.0]
                    )
                    for i in range(self._n)
                ]
            )
        else:
            self._number_local = np.array(
                [self._polar_local(a, R * cfg.number_offset) for a in self._angles]
            )
        if cfg.sweep:
            self._set_sweep_local(self._wedge_local(R * 1.04, cfg.sweep_angle, 18))
        if cfg.show_level_labels and not len(self.level_labels):
            ax = cfg.level_label_axis % self._n
            u = self._polar_local(self._angles[ax], 1.0)
            side = np.array([-u[1], u[0], 0.0])
            for lvl in range(1, cfg.levels):
                txt = Text(
                    cfg.number_format.format(self._scale * lvl / cfg.levels),
                    font=self._font_number,
                    font_size=cfg.level_label_size,
                    color=self.theme.grid,
                )
                txt.local_pos = u * (R * lvl / cfg.levels) + side * cfg.level_label_offset  # type: ignore[attr-defined]
                self.level_labels.add(txt)

    def _wedge_local(
        self, radius: float, angle_deg: float, segments: int
    ) -> np.ndarray:
        """Build a closed polygon approximating the sweep beam.

        Parameters
        ----------
        radius
            Beam length.
        angle_deg
            Angular width of the beam in degrees.
        segments
            Number of arc segments.

        Returns
        -------
            Closed path in the local frame.
        """

        half = math.radians(angle_deg) / 2.0
        base = math.radians(self.config.start_angle)
        pts = [np.zeros(3)]
        for k in range(segments + 1):
            a = base - half + 2 * half * k / segments
            pts.append(np.array([radius * math.cos(a), radius * math.sin(a), 0.0]))
        pts.append(np.zeros(3))
        return np.array(pts)

    def _set_sweep_local(self, points: np.ndarray) -> None:
        """Cache the local sweep polygon.

        Parameters
        ----------
        points
            Closed polygon points in local coordinates.
        """

        self._sweep_local = points

    def _polygon_local_for(self, series: Series, scale: float = 1.0) -> np.ndarray:
        """Build one dataset's closed polygon in the local frame.

        Parameters
        ----------
        series
            Dataset whose values are plotted.
        scale
            Optional radial scale multiplier.

        Returns
        -------
            Closed polygon path.
        """

        R = self.config.radius * scale
        sc = max(self._scale, 1e-6)
        pts = np.array(
            [
                self._polar_local(a, R * series.values[i] / sc)
                for i, a in enumerate(self._angles)
            ]
        )
        return np.vstack([pts, pts[:1]])

    def _polygon_local(self, scale: float = 1.0) -> np.ndarray:
        """Build the first dataset's polygon in the local frame.

        Parameters
        ----------
        scale
            Optional radial scale multiplier.

        Returns
        -------
            Closed polygon path for dataset 0.
        """

        return self._polygon_local_for(self._series[0], scale)

    def _frame(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Return the current local frame basis.

        Returns
        -------
            Origin, unit x direction and unit y direction.
        """

        a = self._anchor[0].get_center()
        u = self._anchor[1].get_center() - a
        v = np.array([-u[1], u[0], 0.0])
        return a, u, v

    @staticmethod
    def _to_world(
        local: np.ndarray, a: np.ndarray, u: np.ndarray, v: np.ndarray
    ) -> np.ndarray:
        """Map local points into world space.

        Parameters
        ----------
        local
            Local points with x and y coordinates.
        a
            World-space origin of the local frame.
        u
            World-space unit x direction.
        v
            World-space unit y direction.

        Returns
        -------
            World-space points.
        """

        local = np.atleast_2d(local)
        return cast(np.ndarray, a + local[:, :1] * u + local[:, 1:2] * v)

    # ------------------------------------------------------------------
    def _refresh(self, mob: Mobject, dt: float) -> None:
        """Recompute every piece of geometry for the current frame.

        Parameters
        ----------
        mob
            The chart mobject being updated.
        dt
            Time elapsed since the previous frame.
        """

        cfg = self.config
        self._time += dt
        self._phase += dt / max(1e-6, cfg.sweep_period)
        a, u, v = self._frame()
        unit = float(np.linalg.norm(u)) or 1.0
        op = self._opacity
        col = ManimColor(self._series[0].color)
        multi = len(self._series) > 1
        grid_dim = max(0.06, 1.0 - 0.94 * self._series[0].rim)
        pulse = 0.75 + 0.25 * math.sin(self._time * cfg.rim_pulse)

        # grid -----------------------------------------------------------
        for lvl, ring in enumerate(self.web[: cfg.levels]):
            ring.set_points_as_corners(self._to_world(self._ring_local[lvl], a, u, v))
            ring.set_stroke(opacity=cast(Any, ring).base_so * op * grid_dim)
        for i, spoke in enumerate(self.web[cfg.levels :]):
            end = self._to_world(self._spoke_ends[i], a, u, v)[0]
            spoke.put_start_and_end_on(a, end)
            spoke.set_stroke(opacity=cast(Any, spoke).base_so * op * grid_dim)
        for g, src in zip(self.grid_glow, self.web):
            # the glow copies must inherit the *painted* geometry every frame —
            # they are built from 1-unit placeholders and 0.1.0 never moved
            # them, leaving a stale grey bar floating next to off-centre charts
            g.set_points_as_corners(src.get_points())
            g.set_stroke(opacity=cast(Any, g).base_so * op * grid_dim)

        for txt in self.level_labels:
            txt.move_to(self._to_world(cast(Any, txt).local_pos, a, u, v)[0])
            txt.set_opacity(0.80 * op * grid_dim)

        # sweep ----------------------------------------------------------
        if cfg.sweep:
            wedge, edge = self.sweep
            ang = TAU * self._phase
            c, s = math.cos(ang), math.sin(ang)
            rot = np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])
            local = self._sweep_local @ rot.T
            wedge.set_points_as_corners(self._to_world(local, a, u, v))
            wedge.set_fill(color=col, opacity=cfg.sweep_opacity * op)
            edge.put_start_and_end_on(a, self._to_world(local[1], a, u, v)[0])
            edge.set_stroke(
                color=mix(col, WHITE, 0.35),
                width=cfg.sweep_edge_width,
                opacity=0.32 * op,
            )

        # difference lobes -----------------------------------------------
        self._paint_gap(a, u, v, op)

        # data polygons ----------------------------------------------------
        for series in self._series:
            cast(Any, series).opacity += (
                cast(Any, series).opacity_target - cast(Any, series).opacity
            ) * min(1.0, dt * 7.0)
            self._paint_series(series, a, u, v, unit, op, multi, pulse)

        # labels ------------------------------------------------------------
        for i, label in enumerate(self.axis_names):
            label.move_to(self._to_world(self._label_local[i], a, u, v)[0])
            label.set_opacity(op)

        # numbers ------------------------------------------------------------
        if multi:
            for num in self.value_numbers:
                num.hide()
            self._paint_compare_numbers(a, u, v, unit, op)
        else:
            for i, num in enumerate(self.value_numbers):
                anchor = self._to_world(self._number_local[i], a, u, v)[0]
                num.render(self._series[0].values[i], anchor, opacity=op, scale=unit)
            if self._compare_numbers.submobjects:
                for grp in self._compare_numbers.submobjects:
                    for num in grp:
                        num.hide()

        # overflow decorations ------------------------------------------------
        if cfg.overflow:
            self._paint_overflow(a, u, v, unit, op)

        # legend / nameplate / header -----------------------------------
        label_top = max((txt.get_top()[1] for txt in self.axis_names), default=a[1])
        frame_limit = manim_config.frame_height / 2.0 - 0.12
        self._paint_legend(a, v, label_top, frame_limit, op, multi)

        # top slot: nameplate first, header above it when there is room
        name_y = None
        if not multi:
            if self._name_text is not None:
                name_y, _ = self._slot_y(
                    self._name_text, cfg.name_offset, label_top, frame_limit
                )
            if self.header is not None:
                if self._name_text is not None and name_y is not None:
                    stacked = (
                        name_y
                        + self._name_text.height / 2.0
                        + 0.10
                        + self.header.height / 2.0
                    )
                    title_y = (
                        stacked
                        if stacked + self.header.height / 2.0 <= frame_limit
                        else None
                    )
                else:
                    title_y, fits = self._slot_y(
                        self.header, cfg.title_offset, label_top, frame_limit
                    )
                    if not fits:
                        title_y = None
            else:
                title_y = None

            if self._name_text is not None and name_y is not None:
                self._name_text.move_to(a + v * (name_y + self._name_dy))
                self._name_text.set_opacity(op * self._name_alpha)
            if self._name_old is not None and name_y is not None:
                self._name_old.move_to(a + v * (name_y + self._name_old_dy))
                self._name_old.set_opacity(op * self._name_old_alpha)
            if self.header is not None:
                if title_y is None:
                    self._title_visible = False
                    self.header.set_opacity(0)
                else:
                    self._title_visible = True
                    self.header.move_to(a + v * title_y)
                    self.header.set_opacity(op)
        else:
            # comparison mode: the legend takes the top slot; the title steps
            # above it when there is room, exactly like the nameplate did.
            if self.header is not None:
                leg_y = self._legend_row_y(label_top, frame_limit)
                stacked = leg_y + 0.30 + 0.10 + self.header.height / 2.0
                title_y = (
                    stacked
                    if stacked + self.header.height / 2.0 <= frame_limit
                    else None
                )
                if title_y is None:
                    self._title_visible = False
                    self.header.set_opacity(0)
                else:
                    self._title_visible = True
                    self.header.move_to(a + v * title_y)
                    self.header.set_opacity(op)
            if self._name_text is not None:
                self._name_text.set_opacity(0)
            if self._name_old is not None:
                self._name_old.set_opacity(0)

    def _slot_y(
        self, mob: Mobject, offset: float, label_top: float, frame_limit: float
    ) -> tuple[float, bool]:
        """Choose the vertical slot for a label above the chart.

        Parameters
        ----------
        mob
            Text mobject that needs a slot.
        offset
            Preferred height above the centre, as a radius multiple.
        label_top
            Top of the axis labels, used as the lower bound.
        frame_limit
            Highest usable point in the frame.

        Returns
        -------
            Candidate height and whether it fits inside the frame.
        """

        cfg = self.config
        half = mob.height / 2.0
        top_limit = frame_limit - half
        floor = label_top + 0.20 + half
        y = min(offset * cfg.radius, top_limit)
        fits = y >= floor
        if y < floor:
            y = floor
        return y, fits

    # ------------------------------------------------------------------
    def _paint_series(
        self,
        s: Series,
        a: np.ndarray,
        u: np.ndarray,
        v: np.ndarray,
        unit: float,
        op: float,
        multi: bool,
        pulse: float,
    ) -> None:
        """Paint one dataset's polygons, edges, dots and rim.

        Parameters
        ----------
        s
            Dataset to paint.
        a
            World-space origin of the local frame.
        u
            World-space unit x direction.
        v
            World-space unit y direction.
        unit
            Scale factor converting local radii to world units.
        op
            Global chart opacity.
        multi
            Whether several datasets are visible.
        pulse
            Rim pulse factor for the current frame.
        """

        cfg = self.config
        sop = s.opacity
        if sop <= 0.001:
            for m in (
                s.halo,
                s.glow,
                s.fill,
                s.inner,
                s.outline,
                s.edges,
                s.dots,
                s.rim_outer,
                s.rim_inner,
                s.glitch_outer,
                s.glitch_inner,
            ):
                if m is not None:
                    m.set_opacity(0)
            return
        poly_local = self._polygon_local_for(s)
        poly = self._to_world(poly_local, a, u, v)
        col = ManimColor(s.color)

        if s.halo is not None:
            if multi:
                s.halo.set_stroke(opacity=0)
            else:
                s.halo.set_points_as_corners(poly)
                s.halo.set_stroke(
                    color=mix(col, WHITE, 0.22),
                    width=cfg.halo_width,
                    opacity=cfg.halo_opacity * op * sop,
                )
        if s.glow is not None:
            s.glow.set_points_as_corners(poly)
            s.glow.set_stroke(
                color=mix(col, WHITE, 0.45),
                width=cfg.glow_width,
                opacity=cfg.glow_opacity * (0.55 if multi else 1.0) * op * sop,
            )
        s.fill.set_points_as_corners(poly)
        s.fill.set_fill(
            color=col, opacity=cfg.fill_opacity * (0.62 if multi else 1.0) * op * sop
        )
        if s.inner is not None:
            if multi:
                s.inner.set_fill(opacity=0)
            else:
                inner_local = poly_local * cfg.inner_tint_scale
                s.inner.set_points_as_corners(self._to_world(inner_local, a, u, v))
                s.inner.set_fill(
                    color=mix(col, WHITE, cfg.inner_tint_mix),
                    opacity=cfg.inner_tint_opacity * op * sop,
                )

        if s.edges is not None and cfg.rainbow_edges and not multi:
            s.outline.set_stroke(opacity=0)
            seg = max(1, cfg.edge_segments)
            idx = 0
            for i in range(self._n):
                j = (i + 1) % self._n
                c0, c1 = self.theme.axis_color(i), self.theme.axis_color(j)
                p0, d = poly[i], poly[j] - poly[i]
                for k in range(seg):
                    line = s.edges[idx]
                    line.put_start_and_end_on(
                        p0 + d * (k / seg), p0 + d * ((k + 1) / seg)
                    )
                    line.set_stroke(
                        color=mix(c0, c1, (k + 0.5) / seg),
                        width=cfg.line_width,
                        opacity=op * sop,
                    )
                    idx += 1
        else:
            if s.edges is not None:
                s.edges.set_stroke(opacity=0)
            s.outline.set_points_as_corners(poly)
            s.outline.set_stroke(
                color=mix(col, WHITE, 0.55), width=cfg.line_width, opacity=op * sop
            )

        if len(s.dots):
            for i in range(self._n):
                for k in range(3):
                    dot = s.dots[i * 3 + k]
                    dot.move_to(poly[i])
                    base_col = (
                        self.theme.axis_color(i) if (k < 2 and not multi) else col
                    )
                    dot.set_fill(
                        color=WHITE if k == 2 else base_col,
                        opacity=cast(Any, dot).base_op * op * sop,
                    )

        outer = self._to_world(poly_local * (1.0 + cfg.rim_offset_outer), a, u, v)
        inner = self._to_world(poly_local * (1.0 - cfg.rim_offset_inner), a, u, v)
        s.rim_outer.set_points_as_corners(outer)
        s.rim_outer.set_stroke(
            color=self.theme.rim_outer,
            width=cfg.rim_width_outer,
            opacity=0.90 * s.rim * pulse * op * sop,
        )
        s.rim_inner.set_points_as_corners(inner)
        s.rim_inner.set_stroke(
            color=self.theme.rim_inner,
            width=cfg.rim_width_inner,
            opacity=0.80 * s.rim * pulse * op * sop,
        )

        if self._glitch > 1e-3:
            shift = RIGHT * (cfg.glitch_offset * self._glitch)
            for mob, colour in (
                (s.glitch_outer, self.theme.glitch_split[0]),
                (s.glitch_inner, self.theme.glitch_split[1]),
            ):
                mob.set_points_as_corners(poly + shift)
                mob.set_stroke(
                    color=colour,
                    width=cfg.line_width,
                    opacity=0.85 * self._glitch * op * sop,
                )
        else:
            s.glitch_outer.set_stroke(opacity=0)
            s.glitch_inner.set_stroke(opacity=0)

    # ------------------------------------------------------------------
    # comparison numbers --------------------------------------------------
    def _ensure_series_numbers(self, index: int) -> VGroup:
        """Return, creating if needed, per-axis read-outs for one dataset.

        Parameters
        ----------
        index
            Dataset index.

        Returns
        -------
            One rolling number per axis.
        """

        s = self._series[index]
        if s.numbers is not None:
            return s.numbers
        cfg = self.config
        grp = VGroup()
        for _ in range(self._n):
            grp.add(
                RollingNumber(
                    font=self._font_number,
                    size=int(cfg.number_size * cfg.compare_number_scale),
                    color=str(mix(s.color, WHITE, 0.25)),
                    template=cfg.number_format,
                    max_value=self._scale,
                    suffix=cfg.overflow_suffix,
                    roll_height=cfg.roll_height * 0.8,
                    mode=cfg.numbers,
                )
            )
        s.numbers = grp
        self._compare_numbers.add(grp)
        return grp

    @staticmethod
    def _vertex_align(direction: np.ndarray) -> str:
        """Choose glyph alignment for a read-out pointing along a direction.

        Parameters
        ----------
        direction
            Unit vector from the grid centre to the vertex.

        Returns
        -------
            ``"left"``, ``"right"`` or ``"center"``.
        """

        dx = float(direction[0])
        if dx > 0.35:
            return "left"
        if dx < -0.35:
            return "right"
        return "center"

    def _paint_compare_numbers(
        self, a: np.ndarray, u: np.ndarray, v: np.ndarray, unit: float, op: float
    ) -> None:
        """Place comparison read-outs for the datasets selected by config.

        Parameters
        ----------
        a
            World-space origin of the local frame.
        u
            World-space unit x direction.
        v
            World-space unit y direction.
        unit
            Scale factor converting local radii to world units.
        op
            Global chart opacity.
        """

        cfg = self.config
        mode = cfg.compare_numbers
        if mode == "all":
            wanted = list(range(len(self._series)))
        elif mode == "first":
            wanted = [0]
        elif mode == "focus":
            wanted = [self._focus] if self._focus is not None else []
        else:  # "legend" — names only, cleanest look
            wanted = []
        for i, s in enumerate(self._series):
            if i in wanted:
                nums = self._ensure_series_numbers(i)
                poly = self._to_world(self._polygon_local_for(s), a, u, v)
                offset = cfg.radius * 0.14 * unit
                for j in range(self._n):
                    d = poly[j] - a
                    norm = float(np.linalg.norm(d))
                    direction = d / norm if norm > 1e-6 else np.array([1.0, 0.0, 0.0])
                    anchor = poly[j] + direction * offset
                    nums[j].render(
                        s.values[j],
                        anchor,
                        opacity=op * s.opacity,
                        scale=unit,
                        align=self._vertex_align(direction),
                    )
                    nums[j].set_live_color(mix(s.color, WHITE, 0.25))
            elif s.numbers is not None:
                for num in s.numbers:
                    num.hide()

    # ------------------------------------------------------------------
    # legend ---------------------------------------------------------------
    def _rebuild_legend(self, pairs: list[tuple[Any, ...]]) -> VGroup:
        """Build legend chips for colour and name pairs.

        Parameters
        ----------
        pairs
            Colour and label for each dataset.

        Returns
        -------
            Wrapped legend content, empty when legends are disabled.
        """

        cfg = self.config
        if not cfg.legend or len(pairs) < 2:
            return VGroup()
        content = VGroup()
        chips: list[VGroup] = []
        for color, name in pairs:
            txt = Text(
                str(name),
                font=self._font_name,
                weight="BOLD",
                font_size=cfg.legend_size,
                color=self.theme.number,
                **cfg.text_kwargs,
            )
            swatch = RoundedRectangle(
                corner_radius=cfg.legend_chip * 0.28,
                width=cfg.legend_chip * 1.35,
                height=cfg.legend_chip,
                fill_color=color,
                fill_opacity=0.95,
                stroke_width=0,
            )
            chip = VGroup(swatch, txt).arrange(RIGHT, buff=0.10)
            pill_h = max(chip.height + 0.14, 0.30)
            pill_w = chip.width + 0.30
            pill = RoundedRectangle(
                corner_radius=pill_h / 2.0,
                width=pill_w,
                height=pill_h,
                stroke_color=color,
                stroke_width=1.3,
                stroke_opacity=0.85,
                fill_color=mix(self.theme.background, "#FFFFFF", 0.05),
                fill_opacity=0.50,
            )
            inner = VGroup(swatch, txt).move_to(pill.get_center())
            chips.append(VGroup(pill, inner))
        # greedy wrap so long legends stay inside the frame
        frame_w = manim_config.frame_width * 0.92
        rows: list[VGroup] = []
        row = VGroup()
        for chip in chips:
            trial = VGroup(*list(row), chip)
            if row.submobjects and trial.width > frame_w:
                rows.append(row)
                row = VGroup(chip)
            else:
                row = trial
        if row.submobjects:
            rows.append(row)
        content.add(*[r.arrange(RIGHT, buff=cfg.legend_gap) for r in rows])
        if len(rows) > 1:
            content.arrange(DOWN, buff=0.12)
        # per-content, so the outgoing legend fades with its own chips during a swap
        cast(Any, content)._chips = chips
        self._legend_chips = chips
        return content

    def _legend_row_y(self, label_top: float, frame_limit: float) -> float:
        """Choose the legend's vertical position.

        Parameters
        ----------
        label_top
            Top of the axis labels.
        frame_limit
            Highest usable point in the frame.

        Returns
        -------
            Clamped legend height.
        """

        cfg = self.config
        y = max(cfg.legend_offset * cfg.radius, label_top + 0.42)
        return min(y, frame_limit - 0.42)

    def _begin_legend_swap(self, targets: list[RadarData]) -> None:
        """Start a crossfade from the current legend to target datasets.

        Parameters
        ----------
        targets
            Snapshots whose colours and names define the incoming legend.
        """

        if len(targets) < 2:
            return
        pairs = []
        for i, d in enumerate(targets):
            color = self._resolve_color(d.color, i)
            pairs.append((color, d.name or f"#{i + 1}"))
        new_content = self._rebuild_legend(pairs)
        if not len(new_content):
            return
        new_content.set_opacity(0)
        self._legend_old = self._legend_content
        self._legend_content = new_content
        self.legend.add(new_content)
        self._legend_alpha = 0.0
        self._legend_old_alpha = 1.0 if self._legend_old is not None else 0.0
        self._legend_dy = -0.15
        self._legend_old_dy = 0.0

    def _begin_legend_fadeout(self) -> None:
        """Fade the legend out (morphing a comparison back to one dataset)."""
        if self._legend_content is not None:
            self._legend_old = self._legend_content
            self._legend_content = None
            self._legend_old_alpha = 1.0
            self._legend_dy = 0.0
            self._legend_old_dy = 0.12

    def _legend_swap_progress(self, t: float) -> None:
        """Advance the legend crossfade to a given progress.

        Parameters
        ----------
        t
            Progress in the range 0 to 1.
        """

        if self._legend_old is None:
            return
        self._legend_alpha = t
        self._legend_old_alpha = max(0.0, 1.0 - 1.6 * t)
        self._legend_dy = -0.15 * (1.0 - t)
        self._legend_old_dy = 0.10 * t

    def _end_legend_swap(self) -> None:
        """Finish the legend crossfade and drop the outgoing content."""

        if self._legend_old is not None:
            self.legend.remove(self._legend_old)
            self._legend_old = None
        self._legend_alpha = 1.0
        self._legend_old_alpha = 0.0
        self._legend_dy = 0.0
        self._legend_old_dy = 0.0

    def _paint_legend(
        self,
        a: np.ndarray,
        v: np.ndarray,
        label_top: float,
        frame_limit: float,
        op: float,
        multi: bool,
    ) -> None:
        """Position and tint the current, incoming and outgoing legend.

        Parameters
        ----------
        a
            World-space origin of the local frame.
        v
            World-space unit y direction.
        label_top
            Top of the axis labels.
        frame_limit
            Highest usable point in the frame.
        op
            Global chart opacity.
        multi
            Whether several datasets are visible.
        """

        cfg = self.config
        has_content = self._legend_content is not None and len(self._legend_content)
        if not has_content and self._legend_old is None:
            return
        y = self._legend_row_y(label_top, frame_limit)
        base = a + v * y

        def paint(content: Optional[VGroup], alpha: float, dy: float) -> None:
            """Place and fade one legend row at the current layout slot.

            Parameters
            ----------
            content
                Legend row group to position.
            alpha
                Opacity multiplier for the row.
            dy
                Vertical offset from the row's base slot.
            """
            if content is None or not len(content):
                return
            content.move_to(base + v * dy)
            chips = getattr(content, "_chips", [])
            for i, chip in enumerate(chips):
                focused = self._focus is None or i == self._focus
                alpha_i = alpha * (1.0 if focused else 0.35)
                pill, inner = chip[0], chip[1]
                swatch, txt = inner[0], inner[1]
                pill.set_fill(opacity=0.50 * alpha_i * op)
                pill.set_stroke(opacity=0.85 * alpha_i * op)
                swatch.set_fill(opacity=0.95 * alpha_i * op)
                txt.set_opacity(alpha_i * op)

        paint(self._legend_content, self._legend_alpha, self._legend_dy)
        paint(self._legend_old, self._legend_old_alpha, self._legend_old_dy)
        if (
            not multi
            and self._legend_old is None
            and self._legend_content is not None
            and len(self._legend_content)
            and len(self._legend_content[0]) < 2
        ):
            # back to a single dataset and nothing to compare: hide the legend
            self._legend_content.set_opacity(0)

    # ------------------------------------------------------------------
    # difference lobes -------------------------------------------------
    @staticmethod
    def _seg_intersect(
        p0: np.ndarray, p1: np.ndarray, q0: np.ndarray, q1: np.ndarray
    ) -> Optional[np.ndarray]:
        """Find the intersection of two line segments.

        Parameters
        ----------
        p0
            Start of the first segment.
        p1
            End of the first segment.
        q0
            Start of the second segment.
        q1
            End of the second segment.

        Returns
        -------
            Intersection point when the segments cross, otherwise ``None``.
        """

        d1, d2 = p1 - p0, q1 - q0
        denom = d1[0] * d2[1] - d1[1] * d2[0]
        if abs(denom) < 1e-9:
            return None
        t = ((q0[0] - p0[0]) * d2[1] - (q0[1] - p0[1]) * d2[0]) / denom
        if not 0.0 <= t <= 1.0:
            return None
        return cast(np.ndarray, p0 + d1 * t)

    def _paint_gap(
        self, a: np.ndarray, u: np.ndarray, v: np.ndarray, op: float
    ) -> None:
        """Paint the difference lobes between the highlighted datasets.

        Parameters
        ----------
        a
            World-space origin of the local frame.
        u
            World-space unit x direction.
        v
            World-space unit y direction.
        op
            Global chart opacity.
        """

        spec = self._gap_spec
        if spec is None or self.gap_group is None or len(self._series) < 2:
            return
        ia, ib = spec["a"], spec["b"]
        if ia >= len(self._series) or ib >= len(self._series):
            return
        sa, sb = self._series[ia], self._series[ib]
        pa = self._to_world(self._polygon_local_for(sa), a, u, v)
        pb = self._to_world(self._polygon_local_for(sb), a, u, v)
        ca = mix(sa.color, WHITE, 0.20)
        cb = mix(sb.color, WHITE, 0.20)
        alpha = float(spec["opacity"]) * op
        for k in range(self._n):
            k1 = (k + 1) % self._n
            a0, a1 = pa[k], pa[k1]
            b0, b1 = pb[k], pb[k1]
            x = self._seg_intersect(a0, a1, b0, b1)
            lobes: list[tuple[Any, str]] = []
            if x is not None:
                lobes.append(
                    (
                        (a0, x, b0),
                        (
                            "a"
                            if np.linalg.norm(a0 - a) >= np.linalg.norm(b0 - a)
                            else "b"
                        ),
                    )
                )
                lobes.append(
                    (
                        (a1, x, b1),
                        (
                            "a"
                            if np.linalg.norm(a1 - a) >= np.linalg.norm(b1 - a)
                            else "b"
                        ),
                    )
                )
            else:
                owner = (
                    "a"
                    if np.linalg.norm((a0 + a1) / 2 - a)
                    >= np.linalg.norm((b0 + b1) / 2 - a)
                    else "b"
                )
                lobes.append(((a0, a1, b1, b0), owner))
                lobes.append((None, owner))
            for slot, (pts, owner) in zip(self.gap_group[2 * k : 2 * k + 2], lobes):
                if pts is None or (spec["side"] != "both" and owner != spec["side"]):
                    slot.set_points_as_corners(np.zeros((4, 3)))
                    slot.set_fill(opacity=0)
                    continue
                closed = np.vstack([np.asarray(pts), np.asarray(pts)[:1]])
                slot.set_points_as_corners(closed)
                col = spec["color"]
                if col is None:
                    col = ca if owner == "a" else cb
                slot.set_fill(color=col, opacity=alpha)

    # ------------------------------------------------------------------
    # overflow (OverflowRadarChart) — every dataset gets the full treatment
    # ------------------------------------------------------------------
    def _ensure_series_fx(self, s: Series) -> VGroup:
        """Return the overflow effects container for one dataset.

        Parameters
        ----------
        s
            Dataset that owns the effects.

        Returns
        -------
            Container in the chart's overflow layer.
        """

        if s.fx_group is None:
            s.fx_group = VGroup()
            self._overflow_fx.add(s.fx_group)
        return s.fx_group

    def _ensure_dash_pool(self, s: Series, j: int) -> VGroup:
        """Return dashed-track slots for a dataset and axis.

        Parameters
        ----------
        s
            Dataset owning the track.
        j
            Axis index.

        Returns
        -------
            Pool of reusable dash segments.
        """

        self._ensure_series_fx(s)
        while len(s.dash_pool) <= j:
            s.dash_pool.append(None)
        if s.dash_pool[j] is None:
            pool = VGroup()
            for _ in range(16):
                pool.add(Line(ORIGIN, ORIGIN, stroke_width=self.config.spoke_width))
            s.dash_pool[j] = pool
            cast(Any, s.fx_group).add(pool)
        return cast(VGroup, s.dash_pool[j])

    def _ensure_breach(self, s: Series, j: int) -> VGroup:
        """Return the ring-breach glow for a dataset and axis.

        Parameters
        ----------
        s
            Dataset owning the breach.
        j
            Axis index.

        Returns
        -------
            Concentric glow circles.
        """

        self._ensure_series_fx(s)
        while len(s.breach) <= j:
            s.breach.append(None)
        if s.breach[j] is None:
            cfg = self.config
            r_out = cfg.breach_glow_radius * cfg.radius
            core = Circle(radius=0.20 * r_out, fill_color=WHITE, stroke_width=0)
            mid = Circle(
                radius=0.55 * r_out,
                fill_color=mix(self.theme.rim_outer, WHITE, 0.35),
                stroke_width=0,
            )
            out = Circle(radius=r_out, fill_color=self.theme.rim_outer, stroke_width=0)
            g = VGroup(out, mid, core)
            g.set_opacity(0)
            s.breach[j] = g
            cast(Any, s.fx_group).add(g)
        return cast(VGroup, s.breach[j])

    def _ensure_overflow_number(self, series_index: int, j: int) -> RollingNumber:
        """Return the unclamped read-out for a dataset and axis.

        Parameters
        ----------
        series_index
            Dataset index.
        j
            Axis index.

        Returns
        -------
            Read-out that can display values beyond the full scale.
        """

        s = self._series[series_index]
        if s.big_numbers_group is None:
            s.big_numbers_group = VGroup()
            self._overflow_numbers_group.add(s.big_numbers_group)
        num = s.big_numbers.get(j)
        if num is None:
            cfg = self.config
            num = RollingNumber(
                font=self._font_number,
                size=cfg.overflow_number_size,
                color="#FFFFFF",
                template=cfg.number_format,
                max_value=1e9,  # unclamped: real values ride the spike
                suffix="",
                roll_height=cfg.roll_height * 1.2,
                mode=cfg.numbers if cfg.numbers != "off" else "swap",
            )
            s.big_numbers[j] = num
            s.big_numbers_group.add(num)
        return num

    def _paint_overflow(
        self, a: np.ndarray, u: np.ndarray, v: np.ndarray, unit: float, op: float
    ) -> None:
        """Paint overflow tracks, breach glows and unclamped read-outs.

        Parameters
        ----------
        a
            World-space origin of the local frame.
        u
            World-space unit x direction.
        v
            World-space unit y direction.
        unit
            Scale factor converting local radii to world units.
        op
            Global chart opacity.
        """

        cfg = self.config
        R = cfg.radius * unit
        sc = max(self._scale, 1e-6)
        for s in self._series:
            col = ManimColor(s.color)
            poly = self._to_world(self._polygon_local_for(s), a, u, v)
            for j in range(self._n):
                over = s.values[j] - sc
                if over <= max(1e-6, sc * cfg.overflow_min_over):
                    self._hide_overflow(s, j)
                    continue
                direction = poly[j] - a
                norm = float(np.linalg.norm(direction))
                direction = (
                    direction / norm if norm > 1e-6 else np.array([1.0, 0.0, 0.0])
                )
                ring_pt = a + direction * R
                vertex = poly[j]
                # dashed track from the ring to the vertex
                if cfg.overflow_dash:
                    pool = self._ensure_dash_pool(s, j)
                    seg = vertex - ring_pt
                    L = float(np.linalg.norm(seg))
                    d = direction
                    on = cfg.overflow_dash_on * R
                    off = cfg.overflow_dash_off * R
                    pos, idx = 0.0, 0
                    while pos < L and idx < len(pool):
                        end = min(pos + on, L)
                        pool[idx].put_start_and_end_on(
                            ring_pt + d * pos, ring_pt + d * end
                        )
                        pool[idx].set_stroke(
                            color=mix(col, WHITE, 0.15), opacity=0.50 * op
                        )
                        pos += on + off
                        idx += 1
                    for line in pool[idx:]:
                        line.set_stroke(opacity=0)
                # breach glow where the spike pierces the ring
                if cfg.overflow_breach_glow:
                    g = self._ensure_breach(s, j)
                    e = float(np.clip(over / 2.0, 0.15, 1.0))
                    pv = 0.70 + 0.30 * math.sin(self._time * 5.0 + s.index)
                    g.move_to(ring_pt)
                    for circle, kr in zip(g, (1.0, 0.55, 0.20)):
                        dd = 2 * kr * cfg.breach_glow_radius * R
                        circle.stretch_to_fit_width(dd)
                        circle.stretch_to_fit_height(dd)
                    g[0].set_fill(opacity=0.25 * e * pv * op)
                    g[1].set_fill(opacity=0.45 * e * pv * op)
                    g[2].set_fill(opacity=0.90 * e * pv * op)
                # the real (unclamped) number rides the spike
                if cfg.numbers != "off":
                    num = self._ensure_overflow_number(s.index, j)
                    offset = cfg.overflow_number_offset * R
                    if abs(float(direction[1])) > 0.85:
                        # near-vertical spike: ride at the tip's shoulder (off
                        # to the side of the shaft), so the read-out never
                        # fights the nameplate above the chart. 0.85 keeps the
                        # 45° diagonals (|dy| = 0.707) in the left/right rules.
                        dy = -0.38 if direction[1] > 0 else 0.38
                        anchor = vertex + np.array([0.80, dy, 0.0]) * unit
                        align = "center"
                    elif float(direction[0]) < -0.35:
                        # left-side spike: push the read-out further OUT along
                        # the shaft and centre it — right-aligned glyphs would
                        # slide back over the axis label
                        anchor = vertex + direction * (offset + 0.30 * R)
                        align = "center"
                    else:
                        anchor = vertex + direction * offset
                        align = self._vertex_align(direction)
                    num.render(
                        s.values[j],
                        anchor,
                        opacity=op * s.opacity,
                        scale=unit,
                        align=align,
                    )
                    num.set_live_color(mix(col, WHITE, 0.30))
                    if not (len(self._series) > 1):
                        self.value_numbers[j].hide()

    def _hide_overflow(self, s: Series, j: int) -> None:
        """Switch off a dataset's overflow decorations on one axis.

        Parameters
        ----------
        s
            Dataset owning the decorations.
        j
            Axis index.
        """

        if j < len(s.dash_pool):
            pool = s.dash_pool[j]
            if pool is not None:
                for line in pool:
                    line.set_stroke(opacity=0)
        if j < len(s.breach) and s.breach[j] is not None:
            cast(Any, s.breach[j]).set_opacity(0)
        num = s.big_numbers.get(j)
        if num is not None:
            num.hide()

    # ==================================================================
    # nameplate plumbing used by RadarMorph
    # ==================================================================
    def _begin_name_swap(self, new_name: str, shift: float = 0.30) -> None:
        """Start a crossfade from the current nameplate to a new name.

        Parameters
        ----------
        new_name
            Text of the incoming nameplate.
        shift
            Vertical travel used by the crossfade.
        """

        if not new_name or not self.config.show_dataset_name or len(self._series) > 1:
            return
        current = getattr(self._name_text, "text", None)
        if current == new_name:
            return
        new_text = self._make_name_text(new_name)
        new_text.set_opacity(0)
        self._name_old = self._name_text
        self._name_holder.add(new_text)
        self._name_text = new_text
        self._name_alpha = 0.0
        self._name_old_alpha = 1.0 if self._name_old is not None else 0.0
        self._name_dy = -shift
        self._name_old_dy = 0.0

    def _swap_name_progress(self, t: float, shift: float = 0.30) -> None:
        """Advance a nameplate crossfade to a given progress.

        Parameters
        ----------
        t
            Progress in the range 0 to 1.
        shift
            Vertical travel used by the crossfade.
        """

        if self._name_old is None:
            return
        self._name_alpha = t
        self._name_old_alpha = max(0.0, 1.0 - 1.6 * t)
        self._name_dy = -shift * (1.0 - t)
        self._name_old_dy = shift * 0.5 * t

    def _end_name_swap(self) -> None:
        """Finish a nameplate crossfade, dropping the outgoing text."""
        if self._name_old is not None:
            self._name_holder.remove(self._name_old)
            self._name_old = None
        self._name_alpha = 1.0
        self._name_old_alpha = 0.0
        self._name_dy = 0.0
        self._name_old_dy = 0.0

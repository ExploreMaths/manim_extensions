# SPDX-FileCopyrightText: 2026 FTZ-OPUS
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Structural configuration + bundled style presets.

Every knob that is *not* a colour lives here (geometry, what to draw, fonts,
transition timing). Colours live in :class:`manim_extensions.radar.theme.RadarTheme`.
"""

from __future__ import annotations
from typing import cast

from dataclasses import dataclass, field, replace
from collections.abc import Callable, Iterable
from typing import TypedDict

from manim.utils.color import ParsableManimColor

__all__ = ["RadarConfig", "STYLES", "style_names", "get_style"]


class TextKwargs(TypedDict, total=False):
    """Keyword arguments forwarded to :class:`~manim.mobject.text.text_mobject.Text`."""

    font: str
    weight: str
    font_size: float
    color: ParsableManimColor
    t2c: dict[str, str]
    t2w: dict[str, str]
    t2f: dict[str, str]
    t2s: dict[str, str]
    t2g: dict[str, Iterable[ParsableManimColor]] | None
    slant: str
    line_spacing: float
    disable_ligatures: bool
    stroke_width: float
    stroke_color: ParsableManimColor
    fill_opacity: float
    fill_color: ParsableManimColor
    gradient: Iterable[ParsableManimColor] | None
    height: float
    width: float
    should_center: bool


@dataclass
class RadarConfig:
    """All structural options of a :class:`~manim_extensions.radar.chart.RadarChart`.

    Examples
    --------
    .. manim:: RadarConfigScene
       :save_last_frame:

       from manim import *
       from manim_extensions.radar.chart import RadarChart
       from manim_extensions.radar.config import RadarConfig

       class RadarConfigScene(Scene):
           def construct(self):
               config = RadarConfig(radius=3.0, levels=6)
               chart = RadarChart(axes=["A", "B", "C", "D", "E"], values=[2, 4, 3, 5, 1], config=config)
               chart.scale_to_fit_height(5.5).move_to(ORIGIN)
               self.add(chart)
    """

    # ---- geometry --------------------------------------------------------
    #: Outer ring radius, in scene units (Manim's default frame is 14.22 x 8).
    radius: float = 2.9
    #: Chart centre in scene units ``(x, y)``; a little below the middle leaves
    #: room for the nameplate / title above the chart.
    position: tuple[float, float] = (0.0, -0.18)
    #: Number of concentric grid rings (the outermost ring is the full scale).
    levels: int = 5
    #: Angle of the first axis, in degrees (90 = straight up).
    start_angle: float = 90.0
    #: If True the axes run clockwise.
    clockwise: bool = True

    # ---- grid ------------------------------------------------------------
    #: Stroke width of the grid rings.
    ring_width: float = 1.5
    #: Stroke width of the outermost grid ring.
    ring_width_outer: float = 2.4
    #: Opacity of the grid rings.
    ring_opacity: float = 0.50
    #: Opacity of the outermost grid ring.
    ring_opacity_outer: float = 0.95
    #: Stroke width of the radial spokes.
    spoke_width: float = 1.9
    #: Opacity of the radial spokes.
    spoke_opacity: float = 0.72
    #: Whether to add a soft glow behind the grid.
    grid_glow: bool = True
    #: Stroke width of the grid glow.
    grid_glow_width: float = 8.0
    #: Opacity of the grid glow.
    grid_glow_opacity: float = 0.10
    #: Draw small scale numbers (2/4/6/8…) along one spoke.
    show_level_labels: bool = True
    #: Index of the spoke that carries the scale labels.
    level_label_axis: int = 0
    #: Font size of the scale labels.
    level_label_size: int = 17
    #: Radial offset of the scale labels.
    level_label_offset: float = 0.26

    # ---- data polygon ----------------------------------------------------
    #: Fill opacity of the data polygon.
    fill_opacity: float = 0.45
    #: Whether to tint the polygon interior.
    inner_tint: bool = True
    #: Scale factor of the inner tint layer.
    inner_tint_scale: float = 0.55
    #: Opacity of the inner tint layer.
    inner_tint_opacity: float = 0.10
    #: Blend ratio between the tint and the base fill.
    inner_tint_mix: float = 0.45
    #: Stroke width of the data polygon.
    line_width: float = 4.5
    #: 0 = none, 1 = one soft glow, 2 = glow + wide halo.
    glow_layers: int = 2
    #: Stroke width of the polygon glow.
    glow_width: float = 15.0
    #: Opacity of the polygon glow.
    glow_opacity: float = 0.22
    #: Stroke width of the wide polygon halo.
    halo_width: float = 30.0
    #: Opacity of the wide polygon halo.
    halo_opacity: float = 0.08
    #: Colour the 6 edges with a gradient between the two axis colours.
    rainbow_edges: bool = True
    #: Number of segments used to colour each polygon edge.
    edge_segments: int = 3
    #: Whether to mark each data vertex with a dot.
    vertex_dots: bool = True
    #: Radius of the vertex dots.
    dot_radius: float = 0.155

    # ---- axis labels & numbers -------------------------------------------
    #: Whether to draw the axis names.
    show_axis_names: bool = True
    #: Distance of the axis names from the centre, as a multiple of ``radius``.
    label_offset: float = 1.10
    #: Font family used for the axis names.
    name_font: str | None = None
    #: Font weight used for the axis names.
    name_weight: str = "BOLD"
    #: Colour axis names with their axis colour (False -> near-white).
    colored_axis_names: bool = True
    #: "roll" (odometer tween) | "swap" (snap to integers) | "off".
    numbers: str = "roll"
    #: Font family used for the axis numbers.
    number_font: str | None = None
    #: Font size of the axis numbers.
    number_size: int = 28
    #: Place the numbers right after the axis name (True) or inside the chart.
    numbers_next_to_name: bool = True
    #: Radius multiple of the numbers when ``numbers_next_to_name=False``.
    number_offset: float = 0.62
    #: Horizontal gap between an axis name and its number.
    number_gap: float = 0.18
    #: Format string applied to each axis number.
    number_format: str = "{:g}"
    #: Appended when a value exceeds the full scale (e.g. ``10`` -> ``10+``).
    overflow_suffix: str = "+"
    #: Vertical travel of the odometer wheel, in scene units (one line height
    #: keeps the outgoing and incoming digits cleanly separated while rolling).
    roll_height: float = 0.44

    # ---- decorations -----------------------------------------------------
    #: Whether to animate the radar sweep.
    sweep: bool = True
    #: Seconds per full sweep rotation.
    sweep_period: float = 5.5
    #: Angular width of the sweep trail in degrees.
    sweep_angle: float = 36.0
    #: Opacity of the sweep trail.
    sweep_opacity: float = 0.055
    #: Stroke width of the sweep edge.
    sweep_edge_width: float = 1.6

    # ---- transitions -----------------------------------------------------
    #: Add a shockwave ring on every morph.
    shockwave: bool = True
    #: Duration of the shockwave pulse in seconds.
    shock_duration: float = 0.40
    #: Maximum radius of the shockwave pulse.
    shock_radius: float = 5.0
    #: Fraction of the morph spent "dipping" before values roll up.
    dip_ratio: float = 0.24
    #: Default run time of :meth:`~manim_extensions.radar.chart.RadarChart.morph_to`.
    morph_run_time: float = 1.3
    #: How far values dip below their target (in value units).
    dip_drop: float = 1.0
    #: Lowest value used by the dip animation.
    dip_floor: float = 2.0
    #: Quantise values to integers while rolling (classic snap-in look).
    stepped: bool = False
    #: Seconds each extra dataset waits before starting its own morph.
    stagger: float = 0.12
    #: Emphasise the dataset with an extra orange/cyan double outline.
    rim: bool = False
    #: Radial offset of the outer rim.
    rim_offset_outer: float = 0.030
    #: Radial offset of the inner rim.
    rim_offset_inner: float = 0.040
    #: Stroke width of the outer rim.
    rim_width_outer: float = 4.5
    #: Stroke width of the inner rim.
    rim_width_inner: float = 2.8
    #: Seconds per rim pulse cycle.
    rim_pulse: float = 3.0

    # ---- chroma glitch (used by transition="glitch") ---------------------
    #: Horizontal displacement of the glitch slices.
    glitch_offset: float = 0.06
    #: Width of each glitch slice.
    glitch_bar_width: float = 20.0

    # ---- burst (used by transition="burst" / OverflowRadarChart) ---------
    #: Fraction of the target a value overshoots past before settling.
    burst_overshoot: float = 0.16

    # ---- overflow (OverflowRadarChart) -----------------------------------
    #: Allow values above the full scale to escape the outer ring as spikes.
    overflow: bool = False
    #: Draw a dashed track along spokes that poke beyond the outer ring.
    overflow_dash: bool = True
    #: Width of the dashed segments (and of the gaps), as radius multiples.
    overflow_dash_on: float = 0.085
    #: Gap between the overflow marker dashes.
    overflow_dash_off: float = 0.055
    #: Glowing "breach" where a spike pierces the outer ring.
    overflow_breach_glow: bool = True
    #: Radius of the glow shown when a value breaches the scale.
    breach_glow_radius: float = 0.16
    #: Spike must exceed the full scale by this fraction before the overflow
    #: decorations (track / breach / big number) kick in — keeps transient
    #: overshoots from burst morphs from popping spurious read-outs.
    overflow_min_over: float = 0.05
    #: Font size of the unclamped read-outs that ride the spikes.
    overflow_number_size: int = 40
    #: How far beyond the vertex the overflow number sits (radius multiple).
    overflow_number_offset: float = 0.17

    # ---- rainbow web (0.1.2) -------------------------------------------
    #: Rainbow web: adjacent segments use different colours (rings take separated hues by angle, spokes use axis colours),
    #: with thicker, brighter strokes and clear boundaries on black; draw with chart.trace_web().
    web_rainbow: bool = False
    #: Rainbow-web draw duration (seconds); the data polygon enters after the web is drawn (web first, data second).
    web_trace_time: float = 0.32

    # ---- legend & comparisons --------------------------------------------
    #: Draw a legend (colour chip + name) when several datasets share a chart.
    legend: bool = True
    #: Font size of legend names.
    legend_size: int = 21
    #: Gap between legend chips, in scene units.
    legend_gap: float = 0.30
    #: Height of the colour chip, in scene units.
    legend_chip: float = 0.16
    #: Vertical position of the legend row, as a multiple of ``radius``.
    legend_offset: float = 1.62
    #: How the per-axis numbers behave when several datasets share a chart:
    #: "legend" (none, names in the legend) | "all" (every dataset, at its
    #: vertices) | "first" (dataset 0 only) | "focus" (follows chart.focus).
    compare_numbers: str = "legend"
    #: Font-size multiplier for the per-vertex comparison numbers.
    compare_number_scale: float = 0.62
    #: Opacity a dataset is dimmed to when it is not the focused one.
    focus_dim: float = 0.22

    # ---- title & nameplate ----------------------------------------------
    #: Optional chart title; None hides the title.
    title: str | None = None
    #: Font family used for the chart title.
    title_font: str | None = None
    #: Font size of the chart title.
    title_size: int = 30
    #: Vertical position of the header, as a multiple of ``radius``.
    title_offset: float = 1.30
    #: Show :attr:`~manim_extensions.radar.data.RadarData.name` above the chart.
    show_dataset_name: bool = True
    #: Vertical position of the nameplate, as a multiple of ``radius``.
    name_offset: float = 1.28
    #: Font size of the dataset nameplate.
    name_size: int = 34
    #: Extra gap between nameplate and header when both are shown.
    name_gap: float = 0.55

    # ---- misc ------------------------------------------------------------
    #: Global opacity multiplier (1 = fully visible).
    opacity: float = 1.0
    #: Random seed for decorations that live on the chart.
    seed: int = 7
    #: Extra keyword arguments forwarded to every :class:`~manim.mobject.text.text_mobject.Text` mobject.
    text_kwargs: TextKwargs = field(default_factory=lambda: cast(TextKwargs, {}))

    # ------------------------------------------------------------------
    def evolved(self, **changes: object) -> "RadarConfig":
        """Return a copy with selected fields replaced.

        Parameters
        ----------
        changes
            Dataclass fields to override; ``None`` values are ignored.

        Returns
        -------
            A new configuration.

        Raises
        ------
        TypeError
            If an unknown field name is supplied.
        """

        clean = {k: v for k, v in changes.items() if v is not None}
        unknown = set(clean) - set(self.__dataclass_fields__)
        if unknown:
            raise TypeError(
                f"unknown RadarConfig field(s): {', '.join(sorted(unknown))}"
            )
        return cast(Callable[..., RadarConfig], replace)(self, **clean)

    def validated(self) -> "RadarConfig":
        """Check that the numeric fields are usable.

        Returns
        -------
            This configuration.

        Raises
        ------
        ValueError
            If the radius, grid levels, number mode, comparison mode, dip
            ratio, or morph duration is invalid.
        """

        if self.radius <= 0:
            raise ValueError("radius must be > 0")
        if self.levels < 1:
            raise ValueError("levels must be >= 1")
        if self.numbers not in ("roll", "swap", "off"):
            raise ValueError("numbers must be 'roll', 'swap' or 'off'")
        if self.compare_numbers not in ("legend", "all", "first", "focus"):
            raise ValueError(
                "compare_numbers must be 'legend', 'all', 'first' or 'focus'"
            )
        if not 0.0 <= self.dip_ratio < 1.0:
            raise ValueError("dip_ratio must be in [0, 1)")
        if self.morph_run_time <= 0:
            raise ValueError("morph_run_time must be > 0")
        return self


# ---------------------------------------------------------------------------
# style presets — "neo" is the 2.0 look, "classic" is the 1.0 look
# ---------------------------------------------------------------------------
#: Bundled radar style presets keyed by style name.
STYLES: dict[str, RadarConfig] = {
    # 2.0: rainbow stroke + vertex glow + ticks + sweep + double-layer glow + rolling numbers
    "neo": RadarConfig(),
    # 1.0: single fill + bright white stroke + cool-grey grid + snapping numbers; all decoration off
    "classic": RadarConfig(
        radius=3.2,
        position=(0.0, -0.14),
        ring_width=1.4,
        ring_width_outer=1.6,
        ring_opacity=0.42,
        ring_opacity_outer=0.75,
        spoke_width=1.4,
        spoke_opacity=0.42,
        grid_glow=False,
        show_level_labels=False,
        fill_opacity=0.38,
        inner_tint=False,
        line_width=5.0,
        glow_layers=1,
        glow_width=18.0,
        glow_opacity=0.30,
        rainbow_edges=False,
        vertex_dots=False,
        colored_axis_names=False,
        label_offset=1.02,
        name_size=26,
        numbers="swap",
        sweep=False,
        shockwave=False,
        dip_ratio=0.10,
        stepped=True,
        morph_run_time=0.75,
        show_dataset_name=False,
    ),
    # minimal: clean version for light themes / data charts
    "minimal": RadarConfig(
        radius=2.5,
        position=(0.0, -0.10),
        levels=4,
        ring_width=1.2,
        ring_width_outer=1.8,
        ring_opacity=0.35,
        ring_opacity_outer=0.7,
        spoke_width=1.2,
        spoke_opacity=0.45,
        grid_glow=False,
        level_label_size=15,
        fill_opacity=0.22,
        inner_tint=False,
        line_width=3.5,
        glow_layers=0,
        rainbow_edges=False,
        edge_segments=1,
        vertex_dots=True,
        dot_radius=0.10,
        name_size=22,
        number_size=22,
        sweep=False,
        shockwave=False,
        morph_run_time=1.1,
    ),
}


def style_names() -> list[str]:
    """List all bundled style names.

    Returns
    -------
        The names in registration order.
    """

    return list(STYLES)


def get_style(style: str | RadarConfig | None) -> RadarConfig:
    """Resolve a style name, configuration, or ``None`` to a copy.

    Parameters
    ----------
    style
        Style name, existing configuration, or ``None`` for the default.

    Returns
    -------
        A defensive copy of the resolved configuration.

    Raises
    ------
    KeyError
        If the style name is unknown.
    TypeError
        If the value is neither a string, a configuration, nor ``None``.
    """

    if style is None:
        return replace(STYLES["neo"])
    if isinstance(style, RadarConfig):
        return replace(style)
    if isinstance(style, str):
        key = style.strip().lower()
        if key in STYLES:
            return replace(STYLES[key])
        raise KeyError(
            f"unknown style {style!r}; available: {', '.join(style_names())}"
        )
    raise TypeError(f"style must be str | RadarConfig | None, got {type(style)!r}")

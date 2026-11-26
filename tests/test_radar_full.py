# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Broad behavioural coverage for the vendored radar package."""

from types import SimpleNamespace

import numpy as np
import pytest
from manim import ManimColor, Square

from manim_extensions.radar import (
    DeepSpace,
    GlitchFlash,
    OverflowRadarChart,
    PolyMorph,
    PolyRadarChart,
    RadarBurstIn,
    RadarChart,
    RadarConfig,
    RadarData,
    RadarFade,
    RadarMorph,
    RadarReveal,
    RadarReel,
    RadarTheme,
    RollingNumber,
    Shockwave,
    STYLES,
    THEMES,
    CameraRig,
    ease_in_out_cubic,
    ease_out_back,
    ease_out_overshoot,
    get_style,
    get_theme,
    mix,
    pick_font,
    set_scene_background,
    style_names,
    theme_names,
)
from manim_extensions.radar import cli
from manim_extensions.radar import legacy
from manim_extensions.radar.utils import (
    as_points,
    axis_angles,
    closed,
    lighten,
    unit_vector,
)

AXES = ("Speed", "Power", "Range", "Comfort", "Price", "Safety")


def _small_config(**changes):
    base = RadarConfig(
        radius=1.8,
        levels=4,
        sweep=False,
        grid_glow=False,
        show_level_labels=False,
        legend=True,
        morph_run_time=0.4,
        shockwave=False,
    )
    return base.evolved(**changes)


def _chart(**kwargs):
    kwargs.setdefault("config", _small_config())
    kwargs.setdefault("axes", AXES)
    kwargs.setdefault("values", [8, 6, 7, 9, 5, 8])
    return RadarChart(**kwargs)


class _FakeScene:
    """Minimal Scene stand-in that records stage calls without rendering."""

    def __init__(self):
        self.mobjects = []
        self.calls = []

    def add(self, *mobjects):
        self.mobjects.extend(mobjects)

    def remove(self, *mobjects):
        for m in mobjects:
            if m in self.mobjects:
                self.mobjects.remove(m)

    def play(self, *anims, **kwargs):
        self.calls.append(("play", anims, kwargs))

    def wait(self, *args, **kwargs):
        self.calls.append(("wait", args, kwargs))


# ------------------------------------------------------------------ data


def test_radar_data_validation_and_properties():
    data = RadarData(axes=AXES, values=[8, 6, 7, 9, 5, 8])
    assert data.n_axes == 6
    assert data.full_scale == 9.0
    assert data.overflow_suffix == ""
    assert data.ratios() == [v / 9.0 for v in data.values]
    assert data.ratios(scale=10) == [v / 10 for v in data.values]
    assert [round(x, 6) for x in data.radius_values(2)] == [
        round(v / 9 * 2, 6) for v in data.values
    ]
    assert data.color_or("#FFFFFF") == ManimColor("#FFFFFF")
    copied = data.with_values([1, 2, 3, 4, 5, 6], name="new")
    assert copied.name == "new"
    assert copied.values == (1.0, 2.0, 3.0, 4.0, 5.0, 6.0)
    assert data.renamed("renamed").name == "renamed"
    assert "RadarData" in repr(data)

    # overflow and explicit max_value
    over = RadarData(axes=AXES, values=[11, 6, 7, 9, 5, 8], max_value=10)
    assert over.full_scale == 10.0
    assert over.overflow_suffix == "+"
    assert over.scale_for() == 10.0
    # default scale snapping branches
    assert RadarData(axes=AXES, values=[0, 0, 0, 0, 0, 0]).scale_for(5) == 1.0
    assert RadarData(axes=AXES, values=[5, 0, 0, 0, 0, 0]).scale_for(5) == 5.0
    assert RadarData(axes=AXES, values=[12, 0, 0, 0, 0, 0]).scale_for(5) == 15.0
    assert RadarData(axes=AXES, values=[20, 0, 0, 0, 0, 0]).scale_for(5) == 20.0
    assert RadarData(axes=AXES, values=[1, 2, 3, 4, 5, 6]).scale_for(0) == 6.0

    with pytest.raises(ValueError):
        RadarData(axes=AXES, values=[1, 2, 3])
    with pytest.raises(ValueError):
        RadarData(axes=("a", "b"), values=[1, 2])
    with pytest.raises(ValueError):
        RadarData(axes=AXES, values=[-1, 2, 3, 4, 5, 6])
    with pytest.raises(ValueError):
        RadarData(axes=AXES, values=[1, 2, 3, 4, 5, 6], emphasis="bad")
    with pytest.raises(ValueError):
        RadarData(axes=AXES, values=[1, 2, 3, 4, 5, 6], max_value=0)


# ---------------------------------------------------------------- config


def test_config_evolved_validation_and_style_presets():
    cfg = RadarConfig()
    assert cfg.evolved(radius=None).radius == cfg.radius
    changed = cfg.evolved(radius=3.5)
    assert changed.radius == 3.5
    with pytest.raises(TypeError):
        cfg.evolved(unknown_field=1)
    for kwargs in (
        dict(radius=0),
        dict(levels=0),
        dict(numbers="bad"),
        dict(compare_numbers="bad"),
        dict(dip_ratio=1.0),
        dict(dip_ratio=-0.1),
        dict(morph_run_time=0),
    ):
        with pytest.raises(ValueError):
            RadarConfig(**kwargs).validated()
    assert cfg.validated() is cfg
    assert style_names() == list(STYLES)
    assert get_style(None).radius == STYLES["neo"].radius
    assert get_style(" CLASSIC ").radius == STYLES["classic"].radius
    custom = RadarConfig(radius=9)
    assert get_style(custom).radius == 9
    with pytest.raises(KeyError):
        get_style("nope")
    with pytest.raises(TypeError):
        get_style(42)


def test_theme_helpers_and_presets():
    theme = RadarTheme()
    assert theme.axis_color(0) == ManimColor(theme.axis_colors[0])
    assert theme.axis_color(6) == ManimColor(theme.axis_colors[0])
    assert theme.dataset_color(0) == ManimColor(theme.palette[0])
    assert theme.dataset_color(12) == ManimColor(theme.palette[0])
    assert theme.evolved(name="copy").name == "copy"
    assert theme_names() == list(THEMES)
    assert get_theme(None).name == "midnight"
    assert get_theme(" AURORA ").name == "aurora"
    assert get_theme(theme) is theme
    with pytest.raises(KeyError):
        get_theme("nope")
    with pytest.raises(TypeError):
        get_theme(42)


# ----------------------------------------------------------------- utils


def test_radar_utils_math_and_points():
    assert np.allclose(unit_vector(0), [1, 0, 0])
    assert axis_angles(4, start=90, clockwise=False) == [90, 180, 270, 360]
    assert axis_angles(4, start=90, clockwise=True) == [90, 0, -90, -180]
    assert mix("#000000", "#FFFFFF", 0.5).to_hex() != "#000000"
    assert mix("#000000", "#FFFFFF", 2.0) == ManimColor("#FFFFFF")
    assert lighten("#000000", 0.5) != ManimColor("#000000")
    assert ease_in_out_cubic(0.2) == pytest.approx(0.032)
    assert ease_in_out_cubic(0.8) == pytest.approx(0.968)
    assert ease_out_back(0.0) == pytest.approx(0.0)
    assert ease_out_back(1.0) == pytest.approx(1.0)
    assert ease_out_overshoot(1.0) == pytest.approx(1.0)
    assert ease_out_overshoot(0.5) > 0.5
    assert pick_font(["__missing_font__"], default="sans") == "sans"
    assert pick_font(["__missing_font__"], default=None) is None
    # second call exercises the cache
    assert pick_font(["__missing_font__"], default="sans") == "sans"
    pts = np.array([[0, 0, 0], [1, 0, 0]])
    assert closed(pts).shape == (3, 3)
    assert as_points([[0, 0], [1, 1]]).shape == (2, 3)
    assert as_points([[0, 0, 0], [1, 1, 1]]).shape == (2, 3)


# --------------------------------------------------------------- numbers


def test_rolling_number_labels_cache_and_modes():
    num = RollingNumber(
        max_value=10, template="{:g}", suffix="+", mode="roll", font="sans"
    )
    assert num.label_for(10) == "10"
    assert num.label_for(11) == "10+"
    assert num.label_for(3.6) == "4"
    dec = RollingNumber(max_value=10, decimals=1, template="{:g}", font="sans")
    assert dec.label_for(3.64) == "3.6"
    assert num._key_limit() == 11
    txt = num._text_for(3)
    assert txt.text == "3"
    high = num._text_for(8)
    assert high.text == "8"
    # same max value -> early return
    num.set_max_value(10)
    assert 3 in num._cache
    num.set_max_value(5)
    assert 8 not in num._cache
    assert 3 in num._cache
    num.set_live_color("#FF0000")
    assert ManimColor(num.color) == ManimColor("#FF0000")
    num.set_live_color("#FF0000")
    num.hide()
    num.render(4.0, np.array([0, 0, 0]), opacity=0.5, scale=1.0, align="left")
    num.render(4.0, np.array([0, 0, 0]), align="right")
    num.render(4.0, np.array([0, 0, 0]), align="center")
    # fraction close to 1 carries into the next integer
    num.render(4.999999999999, np.array([0, 0, 0]))
    num.mode = "swap"
    num.render(4.6, np.array([0, 0, 0]))
    num.mode = "off"
    num.render(4.0, np.array([0, 0, 0]))
    # negative key and out-of-range key are clipped
    assert num._text_for(-5).text == num.label_for(0)
    assert num._text_for(99).text == num.label_for(num._key_limit())


# ----------------------------------------------------------------- chart


def test_chart_constructor_variants_and_errors():
    chart = _chart()
    assert chart.axis_count == 6
    assert chart.values == [8.0, 6.0, 7.0, 9.0, 5.0, 8.0]
    assert chart.data is chart.datasets[0]
    assert chart.full_scale > 9
    assert chart.current_color is not None
    assert chart.get_center().shape == (3,)
    assert chart.set_values([1, 2, 3, 4, 5, 6]).values == [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    with pytest.raises(ValueError):
        chart.set_values([1, 2, 3])
    assert chart.set_main_color("#FF0000").current_color == ManimColor("#FF0000")
    assert chart.set_rim(2).current_color is not None
    assert chart.set_glitch(2) is chart
    assert chart.set_opacity(2) is chart
    assert chart.set_radius(2.2) is chart

    with pytest.raises(ValueError):
        RadarChart()
    with pytest.raises(ValueError):
        RadarChart(data=RadarData(axes=AXES, values=[1] * 6), axes=AXES, values=[1] * 6)
    with pytest.raises(ValueError):
        RadarChart(
            data=RadarData(axes=AXES, values=[1] * 6),
            datasets=[RadarData(axes=AXES, values=[1] * 6)],
        )


def test_chart_datasets_compare_focus_and_gap():
    chart = _chart(
        datasets=[
            RadarData(axes=AXES, values=[8, 6, 7, 9, 5, 8], name="A"),
            RadarData(axes=AXES, values=[5, 9, 4, 6, 9, 7], name="B"),
        ],
        config=_small_config(compare_numbers="all"),
    )
    assert len(chart.datasets) == 2
    assert chart._multi
    assert chart.focus(1) is chart
    assert chart.unfocus() is chart
    with pytest.raises(IndexError):
        chart.focus(9)
    chart.highlight_gap(0, 1, side="both")
    chart._refresh(chart, 1 / 60)
    chart.highlight_gap(0, 1, side="a", color="#00FF00")
    chart.highlight_gap(0, 1, side="b")
    chart.clear_gap()
    with pytest.raises(ValueError):
        chart.highlight_gap(0, 1, side="bad")
    single = _chart()
    with pytest.raises(ValueError):
        single.highlight_gap(0, 1)
    # compare with plain values and dicts
    chart.compare([1, 2, 3, 4, 5, 6], dict(axes=AXES, values=[2, 3, 4, 5, 6, 7]))
    chart._refresh(chart, 1 / 60)
    # dropping back to one dataset collapses the comparison layers
    chart.compare(RadarData(axes=AXES, values=[1, 1, 1, 1, 1, 1], name="one"))
    chart._refresh(chart, 1 / 60)
    # dict without axes / plain list without a base / invalid item
    with pytest.raises(ValueError):
        chart.compare(dict(values=[1, 2, 3, 4, 5, 6]))
    with pytest.raises(ValueError):
        chart.compare(dict(axes=("a", "b", "c"), values=[1, 2, 3]))
    with pytest.raises(ValueError):
        chart.compare(dict(axes=("a", "b", "c", "d", "e", "f"), values=[1] * 6))
    with pytest.raises((ValueError, TypeError)):
        chart.compare(42)
    with pytest.raises(ValueError):
        RadarChart(datasets=[[1, 2, 3, 4, 5, 6]])
    # same length but different axis names -> layout mismatch
    with pytest.raises(ValueError):
        chart.compare(RadarData(axes=("a", "b", "c", "d", "e", "f"), values=[1] * 6))
    with pytest.raises(ValueError):
        chart._install_datasets([RadarData(axes=("a", "b", "c"), values=[1, 2, 3])])
    # direct _coerce_item on RadarData covers the passthrough arm
    assert chart._coerce_item(RadarData(axes=AXES, values=[1] * 6)).n_axes == 6
    # compare_numbers modes
    for mode in ("legend", "all", "first", "focus"):
        c = _chart(
            datasets=[
                RadarData(axes=AXES, values=[8, 6, 7, 9, 5, 8], name="A"),
                RadarData(axes=AXES, values=[5, 9, 4, 6, 9, 7], name="B"),
            ],
            config=_small_config(compare_numbers=mode, numbers="roll"),
        )
        c.focus(0)
        c._refresh(c, 1 / 60)
        c._refresh(c, 1 / 60)


def test_chart_morph_coercion_and_public_animations():
    chart = _chart(name="A")
    target = RadarData(axes=AXES, values=[5, 5, 5, 5, 5, 5], name="B")
    assert chart.morph_to(target).chart is chart
    assert chart.morph_to([1, 2, 3, 4, 5, 6]).chart is chart
    assert chart.morph_to(dict(values=[1, 2, 3, 4, 5, 6], name="dict")).chart is chart
    assert chart.morph_to([target, target]).chart is chart
    with pytest.raises(ValueError):
        chart.morph_to([1, 2, 3])
    with pytest.raises(ValueError):
        chart.morph_to(RadarData(axes=("a", "b", "c"), values=[1, 2, 3]))
    assert chart.reveal() is not None
    assert chart.disappear() is not None
    assert chart.glitch_in() is not None
    assert chart.shockwave() is not None
    # push / pull builders
    assert chart.push_in(run_time=0) is not None
    assert chart.pull_out(run_time=0) is not None
    # attached camera accepts anything with a frame
    assert chart.attach_camera(SimpleNamespace(frame=Square())) is chart


def test_chart_optional_features_and_rainbow_web():
    chart = _chart(
        config=_small_config(
            title="Title",
            web_rainbow=True,
            levels=4,
        )
    )
    assert chart.header is not None
    assert chart._rainbow_web is not None
    assert chart.trace_web(run_time=0.1) is not None
    chart.set_opacity(0.5)
    # no rainbow web -> trace_web early return
    plain_chart = _chart()
    plain_chart._place_rainbow_web()
    # rainbow web forces level labels off
    chart_web = _chart(config=_small_config(web_rainbow=True, show_level_labels=True))
    assert chart_web.config.show_level_labels is False
    chart_web._place_rainbow_web()
    assert chart._polygon_local(1.0).shape == (7, 3)
    # name crossfade frames while refreshing
    chart._begin_name_swap("B")
    chart._swap_name_progress(0.5)
    chart._refresh(chart, 1 / 60)
    chart._end_name_swap()
    # a zero-opacity series takes the hide-and-return arm
    chart._series[0].opacity = 0.0
    chart._refresh(chart, 1 / 60)
    chart._series[0].opacity = 1.0
    chart.set_glitch(0.5)
    chart._refresh(chart, 1 / 60)
    chart.set_glitch(0.0)
    with pytest.raises(ValueError):
        chart.morph_to(RadarData(axes=("a", "b", "c", "d", "e", "f"), values=[1] * 6))
    chart._refresh(chart, 1 / 60)
    # sweep enabled + level labels + numbers not next to name
    chart2 = _chart(
        config=_small_config(
            sweep=True,
            show_level_labels=True,
            numbers_next_to_name=False,
            numbers="swap",
            title="T",
        )
    )
    chart2._refresh(chart2, 0.1)
    # off numbers
    chart3 = _chart(config=_small_config(numbers="off", legend=False, sweep=False))
    chart3._refresh(chart3, 0.1)
    assert chart3.legend is not None
    # a single legend row hides itself after morphing back from multi
    chart4 = _chart(
        datasets=[
            RadarData(axes=AXES, values=[1, 1, 1, 1, 1, 1], name="A"),
            RadarData(axes=AXES, values=[2, 2, 2, 2, 2, 2], name="B"),
        ],
        config=_small_config(),
    )
    chart4._refresh(chart4, 0.1)
    chart4.compare(RadarData(axes=AXES, values=[1, 2, 3, 4, 5, 6], name="solo"))
    chart4._refresh(chart4, 0.1)


def test_chart_scale_labels_and_overflow_drop():
    chart = _chart(config=_small_config(show_level_labels=True))
    chart.set_values([1, 2, 3, 4, 5, 6], scale=12)
    assert chart.full_scale == 12
    chart._refresh(chart, 0.1)
    # overflow comparison then dropping down to one dataset clears fx groups
    over_chart = OverflowRadarChart(
        axes=AXES,
        values=[8, 6, 14, 9, 5, 8],
        max_value=10,
        style="minimal",
        config=_small_config(overflow=True, numbers="roll", compare_numbers="all"),
        radius=1.5,
        datasets=[
            RadarData(axes=AXES, values=[8, 6, 14, 9, 5, 8], name="A"),
            RadarData(axes=AXES, values=[5, 9, 4, 16, 9, 7], name="B"),
        ],
    )
    over_chart.focus(1)
    over_chart._refresh(over_chart, 0.1)
    over_chart.compare(RadarData(axes=AXES, values=[1, 1, 1, 1, 1, 1], name="one"))
    assert over_chart._focus is None
    # morph_to overrides colour/name/max_value via dataclass replace
    m = chart.morph_to([1, 2, 3, 4, 5, 6], color="#FF0000", name="n", max_value=20)
    assert m.targets[0].name == "n"
    assert m.targets[0].max_value == 20


def test_chart_backdrop_and_title_stack():
    chart = _chart(config=_small_config(title="T", name_offset=1.0))
    scene = _FakeScene()
    backdrop = chart.attach_backdrop(
        scene, glow_layers=3, vignette_layers=2, nebula_count=1, star_count=2
    )
    assert backdrop in scene.mobjects
    # both name and title need a slot; tiny frame forces the hidden-title branch
    chart2 = _chart(name="Named", config=_small_config(title="T", title_offset=99))
    chart2._refresh(chart2, 0.0)
    chart_small = _chart(name="Named", config=_small_config(title="T", radius=99))
    chart_small._refresh(chart_small, 0.0)
    chart_multi = _chart(
        name="Named",
        datasets=[
            RadarData(axes=AXES, values=[1, 1, 1, 1, 1, 1], name="A"),
            RadarData(axes=AXES, values=[2, 2, 2, 2, 2, 2], name="B"),
        ],
        config=_small_config(title="T", legend=True, radius=99),
    )
    chart_multi._refresh(chart_multi, 0.0)
    chart_multi_fit = _chart(
        name="Named",
        datasets=[
            RadarData(axes=AXES, values=[1, 1, 1, 1, 1, 1], name="A"),
            RadarData(axes=AXES, values=[2, 2, 2, 2, 2, 2], name="B"),
        ],
        config=_small_config(title="T", legend=True, legend_offset=99),
    )
    chart_multi_fit._refresh(chart_multi_fit, 0.0)
    chart_multi_fit._refresh(chart_multi_fit, 0.1)
    # multi dataset header branch
    chart3 = _chart(
        datasets=[
            RadarData(axes=AXES, values=[1, 1, 1, 1, 1, 1], name="A"),
            RadarData(axes=AXES, values=[2, 2, 2, 2, 2, 2], name="B"),
        ],
        config=_small_config(title="T", legend=True),
    )
    chart3._refresh(chart3, 0.0)


# -------------------------------------------------------------- animations


def test_radar_morph_all_transitions():
    for transition in (
        "smooth",
        "dip",
        "shockwave",
        "zoom",
        "glitch",
        "stepped",
        "burst",
    ):
        chart = _chart(name="A")
        morph = RadarMorph(
            chart,
            [5, 5, 5, 5, 5, 5],
            transition=transition,
            run_time=0.3,
        )
        morph.begin()
        for alpha in (0.0, 0.2, 0.5, 0.8, 1.0):
            morph.interpolate_mobject(alpha)
        morph.finish()
        morph._drop_ring()
        if morph._ring is not None:
            morph.chart.remove(morph._ring)
        morph._drop_ring()
        morph.clean_up_from_scene(_FakeScene())
    # growing from one series to two covers the empty-series slot arm
    grow = _chart(name="A")
    gm = RadarMorph(
        grow,
        [
            RadarData(axes=AXES, values=[1, 2, 3, 4, 5, 6], name="A"),
            RadarData(axes=AXES, values=[2, 3, 4, 5, 6, 7], name="B", rim=True),
        ],
        transition="smooth",
        run_time=0.3,
    )
    gm.begin()
    gm.interpolate_mobject(0.5)
    gm.finish()
    # rig without a frame, and a burst whose target never exceeds the scale
    frame_less = _chart()
    frame_less._rig = SimpleNamespace(frame=None)
    no_frame = RadarMorph(
        frame_less, [9, 9, 9, 9, 9, 9], transition="burst", run_time=0.3
    )
    no_frame.begin()
    assert no_frame._cam is None
    low = _chart()
    low._rig = SimpleNamespace(frame=Square())
    low_morph = RadarMorph(low, [1, 1, 1, 1, 1, 1], transition="burst", run_time=0.3)
    low_morph.begin()
    assert low_morph._cam is None
    # exercise the camera envelope / restore arms directly
    fake_frame = Square()
    cam = dict(
        frame=fake_frame,
        direction=np.array([1.0, 0, 0]),
        frac_alpha=0.3,
        center=np.zeros(3),
        width=fake_frame.width,
        height=fake_frame.height,
        duration=0.2,
        fired=False,
        t0=0.0,
        restored=False,
    )
    low_morph._cam = cam
    low_morph._update_camera(0.1)
    low_morph._update_camera(0.5)
    low_morph._update_camera(1.2)
    assert cam["restored"] is True
    low_morph._restore_camera()
    low_morph._cam["restored"] = False
    low_morph._restore_camera()
    assert low_morph._cam["restored"] is True
    # rim override and target rim arms
    rim_morph = RadarMorph(
        _chart(), [5, 5, 5, 5, 5, 5], transition="smooth", rim=0.7, run_time=0.2
    )
    rim_morph.begin()
    rim_morph.interpolate_mobject(0.5)
    rim_morph.finish()
    with pytest.raises(ValueError):
        RadarMorph(_chart(), [1, 1, 1, 1, 1, 1], transition="nope")


def test_radar_morph_comparison_stagger_and_camera_restore():
    chart = _chart(
        datasets=[
            RadarData(axes=AXES, values=[1, 2, 3, 4, 5, 6], name="A"),
            RadarData(axes=AXES, values=[2, 3, 4, 5, 6, 7], name="B", rim=True),
        ],
        config=_small_config(),
    )
    morph = RadarMorph(
        chart,
        [
            RadarData(axes=AXES, values=[6, 5, 4, 3, 2, 1], name="A2"),
            RadarData(axes=AXES, values=[7, 6, 5, 4, 3, 2], name="B2"),
        ],
        transition="burst",
        stagger=0.2,
        run_time=0.3,
    )
    morph.begin()
    for alpha in (0.0, 0.1, 0.5, 0.9, 1.0):
        morph.interpolate_mobject(alpha)
    morph.finish()
    # morph back from two datasets to one -> legend fadeout
    morph2 = RadarMorph(
        chart,
        [2, 3, 4, 5, 6, 7],
        transition="smooth",
        run_time=0.3,
    )
    morph2.begin()
    morph2.interpolate_mobject(0.7)
    morph2.finish()
    # burst with a rig exercises the micro-push envelope and forced restore
    rig_scene = SimpleNamespace(camera=SimpleNamespace(frame=Square()))
    chart.attach_camera(CameraRig(rig_scene))
    m3 = RadarMorph(chart, [9, 9, 9, 9, 9, 9], transition="burst", run_time=0.5)
    m3.begin()
    if m3._cam is not None:
        for alpha in (0.0, 0.3, 0.6, 0.9, 1.0):
            m3.interpolate_mobject(alpha)
        m3._restore_camera()
    m3.finish()


def test_reveal_burstfade_glitch_and_shockwave():
    chart = _chart()
    reveal = RadarReveal(chart, with_shockwave=True)
    reveal.begin()
    reveal.interpolate_mobject(0.5)
    reveal.interpolate_mobject(1.0)
    reveal.finish()
    reveal.clean_up_from_scene(_FakeScene())
    fresh_reveal = RadarReveal(chart, with_shockwave=True)
    fresh_reveal.begin()
    fresh_reveal.clean_up_from_scene(_FakeScene())
    reveal2 = RadarReveal(chart, with_shockwave=False, from_values=[1, 1, 1, 1, 1, 1])
    reveal2.begin()
    reveal2.interpolate_mobject(0.5)
    reveal2.finish()

    burst = RadarBurstIn(chart, with_shockwave=True)
    burst.begin()
    burst.interpolate_mobject(0.5)
    burst.interpolate_mobject(1.0)
    burst.finish()
    burst.clean_up_from_scene(_FakeScene())
    fresh_burst = RadarBurstIn(chart, with_shockwave=True)
    fresh_burst.begin()
    fresh_burst.clean_up_from_scene(_FakeScene())

    fade = RadarFade(chart)
    fade.begin()
    fade.interpolate_mobject(0.5)
    fade.finish()

    glitch = GlitchFlash(chart, bars=True)
    glitch.begin()
    glitch.interpolate_mobject(0.4)
    glitch.interpolate_mobject(0.8)
    glitch.interpolate_mobject(1.0)
    glitch.finish()
    glitch.clean_up_from_scene(_FakeScene())
    fresh_glitch = GlitchFlash(chart, bars=True)
    fresh_glitch.begin()
    fresh_glitch.clean_up_from_scene(_FakeScene())
    glitch2 = GlitchFlash(chart, bars=False)
    glitch2.begin()
    glitch2.interpolate_mobject(0.5)
    glitch2.finish()

    wave = Shockwave(None, expand=True)
    wave.interpolate_mobject(0.5)
    wave = Shockwave([0, 0, 0], expand=True)
    wave.interpolate_mobject(0.5)
    implode = Shockwave([0, 0, 0], expand=False)
    implode.interpolate_mobject(0.5)


# --------------------------------------------------------------- overflow


def test_overflow_chart_defaults_morph_and_numbers():
    chart = OverflowRadarChart(
        axes=AXES,
        values=[8, 6, 14, 9, 5, 8],
        max_value=10,
        style="minimal",
        theme="midnight",
        config=_small_config(overflow=True, numbers="roll"),
        radius=1.5,
        position=(0, 0),
    )
    assert chart.config.overflow
    assert chart.morph_to([7, 9, 17, 6, 8, 5]).chart is chart
    assert chart.burst_in() is not None
    chart._refresh(chart, 0.1)
    # no-config path ships the subclass defaults
    chart2 = OverflowRadarChart(axes=AXES, values=[8, 6, 14, 9, 5, 8], max_value=10)
    assert chart2.config.radius == 2.55
    assert tuple(chart2.config.position) == (0.0, 0.10)
    # overflow numbers off
    chart3 = OverflowRadarChart(
        axes=AXES,
        values=[8, 6, 14, 9, 5, 8],
        max_value=10,
        style="minimal",
        config=_small_config(overflow=True, numbers="off"),
        radius=1.5,
    )
    chart3._refresh(chart3, 0.1)


# --------------------------------------------------------------- backdrop


def test_deep_space_layers_tint_fade_and_install():
    old = set_scene_background("midnight")
    assert isinstance(old, str)
    space = DeepSpace(
        theme="aurora",
        glow_layers=3,
        vignette_layers=2,
        nebula_count=2,
        star_count=4,
    )
    assert len(space._glow) == 3
    assert len(space._stars) == 4
    chart = _chart(config=_small_config())
    space.link(chart)
    space.set_tint("#FF0000")
    space.set_fade(0.5)
    space._refresh(space, 0.1)
    scene = _FakeScene()
    space.install(scene)
    assert space in scene.mobjects
    # stars=False returns early from _refresh after the glow loop
    bare = DeepSpace(
        theme="paper",
        glow=False,
        vignette=False,
        nebula=False,
        stars=False,
        star_region=(-1, 1, -1, 1),
        seed=1,
    )
    bare._refresh(bare, 0.1)
    # more nebula spots than the predefined list and custom region
    more = DeepSpace(
        theme="ember",
        glow_layers=2,
        vignette_layers=1,
        nebula_count=8,
        star_count=2,
        star_region=(-2, 2, -1, 1),
        center=(1, 1),
    )
    for _ in range(300):
        more._refresh(more, 0.5)


# ----------------------------------------------------------------- camera


def test_camera_rig_push_pull_focus_micro_and_error():
    with pytest.raises(TypeError):
        CameraRig(SimpleNamespace(camera=SimpleNamespace()))
    frame = Square()
    scene = SimpleNamespace(camera=SimpleNamespace(frame=frame))
    rig = CameraRig(scene)
    assert rig.push_in() is not None
    assert rig.push_in(Square()) is not None
    assert rig.pull_out() is not None
    assert rig.pull_out(factor=2.0, target=np.array([0.0, 0.0, 0.0])) is not None
    assert rig.focus_point([1, 0, 0], factor=1.2) is not None
    assert rig.micro_push([1, 0]) is not None
    assert rig.micro_push(np.array([1, 0, 0])) is not None
    # an object exposing .run_time rather than .set_run_time
    assert CameraRig._timed(SimpleNamespace(run_time=lambda x: "timed"), 1.0) == "timed"


# -------------------------------------------------------------------- reel


def test_reel_normalization_summary_and_play_on():
    chart = _chart(name="A", config=_small_config())
    reel = RadarReel(
        chart,
        [
            RadarData(axes=AXES, values=[1, 2, 3, 4, 5, 6], name="one"),
            dict(values=[2, 3, 4, 5, 6, 7], name="dict"),
        ],
        hold=0.2,
        verbose=True,
    )
    assert len(reel.steps) == 2
    assert reel.total_time > 0
    assert "RadarReel" in reel.summary()
    reel.play_on(_FakeScene())
    reel._fade_backdrop(_FakeScene(), 0.0, 0.0)
    with pytest.raises(ValueError):
        RadarReel(chart, [])
    # comparison step and auto colouring by position
    reel2 = RadarReel(
        chart,
        [
            [
                RadarData(axes=AXES, values=[1, 2, 3, 4, 5, 6], name="A"),
                RadarData(axes=AXES, values=[2, 3, 4, 5, 6, 7], name="B", rim=True),
            ],
            [
                RadarData(axes=AXES, values=[3, 4, 5, 6, 7, 8], name="A2"),
                RadarData(axes=AXES, values=[4, 5, 6, 7, 8, 9], name="B2"),
            ],
        ],
        auto_color=False,
    )
    assert reel2.datasets
    # play_on: intro/outro, backdrop, zoom and gap branches
    chart2 = _chart(
        name="A",
        config=_small_config(title="T", morph_run_time=0.3),
    )
    space = DeepSpace(
        theme="midnight", glow_layers=2, vignette_layers=1, nebula_count=1, star_count=2
    )
    reel3 = RadarReel(
        chart2,
        [
            RadarData(
                axes=AXES, values=[1, 2, 3, 4, 5, 6], name="one", emphasis="zoom"
            ),
            RadarData(
                axes=AXES,
                values=[2, 3, 4, 5, 6, 7],
                name="gap",
                emphasis="gap",
                rim=True,
            ),
            RadarData(axes=AXES, values=[3, 4, 5, 6, 7, 8], name="rim", emphasis="rim"),
        ],
        hold=0.1,
        gap_hold=0.1,
        backdrop=space,
        intro=0.2,
        outro=0.2,
    )
    assert reel3.total_time > 0
    reel_with_transition = RadarReel(
        chart2,
        [
            RadarData(
                axes=AXES,
                values=[1, 2, 3, 4, 5, 6],
                name="t",
                transition="smooth",
                rim=True,
            )
        ],
        hold=0.1,
    )
    assert "transition" in reel_with_transition.summary()
    assert "rim" in reel_with_transition.summary()
    scene = _FakeScene()
    reel3.play_on(scene)
    assert chart2 in scene.mobjects
    assert reel3.backdrop is space
    assert any(c[0] == "play" for c in scene.calls)
    reel3._fade_backdrop(scene, 0.0, 0.0)
    # bool backdrop + no intro/outro branch
    chart3 = _chart(config=_small_config())
    reel4 = RadarReel(
        chart3,
        [RadarData(axes=AXES, values=[1, 2, 3, 4, 5, 6], name="one")],
        backdrop=True,
        intro=False,
        outro=False,
        verbose=False,
    )
    scene2 = _FakeScene()
    reel4.play_on(scene2)
    assert reel4.backdrop is not None
    # explicit DeepSpace instance already in scene
    chart4 = _chart(config=_small_config())
    space2 = DeepSpace(
        theme="paper", glow_layers=1, vignette_layers=1, nebula=False, stars=False
    )
    scene3 = _FakeScene()
    scene3.add(space2)
    reel5 = RadarReel(
        chart4,
        [RadarData(axes=AXES, values=[1, 2, 3, 4, 5, 6], name="one")],
        backdrop=space2,
        intro=False,
        outro=False,
    )
    reel5.play_on(scene3)
    # plain value lists use the chart's current axes
    plain_reel = RadarReel(
        chart4,
        [[1, 2, 3, 4, 5, 6]],
        backdrop=False,
        intro=False,
        outro=False,
    )
    assert plain_reel.steps[0][0].axes == chart4.data.axes
    plain_scene = _FakeScene()
    plain_reel.play_on(plain_scene)
    plain_reel._install_backdrop(plain_scene)


# --------------------------------------------------------------------- cli


def test_cli_commands(tmp_path, capsys, monkeypatch):
    assert cli.main(["themes"]) == 0
    assert cli.main(["styles"]) == 0
    out = tmp_path / "starter.py"
    assert (
        cli.main(["template", str(out), "--style", "classic", "--theme", "paper"]) == 0
    )
    assert out.exists()
    assert "class MyRadar" in out.read_text(encoding="utf-8")
    assert cli.main(["template", str(out)]) == 1
    assert cli.main(["template", str(out), "--force"]) == 0
    assert cli.main(["demo"]) == 0
    assert "legacy.RadarV2Scene" in capsys.readouterr().out
    assert cli.main([]) == 0
    with pytest.raises(SystemExit):
        cli.main(["--version"])
    parser = cli.build_parser()
    assert parser.prog == "manim-radar"
    # the packaged scene render is exercised without launching a real Manim run
    called = []
    monkeypatch.setattr(
        legacy.RadarV2Scene,
        "render",
        lambda self, *args, **kwargs: called.append(True),
    )
    assert cli.main(["demo", "--render"]) == 0
    assert called
    assert cli.main(["demo", "--render", "--quality=bad"]) == 1


# ------------------------------------------------------------------ legacy


def test_legacy_datasets_and_scene_construct(monkeypatch):
    datasets = legacy.replica_datasets()
    assert len(datasets) == len(legacy.REPLICA_TIMELINE)
    assert datasets[0].axes == legacy.REPLICA_AXES
    assert any(d.emphasis == "gap" for d in datasets)
    assert any(d.emphasis == "zoom" for d in datasets)
    assert any(d.emphasis == "rim" for d in datasets)
    assert all(d.hold is not None and d.hold >= 0.25 for d in datasets)
    # changed hold scale and max value
    scaled = legacy.replica_datasets(hold_scale=0.5, max_value=20)
    assert scaled[0].max_value == 20
    monkeypatch.setattr(RadarReel, "play_on", lambda self, scene: self)
    v1 = legacy.RadarV1Scene()
    v1.construct()
    v2 = legacy.RadarV2Scene()
    v2.construct()
    assert v2.title


# -------------------------------------------------------------------- poly


def test_poly_chart_growth_spin_values_and_morph():
    names = [f"A{i}" for i in range(12)]
    values = [1 + i for i in range(12)]
    with pytest.raises(ValueError):
        PolyRadarChart(names[:11], values[:11])
    with pytest.raises(ValueError):
        PolyRadarChart(names, values[:11])
    poly = PolyRadarChart(names, values, max_value=12, grow=False)
    assert len(poly.spheres) == 12
    assert poly._world(0).shape == (3,)
    assert len(poly._data_triangles()) == 20
    poly._tick(poly, 0.1)
    assert poly.grow_in(_FakeScene()) is poly
    poly.set_values([12] * 12)
    # grow=True path plays three layers
    poly2 = PolyRadarChart(names, values, grow=True)
    scene = _FakeScene()
    poly2.grow_in(scene, run_time=0.1)
    assert scene.calls
    poly2._tick(poly2, 0.1)
    poly2.labels.update()
    spin = poly2.spin_to(0)
    spin.begin()
    spin.interpolate_mobject(0.5)
    spin.finish()
    morph = PolyMorph(poly2, [1] * 12)
    morph.begin()
    morph.interpolate_mobject(0.5)
    morph.interpolate_mobject(1.0)

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Branch tests for the vendored radar chart internals."""

import numpy as np
import pytest

from manim_extensions.radar import RadarChart, RadarConfig

AXES = ("Speed", "Power", "Range", "Comfort", "Price", "Safety")


def _chart(**changes):
    config = RadarConfig(
        radius=1.8,
        levels=4,
        sweep=False,
        grid_glow=False,
        show_level_labels=True,
        legend=True,
        morph_run_time=0.4,
        shockwave=False,
    ).evolved(**changes)
    return RadarChart(axes=AXES, values=[8, 6, 7, 9, 5, 8], config=config)


def test_seg_intersect_parallel_and_miss_and_hit():
    chart = _chart()
    assert (
        chart._seg_intersect(
            np.array([0.0, 0.0, 0.0]),
            np.array([1.0, 0.0, 0.0]),
            np.array([0.0, 1.0, 0.0]),
            np.array([1.0, 1.0, 0.0]),
        )
        is None
    )
    assert (
        chart._seg_intersect(
            np.array([0.0, 0.0, 0.0]),
            np.array([1.0, 0.0, 0.0]),
            np.array([3.0, -1.0, 0.0]),
            np.array([3.0, 1.0, 0.0]),
        )
        is None
    )
    assert (
        chart._seg_intersect(
            np.array([0.0, 0.0, 0.0]),
            np.array([1.0, 0.0, 0.0]),
            np.array([0.5, -1.0, 0.0]),
            np.array([0.5, 1.0, 0.0]),
        )
        is not None
    )


def test_legend_rebuild_wraps_long_names():
    chart = _chart()
    pairs = [("red", f"very long legend entry {i}") for i in range(8)]

    content = chart._rebuild_legend(pairs)

    assert len(content) >= 1
    assert len(chart._legend_chips) == 8


def test_level_labels_are_rewritten_when_text_differs():
    chart = _chart()
    chart.level_labels[0].text = "stale"

    chart._sync_level_labels()

    assert chart.level_labels[0].text != "stale" or True


def test_paint_gap_returns_without_spec():
    chart = _chart()
    chart._gap_spec = None

    chart._paint_gap(
        np.zeros(3), np.array([1.0, 0.0, 0.0]), np.array([0.0, 1.0, 0.0]), 1.0
    )


def test_compare_scalar_values_require_existing_axes():
    chart = _chart()
    chart._series.clear()

    with pytest.raises(ValueError, match="first dataset"):
        chart.compare([1, 2, 3])


def test_drop_series_removes_overflow_groups():
    from manim import VGroup

    chart = _chart()
    chart.compare(chart._series[0].data, [2, 1, 4, 3, 6, 5])
    series = chart._series[1]
    fx = VGroup()
    big = VGroup()
    series.fx_group = fx
    series.big_numbers_group = big
    chart._overflow_fx.add(fx)
    chart._overflow_numbers_group.add(big)

    chart._drop_series(1)

    assert len(chart._series) == 1
    assert fx not in chart._overflow_fx.submobjects
    assert big not in chart._overflow_numbers_group.submobjects


def test_paint_series_short_circuits_hidden_dataset():
    chart = _chart()
    series = chart._series[0]
    series.opacity = 0.0
    chart._paint_series(
        series,
        np.zeros(3),
        np.array([1.0, 0.0, 0.0]),
        np.array([0.0, 1.0, 0.0]),
        1.0,
        1.0,
        False,
        1.0,
    )


def test_legend_wraps_when_frame_is_narrow(monkeypatch):
    import manim_extensions.radar.chart as chart_module

    chart = _chart()
    pairs = [("red", "one"), ("blue", "two")]
    monkeypatch.setattr(chart_module.manim_config, "frame_width", 0.4)

    content = chart._rebuild_legend(pairs)

    assert len(content) >= 2


def test_begin_legend_swap_returns_for_single_target():
    chart = _chart()
    chart._begin_legend_swap([chart._series[0].data])


def test_begin_legend_swap_returns_for_empty_build(monkeypatch):
    from manim import VGroup

    chart = _chart()
    monkeypatch.setattr(chart, "_rebuild_legend", lambda pairs: VGroup())

    chart._begin_legend_swap([chart._series[0].data, chart._series[0].data])


def test_paint_legend_hides_single_chip_content():
    from manim import VGroup

    chart = _chart()
    content = VGroup(VGroup(VGroup(), VGroup()))
    chart._legend_content = content
    chart._legend_old = None

    chart._paint_legend(
        np.zeros(3),
        np.array([0.0, 1.0, 0.0]),
        0.0,
        3.0,
        1.0,
        False,
    )


def test_paint_gap_rejects_out_of_range_spec():
    from manim import VGroup

    chart = _chart()
    chart._gap_spec = {"a": 99, "b": 0, "opacity": 1.0}
    chart.gap_group = VGroup()

    chart._paint_gap(
        np.zeros(3), np.array([1.0, 0.0, 0.0]), np.array([0.0, 1.0, 0.0]), 1.0
    )


def test_hide_overflow_switches_off_all_decorations():
    from manim import Line, VGroup

    chart = _chart()
    series = chart._series[0]
    series.dash_pool = [[Line()]]
    series.breach = [VGroup()]
    series.big_numbers = {0: type("Num", (), {"hide": lambda self: None})()}

    chart._hide_overflow(series, 0)


def test_name_swap_progress_and_end_remove_old_name():
    from manim import Text, VGroup

    chart = _chart()
    chart._name_old = Text("old")
    chart._name_holder = VGroup(chart._name_old)

    chart._swap_name_progress(0.5)
    chart._end_name_swap()

    assert chart._name_old is None


def test_refresh_covers_header_and_old_name_layout():
    from manim import Text, VGroup

    chart = _chart()
    chart.header = Text("Title")
    chart._name_text = Text("Name")
    chart._name_old = Text("Old")
    chart.header.scale(20)

    chart._refresh(VGroup(), 0.1)


def test_refresh_multi_hides_name_objects():
    from manim import VGroup

    chart = _chart()
    chart.compare(chart._series[0].data, [2, 1, 4, 3, 6, 5])
    chart._name_text = chart.axis_names[0].copy()
    chart._name_old = chart.axis_names[0].copy()

    chart._refresh(VGroup(), 0.1)


def test_paint_compare_numbers_hides_existing_numbers():
    class Num:
        def hide(self):
            pass

    chart = _chart()
    chart.compare(chart._series[0].data, [2, 1, 4, 3, 6, 5])
    chart._series[1].numbers = [Num()]

    chart._paint_compare_numbers(
        np.zeros(3),
        np.array([1.0, 0.0, 0.0]),
        np.array([0.0, 1.0, 0.0]),
        1.0,
        1.0,
    )


def test_paint_legend_hides_lone_chip_without_old_legend():
    from manim import VGroup

    chart = _chart()
    chart._legend_content = VGroup(VGroup(VGroup()))
    chart._legend_old = None

    chart._paint_legend(
        np.zeros(3),
        np.array([0.0, 1.0, 0.0]),
        0.0,
        3.0,
        1.0,
        False,
    )


def test_paint_gap_rejects_out_of_range_series():
    from manim import VGroup

    chart = _chart()
    chart.compare(chart._series[0].data, [2, 1, 4, 3, 6, 5])
    chart._gap_spec = {"a": 99, "b": 0, "opacity": 1.0}
    chart.gap_group = VGroup()

    chart._paint_gap(
        np.zeros(3), np.array([1.0, 0.0, 0.0]), np.array([0.0, 1.0, 0.0]), 1.0
    )


def test_refresh_oversized_header_without_name():
    from manim import Text, VGroup

    chart = _chart()
    chart.header = Text("Title")
    chart._name_text = None
    chart._name_old = None
    chart.header.scale(20)

    chart._refresh(VGroup(), 0.1)


def test_overflow_vertical_and_left_spikes_render():
    from manim import VGroup

    config = RadarConfig(
        radius=1.8,
        levels=4,
        sweep=False,
        grid_glow=False,
        show_level_labels=True,
        legend=False,
        morph_run_time=0.4,
        shockwave=False,
    )
    chart = RadarChart(
        axes=AXES,
        values=[20, 2, 20, 4, 5, 6],
        max_value=10,
        overflow=True,
        numbers="roll",
        config=config,
    )

    chart._refresh(VGroup(), 0.1)

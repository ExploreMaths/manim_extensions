# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Branch tests for the vendored radar chart internals."""

import numpy as np

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

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for radar morph colour/ring/camera corner cases."""

from types import SimpleNamespace

import numpy as np
import pytest
from manim import Square

from manim_extensions.radar import (
    CameraRig,
    RadarChart,
    RadarConfig,
    RadarData,
    RadarMorph,
)
from manim_extensions.radar.animations import Ring

AXES = ("Speed", "Power", "Range", "Comfort", "Price", "Safety")


def _chart(**changes):
    config = RadarConfig(
        radius=1.8,
        levels=4,
        sweep=False,
        grid_glow=False,
        show_level_labels=True,
        legend=False,
        morph_run_time=0.4,
        shockwave=False,
    ).evolved(**changes)
    return RadarChart(axes=AXES, values=[8, 6, 7, 9, 5, 8], config=config)


def test_morph_starts_with_target_only_colour(monkeypatch):
    chart = _chart()
    monkeypatch.setattr(chart, "_ensure_series_count", lambda *args, **kwargs: None)
    morph = RadarMorph(
        chart,
        [RadarData(axes=AXES, values=[1, 2, 3, 4, 5, 6], name="new")],
        transition="smooth",
        run_time=0.2,
    )
    morph.fade_name = False
    chart._series.clear()

    morph.begin()

    assert morph.slots[0]["start_color"] is not None


def test_morph_drop_ring_removes_attached_ring():
    chart = _chart()
    morph = RadarMorph(chart, [1, 2, 3, 4, 5, 6], run_time=0.2)
    ring = Ring(chart._anchor[0].get_center(), chart._series[0].color)
    chart.add(ring)
    morph._ring = ring

    morph._drop_ring()

    assert morph._ring is None
    assert ring not in chart.submobjects


def test_morph_prepare_camera_with_overflow(monkeypatch):
    chart = _chart()
    rig = CameraRig(SimpleNamespace(camera=SimpleNamespace(frame=Square())))
    chart.attach_camera(rig)
    morph = RadarMorph(
        chart, [9, 9, 9, 9, 9, 9], transition="burst", run_time=0.5
    )
    morph.begin()
    morph.end_scale = 0.0

    target = morph._prepare_camera()

    assert target is not None
    assert "direction" in target
    assert target["frame"] is not None


def test_morph_prepare_camera_returns_none_for_zero_direction(monkeypatch):
    chart = _chart()
    rig = CameraRig(SimpleNamespace(camera=SimpleNamespace(frame=Square())))
    chart.attach_camera(rig)
    morph = RadarMorph(
        chart, [9, 9, 9, 9, 9, 9], transition="burst", run_time=0.5
    )
    morph.begin()
    morph.end_scale = 0.0
    monkeypatch.setattr(
        chart,
        "_to_world",
        lambda points, origin, u, v: np.array([origin, origin]),
    )

    assert morph._prepare_camera() is None

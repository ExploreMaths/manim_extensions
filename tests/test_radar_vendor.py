# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Smoke tests for the vendored ``manim-radar`` package."""

from manim_extensions.radar import (
    THEMES,
    RadarChart,
    RadarData,
    get_theme,
)


def test_radar_data_and_chart():
    data = RadarData(axes=["Speed", "Power", "Range", "Comfort"], values=[8, 6, 7, 9])
    chart = RadarChart(data, title="Test")
    assert chart.config.title == "Test"
    assert data.full_scale >= 8


def test_theme_registry():
    assert "midnight" in THEMES
    assert get_theme("midnight") is THEMES["midnight"]

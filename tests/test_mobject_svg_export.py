# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the Cairo-backed SVG exporter."""

import os

import pytest
from manim import Circle, Square, VGroup

from manim_extensions.mobject_svg.svg import (
    create_svg_from_vgroup,
    create_svg_from_vmobject,
)


def test_vmobject_export_writes_file(tmp_path):
    target = tmp_path / "circle.svg"

    path = create_svg_from_vmobject(Circle(), target)

    assert path.exists()
    assert path.stat().st_size > 0
    assert "<svg" in path.read_text(encoding="utf-8")[:400]


def test_vgroup_export_writes_file(tmp_path):
    target = tmp_path / "group.svg"

    path = create_svg_from_vgroup(VGroup(Square(), Circle()), target)

    assert path.exists()
    assert path.stat().st_size > 0


@pytest.mark.parametrize("crop", [True, False])
def test_crop_flag(crop, tmp_path):
    target = tmp_path / ("crop_%s.svg" % crop)

    path = create_svg_from_vmobject(Circle(), target, crop=crop)

    assert path.exists()


def test_default_file_name_uses_working_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    path = create_svg_from_vmobject(Square())

    assert path.exists()


def test_stroke_and_fill_are_preserved(tmp_path):
    shape = Square().set_stroke(color="#FF0000", width=4).set_fill(color="#0000FF", opacity=0.5)
    target = tmp_path / "styled.svg"

    path = create_svg_from_vmobject(shape, target)

    content = path.read_text(encoding="utf-8")
    assert path.exists()
    assert "svg" in content

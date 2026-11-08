# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the constant-stroke-width scene."""

from manim import Circle

from manim_extensions.scenes import ConstantStrokeWidthScene


def test_adding_and_removing_mobjects():
    scene = ConstantStrokeWidthScene()
    circle = Circle()

    assert scene.add(circle) is scene
    assert scene.remove(circle) is scene


def test_stroke_scale_helpers():
    scene = ConstantStrokeWidthScene()
    circle = Circle()

    assert isinstance(scene._camera_stroke_scale(), float)
    assert scene._scale_family_stroke_widths(circle, 2.0) is None
    assert scene._scale_stroke_width(circle, 2.0) is None
    assert scene._update_stroke_scale(0.1) is None

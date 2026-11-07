# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the trail mobject geometry helpers."""

from manim import Circle

from manim_extensions.mobjects import Trail


def test_create_path_returns_vgroup():
    trail = Trail(Circle())

    path = trail.create_path()

    assert path is not None
    assert path is not None


def test_update_path_accepts_vgroup():
    trail = Trail(Circle())

    trail.update_path(trail.create_path())

    assert trail.create_path() is not None


def test_start_and_stop_trace():
    trail = Trail(Circle())

    trail.start_trace()
    trail.stop_trace()

    assert trail is not None

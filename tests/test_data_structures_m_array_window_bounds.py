# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for sliding window bounds checking and animate accessors."""

import pytest
from manim import Scene, tempconfig

from manim_extensions.data_structures.m_array import MArray, MArraySlidingWindow


@pytest.fixture(autouse=True)
def _config():
    with tempconfig({"dry_run": True, "disable_caching": True, "renderer": "cairo"}):
        yield


@pytest.fixture()
def window():
    scene = Scene()
    array = MArray(scene, [1, 2, 3])
    return MArraySlidingWindow(scene, array, index=0, size=2, label="window")


def test_shift_to_elem_rejects_out_of_range(window):
    with pytest.raises(Exception, match="Index out of bounds"):
        window.shift_to_elem(9)


def test_shift_to_elem_rejects_negative_index(window):
    with pytest.raises(Exception, match="Index out of bounds"):
        window.shift_to_elem(-1)


def test_shift_to_elem_rejects_oversized_window(window):
    with pytest.raises(Exception, match="Invalid window size"):
        window.shift_to_elem(2)


def test_attach_to_elem_rejects_out_of_range(window):
    with pytest.raises(Exception, match="Index out of bounds"):
        window.attach_to_elem(9)


def test_attach_to_elem_rejects_oversized_window(window):
    with pytest.raises(Exception, match="Invalid window size"):
        window.attach_to_elem(2)


def test_attach_to_elem_moves_window(window):
    window.attach_to_elem(1)

    assert window.animate_mob_window() is not None


def test_animate_accessors_return_builders(window):
    assert window.animate_mob_label() is not None

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for out-of-bounds guards and window resizing on the array mobjects."""

import pytest
from manim import Scene

from manim_extensions.data_structures.m_array import (
    MArray,
    MArrayDirection,
    MArraySlidingWindow,
)


@pytest.fixture(scope="module")
def scene():
    return Scene()


@pytest.fixture()
def array(scene):
    return MArray(scene, [1, 2, 3, 4], label="A")


def test_update_elem_value_rejects_negative_index(array):
    with pytest.raises(Exception):
        array.update_elem_value(-1, "x")


def test_update_elem_index_rejects_out_of_range(array):
    with pytest.raises(Exception):
        array.update_elem_index(9, "x")


def test_remove_elem_rejects_out_of_range(array):
    with pytest.raises(Exception):
        array.remove_elem(9)


def test_sliding_window_resize_updates_size(scene, array):
    window = MArraySlidingWindow(scene, array, index=0, size=2, label="w")

    window.resize_window(3)

    assert window is not None


def test_sliding_window_rejects_invalid_size(scene, array):
    window = MArraySlidingWindow(scene, array, index=0, size=2, label="w")

    with pytest.raises(Exception):
        window.resize_window(9)


def test_sliding_window_rejects_zero_size(scene, array):
    window = MArraySlidingWindow(scene, array, index=0, size=2, label="w")

    with pytest.raises(Exception):
        window.resize_window(0)


@pytest.mark.parametrize(
    "arr_dir",
    [MArrayDirection.LEFT, MArrayDirection.RIGHT, MArrayDirection.UP, MArrayDirection.DOWN],
)
def test_window_resize_in_all_directions(scene, arr_dir):
    array = MArray(scene, [1, 2, 3], label="A", arr_dir=arr_dir)
    window = MArraySlidingWindow(scene, array, index=0, size=2, label="w")

    window.resize_window(2)

    assert window is not None

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the array, pointer and sliding-window mobjects."""

import copy

import pytest
from manim import Scene

from manim_extensions.data_structures.m_array import (
    MArray,
    MArrayPointer,
    MArraySlidingWindow,
)


@pytest.fixture(scope="module")
def scene():
    return Scene()


@pytest.fixture()
def array(scene):
    return MArray(scene, [1, 2, 3, 4], label="A")


def test_array_builds_elements(array):
    assert len(array) == 5


def test_append_and_remove(array):
    array.append_elem(5)
    array.remove_elem(0)

    assert len(array) >= 4


def test_array_is_deep_copyable(array):
    clone = copy.deepcopy(array)

    assert isinstance(clone, MArray)
    assert clone is not array


def test_pointer_construction_and_movement(scene, array):
    pointer = MArrayPointer(scene, array, index=2, label="p")

    assert pointer is not None
    assert pointer.shift_to_elem(0) is not None


def test_pointer_is_deep_copyable(scene, array):
    pointer = MArrayPointer(scene, array, index=2)

    assert isinstance(copy.deepcopy(pointer), MArrayPointer)


def test_sliding_window_construction_and_movement(scene, array):
    window = MArraySlidingWindow(scene, array, index=1, size=2, label="w")

    assert window is not None
    assert window.shift_to_elem(0) is not None

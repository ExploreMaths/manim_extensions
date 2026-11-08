# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for MArray labels, pointers and sliding windows."""

import pytest
from manim import Scene

from manim_extensions.data_structures.m_array import (
    MArray,
    MArrayElement,
    MArrayPointer,
    MArraySlidingWindow,
)


@pytest.fixture(scope="module")
def scene():
    return Scene()


@pytest.fixture()
def array(scene):
    return MArray(scene, arr=[10, 20, 30])


def test_element_updates_return_animations(scene):
    element = MArrayElement(scene)

    assert element.update_mob_value({"color": "red"}) is not None
    assert element.update_mob_index({"color": "blue"}) is not None
    assert element.update_mob_label({"color": "green"}) is not None


def test_array_element_index_update(array):
    element = array.update_elem_index(0, 97)

    assert element is not None


def test_pointer_registers_with_array(array, scene):
    pointer = MArrayPointer(scene, array, index=1, label="i")

    pointer.attach_to_elem(1)

    assert pointer is not None


def test_sliding_window_registers_with_array(array, scene):
    window = MArraySlidingWindow(scene, array, index=0, size=2, label="w")

    window.attach_to_elem(0)

    assert window is not None

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for array label positioning and index bound checks."""

import pytest
from manim import Scene

from manim_extensions.data_structures.m_array import MArray
from manim_extensions.data_structures.m_enum import MArrayDirection


@pytest.fixture(scope="module")
def scene():
    return Scene()


def test_array_with_label_and_elements(scene):
    array = MArray(scene, [1, 2, 3], label="A")

    assert len(array.fetch_mob_arr()) == 3


def test_label_shift_factor_follows_array_direction(scene):
    array = MArray(scene, [1, 2, 3], label="A", arr_dir=MArrayDirection.LEFT)

    factor = array._MArray__calc_label_shift_factor(array.fetch_mob_arr()[0])

    assert factor >= 0


def test_update_label_text(scene):
    array = MArray(scene, [1, 2, 3], label="A")

    array.update_mob_arr_label("B")

    assert array.fetch_mob_arr_label().text == "B"


def test_update_elem_value_out_of_range_raises(scene):
    array = MArray(scene, [1, 2, 3])

    with pytest.raises(Exception):
        array.update_elem_value(9, 5)


def test_update_elem_index_out_of_range_raises(scene):
    array = MArray(scene, [1, 2, 3])

    with pytest.raises(Exception):
        array.update_elem_index(9, "x")


def test_animate_elem_returns_builder(scene):
    array = MArray(scene, [1, 2, 3])

    assert array.animate_elem(0) is not None
    assert array.animate_elem_square(0) is not None

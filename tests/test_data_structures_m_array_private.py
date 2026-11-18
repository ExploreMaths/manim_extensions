# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

import pytest
from manim import Scene

from manim_extensions.data_structures.m_array import (
    MArray,
    MArrayDirection,
    MArrayElement,
    MArrayPointer,
    MArraySlidingWindow,
)


@pytest.fixture(scope="module")
def scene():
    return Scene()


def test_non_string_labels_are_cast(scene):
    element = MArrayElement(scene, mob_label_args={"text": 7})
    array = MArray(scene, [1, 2], mob_arr_label_args={"text": 8})
    pointer = MArrayPointer(scene, array, mob_label_args={"text": 9})
    window = MArraySlidingWindow(scene, array, mob_label_args={"text": 10})

    assert isinstance(element.fetch_mob_label().text, str)
    assert array.fetch_mob_arr_label() is not None
    assert pointer.fetch_mob_label() is not None
    assert window.fetch_mob_label() is not None


def test_sum_elem_len_rejects_negative_and_large_ranges(scene):
    array = MArray(scene, [1, 2, 3])

    with pytest.raises(Exception):
        array._MArray__sum_elem_len(-1, 1)
    with pytest.raises(Exception):
        array._MArray__sum_elem_len(0, 9)


def test_private_remove_elem_rejects_out_of_range(scene):
    array = MArray(scene, [1, 2, 3])

    with pytest.raises(Exception):
        array._MArray__remove_elem(9)


def test_animate_elem_helpers_reject_out_of_range(scene):
    array = MArray(scene, [1, 2])

    with pytest.raises(Exception):
        array.animate_elem(9)
    with pytest.raises(Exception):
        array.animate_elem_value(9)
    with pytest.raises(Exception):
        array.animate_elem_index(9)


def test_pointer_arrow_position_swaps_axes(scene):
    array = MArray(scene, [1, 2])
    pointer = MArrayPointer(scene, array, pointer_pos=MArrayDirection.DOWN)

    pointer._MArrayPointer__calc_arrow_pos()


def test_pointer_and_window_update_label_play_animation(scene):
    array = MArray(scene, [1, 2])
    pointer = MArrayPointer(scene, array)
    window = MArraySlidingWindow(scene, array, size=2)
    scene.play = lambda *args, **kwargs: None

    pointer.update_mob_label("new")
    window.update_mob_label("new")


def test_pointer_and_window_remove_updater(scene):
    array = MArray(scene, [1, 2])
    pointer = MArrayPointer(scene, array)
    window = MArraySlidingWindow(scene, array, size=2)

    pointer._MArrayPointer__remove_updater()
    window._MArraySlidingWindow__remove_updater()


def test_animate_elem_square_rejects_out_of_range(scene):
    array = MArray(scene, [1, 2])
    with pytest.raises(Exception):
        array.animate_elem_square(9)


def test_pointer_arrow_position_swaps_axes_for_horizontal_pointer(scene):
    array = MArray(scene, [1, 2])
    pointer = MArrayPointer(scene, array, pointer_pos=MArrayDirection.LEFT)
    pointer._MArrayPointer__calc_arrow_pos()
    assert pointer is not None


def test_remove_elem_uses_non_opposite_label_direction(scene):
    array = MArray(scene, [1, 2], arr_label_pos=MArrayDirection.DOWN)
    array.remove_elem(1)

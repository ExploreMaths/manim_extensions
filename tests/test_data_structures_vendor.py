import numpy as np
import pytest
from manim import Scene

from manim_extensions.data_structures import (
    MArrayElement,
    MArray,
    MArrayPointer,
    MArraySlidingWindow,
    MArrayDirection,
    MArrayElementComp,
    MVariable,
)


class TestMArrayElement:
    def test_init_defaults(self):
        scene = Scene()
        elem = MArrayElement(scene)
        assert elem.fetch_mob_square() is not None
        assert elem.fetch_mob_value() is not None
        assert elem.fetch_mob_index() is not None
        assert elem.fetch_mob_label() is not None

    def test_init_custom_args(self):
        scene = Scene()
        elem = MArrayElement(
            scene,
            mob_value_args={"text": "42"},
            mob_index_args={"text": "i"},
            mob_label_args={"text": "x"},
        )
        assert elem.fetch_mob_value().text == "42"
        assert elem.fetch_mob_index().text == "i"
        assert elem.fetch_mob_label().text == "x"

    def test_fetch_mob_body(self):
        scene = Scene()
        elem = MArrayElement(scene)
        assert elem.fetch_mob(MArrayElementComp.BODY) is elem.fetch_mob_square()

    def test_fetch_mob_value(self):
        scene = Scene()
        elem = MArrayElement(scene)
        assert elem.fetch_mob(MArrayElementComp.VALUE) is elem.fetch_mob_value()

    def test_fetch_mob_index(self):
        scene = Scene()
        elem = MArrayElement(scene)
        assert elem.fetch_mob(MArrayElementComp.INDEX) is elem.fetch_mob_index()

    def test_fetch_mob_label(self):
        scene = Scene()
        elem = MArrayElement(scene)
        assert elem.fetch_mob(MArrayElementComp.LABEL) is elem.fetch_mob_label()

    def test_fetch_mob_unknown(self):
        scene = Scene()
        elem = MArrayElement(scene)
        assert elem.fetch_mob(99) is elem

    def test_animate_mob_square(self):
        scene = Scene()
        elem = MArrayElement(scene)
        assert elem.animate_mob_square() is not None

    def test_animate_mob_value(self):
        scene = Scene()
        elem = MArrayElement(scene)
        assert elem.animate_mob_value() is not None

    def test_animate_mob_index(self):
        scene = Scene()
        elem = MArrayElement(scene)
        assert elem.animate_mob_index() is not None

    def test_animate_mob_label(self):
        scene = Scene()
        elem = MArrayElement(scene)
        assert elem.animate_mob_label() is not None

    def test_update_mob_value_no_play(self):
        scene = Scene()
        elem = MArrayElement(scene, mob_value_args={"text": "old"})
        result = elem.update_mob_value(
            mob_value_args={"text": "new"}, play_anim=False
        )
        assert result.text == "new"

    def test_update_mob_index_no_play(self):
        scene = Scene()
        elem = MArrayElement(scene, mob_index_args={"text": "0"})
        result = elem.update_mob_index(
            mob_index_args={"text": "1"}, play_anim=False
        )
        assert result.text == "1"

    def test_update_mob_label_no_play(self):
        scene = Scene()
        elem = MArrayElement(scene, mob_label_args={"text": "a"})
        result = elem.update_mob_label(
            mob_label_args={"text": "b"}, play_anim=False
        )
        assert result.text == "b"

    def test_multiple_elements_chaining(self):
        scene = Scene()
        elem1 = MArrayElement(scene, mob_value_args={"text": "1"})
        elem2 = MArrayElement(
            scene, mob_value_args={"text": "2"}, next_to_mob=elem1
        )
        assert elem2.fetch_mob_value().text == "2"


class TestMArray:
    def test_init_empty(self):
        scene = Scene()
        arr = MArray(scene)
        assert arr.fetch_arr() == []
        assert arr.fetch_mob_arr() == []
        assert arr.fetch_mob_arr_label() is not None

    def test_init_with_values(self):
        scene = Scene()
        arr = MArray(scene, arr=[1, 2, 3], label="arr")
        assert arr.fetch_arr() == [1, 2, 3]
        assert len(arr.fetch_mob_arr()) == 3
        assert arr.fetch_mob_arr_label().text == "arr"

    def test_fetch_arr_dir(self):
        scene = Scene()
        arr = MArray(scene, arr=[1], arr_dir=MArrayDirection.RIGHT)
        assert arr.fetch_arr_dir() == MArrayDirection.RIGHT

    def test_fetch_arr_dir_left(self):
        scene = Scene()
        arr = MArray(scene, arr=[1], arr_dir=MArrayDirection.LEFT)
        assert arr.fetch_arr_dir() == MArrayDirection.LEFT

    def test_fetch_arr_dir_up(self):
        scene = Scene()
        arr = MArray(scene, arr=[1], arr_dir=MArrayDirection.UP)
        assert arr.fetch_arr_dir() == MArrayDirection.UP

    def test_fetch_arr_dir_down(self):
        scene = Scene()
        arr = MArray(scene, arr=[1], arr_dir=MArrayDirection.DOWN)
        assert arr.fetch_arr_dir() == MArrayDirection.DOWN

    def test_index_hex_display(self):
        scene = Scene()
        arr = MArray(scene, arr=[10], index_hex_display=True)
        idx_text = arr.fetch_mob_arr()[0].fetch_mob_index().text
        assert idx_text == hex(0)

    def test_hide_index(self):
        scene = Scene()
        arr = MArray(scene, arr=[1], hide_index=True)
        idx_text = arr.fetch_mob_arr()[0].fetch_mob_index().text
        assert idx_text == ""

    def test_index_offset_and_start(self):
        scene = Scene()
        arr = MArray(scene, arr=["a", "b"], index_offset=2, index_start=10)
        idx0 = arr.fetch_mob_arr()[0].fetch_mob_index().text
        idx1 = arr.fetch_mob_arr()[1].fetch_mob_index().text
        assert int(idx0) == 10
        assert int(idx1) == 12

    def test_append_elem_no_play(self):
        scene = Scene()
        arr = MArray(scene, arr=[1, 2])
        anims = arr.append_elem(3, play_anim=False)
        assert len(arr.fetch_arr()) == 3
        assert arr.fetch_arr()[2] == 3
        assert len(anims) > 0

    def test_remove_elem_no_play(self):
        scene = Scene()
        arr = MArray(scene, arr=[1, 2, 3])
        remove_anim, update_fn = arr.remove_elem(1, play_anim=False)
        assert arr.fetch_arr() == [1, 3]

    def test_remove_elem_invalid_index(self):
        scene = Scene()
        arr = MArray(scene, arr=[1, 2])
        with pytest.raises(Exception, match="Index out of bounds"):
            arr.remove_elem(5)

    def test_update_elem_value_no_play(self):
        scene = Scene()
        arr = MArray(scene, arr=[1, 2])
        result = arr.update_elem_value(0, 99, play_anim=False)
        assert arr.fetch_arr()[0] == 99

    def test_update_elem_value_invalid_index(self):
        scene = Scene()
        arr = MArray(scene, arr=[1])
        with pytest.raises(Exception, match="Index out of bounds"):
            arr.update_elem_value(5, 10)

    def test_update_elem_index_no_play(self):
        scene = Scene()
        arr = MArray(scene, arr=[10, 20])
        result = arr.update_elem_index(0, "new_idx", play_anim=False)
        assert result.text == "new_idx"

    def test_update_mob_arr_label_no_play(self):
        scene = Scene()
        arr = MArray(scene, arr=[1], label="old")
        result = arr.update_mob_arr_label("new", play_anim=False)
        assert result.text == "new"

    def test_animate_elem(self):
        scene = Scene()
        arr = MArray(scene, arr=[1, 2, 3])
        anim = arr.animate_elem(1)
        assert anim is not None

    def test_animate_elem_invalid_index(self):
        scene = Scene()
        arr = MArray(scene, arr=[1])
        with pytest.raises(Exception, match="Index out of bounds"):
            arr.animate_elem(5)

    def test_animate_elem_square(self):
        scene = Scene()
        arr = MArray(scene, arr=[1, 2])
        anim = arr.animate_elem_square(0)
        assert anim is not None

    def test_animate_elem_value(self):
        scene = Scene()
        arr = MArray(scene, arr=[1, 2])
        anim = arr.animate_elem_value(0)
        assert anim is not None

    def test_animate_elem_index(self):
        scene = Scene()
        arr = MArray(scene, arr=[1, 2])
        anim = arr.animate_elem_index(0)
        assert anim is not None

    def test_append_elem_multiple(self):
        scene = Scene()
        arr = MArray(scene, arr=[])
        arr.append_elem("a", play_anim=False)
        arr.append_elem("b", play_anim=False)
        arr.append_elem("c", play_anim=False)
        assert len(arr.fetch_arr()) == 3
        assert arr.fetch_arr() == ["a", "b", "c"]


class TestMArrayPointer:
    @pytest.fixture
    def arr_with_elements(self):
        scene = Scene()
        arr = MArray(scene, arr=[10, 20, 30])
        return scene, arr

    def test_init(self, arr_with_elements):
        scene, arr = arr_with_elements
        ptr = MArrayPointer(scene, arr, index=0, label="ptr")
        assert ptr.fetch_index() == 0
        assert ptr.fetch_mob_arrow() is not None
        assert ptr.fetch_mob_label().text == "ptr"

    def test_init_second_element(self, arr_with_elements):
        scene, arr = arr_with_elements
        ptr = MArrayPointer(scene, arr, index=1, label="p1")
        assert ptr.fetch_index() == 1

    def test_init_invalid_index(self, arr_with_elements):
        scene, arr = arr_with_elements
        with pytest.raises(Exception, match="Index out of bounds"):
            MArrayPointer(scene, arr, index=10)

    def test_update_mob_label_no_play(self, arr_with_elements):
        scene, arr = arr_with_elements
        ptr = MArrayPointer(scene, arr, index=0, label="old")
        result = ptr.update_mob_label("new", play_anim=False)
        assert result.text == "new"

    def test_animate_mob_arrow(self, arr_with_elements):
        scene, arr = arr_with_elements
        ptr = MArrayPointer(scene, arr, index=0)
        anim = ptr.animate_mob_arrow()
        assert anim is not None

    def test_animate_mob_label(self, arr_with_elements):
        scene, arr = arr_with_elements
        ptr = MArrayPointer(scene, arr, index=0, label="x")
        anim = ptr.animate_mob_label()
        assert anim is not None

    def test_shift_to_elem_no_play(self, arr_with_elements):
        scene, arr = arr_with_elements
        ptr = MArrayPointer(scene, arr, index=0)
        shift_anim = ptr.shift_to_elem(2, play_anim=False)
        assert ptr.fetch_index() == 2

    def test_shift_to_elem_invalid_index(self, arr_with_elements):
        scene, arr = arr_with_elements
        ptr = MArrayPointer(scene, arr, index=0)
        with pytest.raises(Exception, match="Index out of bounds"):
            ptr.shift_to_elem(10)

    def test_attach_to_elem(self, arr_with_elements):
        scene, arr = arr_with_elements
        ptr = MArrayPointer(scene, arr, index=0)
        ptr.attach_to_elem(2)
        assert ptr.fetch_index() == 2

    def test_attach_to_elem_invalid_index(self, arr_with_elements):
        scene, arr = arr_with_elements
        ptr = MArrayPointer(scene, arr, index=0)
        with pytest.raises(Exception, match="Index out of bounds"):
            ptr.attach_to_elem(10)


class TestMArraySlidingWindow:
    @pytest.fixture
    def arr_with_elements(self):
        scene = Scene()
        arr = MArray(scene, arr=[10, 20, 30, 40])
        return scene, arr

    def test_init(self, arr_with_elements):
        scene, arr = arr_with_elements
        win = MArraySlidingWindow(scene, arr, index=0, size=2, label="win")
        assert win.fetch_mob_window() is not None
        assert win.fetch_mob_label().text == "win"

    def test_init_invalid_index(self, arr_with_elements):
        scene, arr = arr_with_elements
        with pytest.raises(Exception, match="Index out of bounds"):
            MArraySlidingWindow(scene, arr, index=10, size=1)

    def test_init_invalid_size(self, arr_with_elements):
        scene, arr = arr_with_elements
        with pytest.raises(Exception, match="Invalid window size"):
            MArraySlidingWindow(scene, arr, index=0, size=0)

    def test_init_size_exceeds(self, arr_with_elements):
        scene, arr = arr_with_elements
        with pytest.raises(Exception, match="Invalid window size"):
            MArraySlidingWindow(scene, arr, index=2, size=5)

    def test_update_mob_label_no_play(self, arr_with_elements):
        scene, arr = arr_with_elements
        win = MArraySlidingWindow(scene, arr, index=0, size=2, label="old")
        result = win.update_mob_label("new", play_anim=False)
        assert result.text == "new"

    def test_fetch_mob_window(self, arr_with_elements):
        scene, arr = arr_with_elements
        win = MArraySlidingWindow(scene, arr, index=0, size=1)
        assert win.fetch_mob_window() is not None

    def test_fetch_mob_label(self, arr_with_elements):
        scene, arr = arr_with_elements
        win = MArraySlidingWindow(scene, arr, index=0, size=1, label="w")
        assert win.fetch_mob_label() is not None


class TestMArrayDirection:
    def test_directions_exist(self):
        assert hasattr(MArrayDirection, "UP")
        assert hasattr(MArrayDirection, "DOWN")
        assert hasattr(MArrayDirection, "RIGHT")
        assert hasattr(MArrayDirection, "LEFT")

    def test_direction_values(self):
        assert MArrayDirection.UP.value == 0
        assert MArrayDirection.DOWN.value == 1
        assert MArrayDirection.RIGHT.value == 2
        assert MArrayDirection.LEFT.value == 3

    def test_direction_count(self):
        assert len(MArrayDirection) == 4


class TestMArrayElementComp:
    def test_components_exist(self):
        assert hasattr(MArrayElementComp, "BODY")
        assert hasattr(MArrayElementComp, "VALUE")
        assert hasattr(MArrayElementComp, "INDEX")
        assert hasattr(MArrayElementComp, "LABEL")

    def test_component_values(self):
        assert MArrayElementComp.BODY.value == 0
        assert MArrayElementComp.VALUE.value == 1
        assert MArrayElementComp.INDEX.value == 2
        assert MArrayElementComp.LABEL.value == 3

    def test_component_count(self):
        assert len(MArrayElementComp) == 4


class TestMVariable:
    def test_init_defaults(self):
        scene = Scene()
        var = MVariable(scene)
        assert var.fetch_value() == ""
        assert var.fetch_index() == ""
        assert var.fetch_label() == ""

    def test_init_with_values(self):
        scene = Scene()
        var = MVariable(scene, value=42, index="i", label="x")
        assert var.fetch_value() == 42
        assert var.fetch_index() == "i"
        assert var.fetch_label() == "x"

    def test_fetch_mob_value(self):
        scene = Scene()
        var = MVariable(scene, value=17)
        assert var.fetch_mob_value() is not None

    def test_fetch_mob_index(self):
        scene = Scene()
        var = MVariable(scene, index="idx")
        assert var.fetch_mob_index() is not None

    def test_fetch_mob_label(self):
        scene = Scene()
        var = MVariable(scene, label="lbl")
        assert var.fetch_mob_label() is not None

    def test_update_value_no_play(self):
        scene = Scene()
        var = MVariable(scene, value=10)
        result = var.update_value(99, play_anim=False)
        assert var.fetch_value() == 99

    def test_update_index_no_play(self):
        scene = Scene()
        var = MVariable(scene, index="old")
        result = var.update_index("new", play_anim=False)
        assert var.fetch_index() == "new"

    def test_update_label_no_play(self):
        scene = Scene()
        var = MVariable(scene, label="old_lbl")
        result = var.update_label("new_lbl", play_anim=False)
        assert var.fetch_label() == "new_lbl"

    def test_inherits_from_marray_element(self):
        from manim_extensions.data_structures.m_array import MArrayElement
        assert issubclass(MVariable, MArrayElement)

    def test_animate_mob_value(self):
        scene = Scene()
        var = MVariable(scene, value=5)
        assert var.animate_mob_value() is not None

    def test_animate_mob_index(self):
        scene = Scene()
        var = MVariable(scene, index="i")
        assert var.animate_mob_index() is not None

    def test_animate_mob_label(self):
        scene = Scene()
        var = MVariable(scene, label="x")
        assert var.animate_mob_label() is not None
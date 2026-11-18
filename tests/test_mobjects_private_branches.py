import numpy as np
from manim import Text

from manim_extensions.mobjects import (
    CropImageMobject,
    FileTree,
    ObjectBorder,
    PerpendicularSign,
)


def test_file_tree_build_tree_rejects_non_dict():
    assert FileTree._build_tree([]) == []


def test_crop_image_accepts_pil_image_and_disables_radius():
    from PIL import Image

    image = Image.new("RGB", (4, 4), (255, 0, 0))
    mobject = CropImageMobject(image, corner_radius=None)

    assert mobject is not None


def test_crop_image_falls_back_to_base_class():
    import pytest

    with pytest.raises(Exception):
        CropImageMobject(object())


def test_chinese_math_tex_ascii_color_key():
    from manim import RED

    from manim_extensions.mobjects import ChineseMathTex

    formula = ChineseMathTex("a", tex_to_color_map={"a": RED})
    assert formula is not None


def test_object_border_without_corners():
    border = ObjectBorder(Text("Hi"), add_corner=False, track=False)
    border._rebuild()

    assert len(border.border) == 1


def test_perpendicular_sign_direction_fallbacks():
    sign = PerpendicularSign.__new__(PerpendicularSign)
    zero = np.array([0.0, 0.0, 0.0])

    line = type(
        "Line", (), {"get_start": lambda self: zero, "get_end": lambda self: zero}
    )()
    first, second = sign._get_both_directions(line, zero)
    assert np.array_equal(first, zero)
    assert np.array_equal(second, zero)
    first, second = sign._select_directions((zero, zero), (zero, zero), None)
    assert np.array_equal(first, zero)
    assert np.array_equal(second, zero)

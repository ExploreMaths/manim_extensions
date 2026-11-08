# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the Chinese-aware LaTeX mobject."""

import pytest
from manim import MathTex

from manim_extensions.mobjects import ChineseMathTex


def test_plain_construction():
    tex = ChineseMathTex(r"\text{你好}")

    assert isinstance(tex, MathTex)


def test_tex_to_color_map_handles_chinese_characters():
    tex = ChineseMathTex(r"\text{你好}", tex_to_color_map={"你": "red", "好": "blue"})

    assert isinstance(tex, MathTex)


def test_custom_tex_template_is_honoured():
    from manim import TexTemplate

    template = TexTemplate()
    template.add_to_preamble(r"\usepackage{amsmath}")

    tex = ChineseMathTex(r"\text{再见}", tex_template=template)

    assert tex is not None


def test_amstex_wrapper_is_mathtex():
    assert isinstance(ChineseMathTex(r"\text{测试}"), MathTex)

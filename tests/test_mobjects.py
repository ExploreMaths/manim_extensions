import shutil
import subprocess

import pytest
from manim import MathTex, VGroup, Line, LEFT, RIGHT, UP, DOWN, ORIGIN

from manim_extensions.mobjects import (
    ChineseMathTex,
    LabelDot,
    MathTexLine,
    MathTexBrace,
    MathTexDoublearrow,
    ExtendedLine,
)

_HAS_XELATEX = shutil.which("xelatex") is not None


@pytest.mark.skipif(not _HAS_XELATEX, reason="xelatex not installed")
class TestChineseMathTex:
    def test_is_math_tex_subclass(self):
        tex = ChineseMathTex("x + y = 1")
        assert isinstance(tex, MathTex)

    def test_font_parameter(self):
        tex = ChineseMathTex("x = 1", font="SimSun")
        assert isinstance(tex, MathTex)


class TestLabelDot:
    def test_creation(self):
        dot = LabelDot("A", [1, 2, 0])
        assert isinstance(dot, VGroup)
        assert len(dot.submobjects) == 2

    def test_direction_and_buff(self):
        dot = LabelDot("B", [0, 0, 0], label_pos=UP, buff=0.2)
        assert isinstance(dot, VGroup)


class TestMathTexLine:
    def test_creation(self):
        formula = MathTex("y = x")
        obj = MathTexLine(formula, direction=UP, buff=0.5)
        assert isinstance(obj, VGroup)
        assert len(obj.submobjects) == 2


class TestMathTexBrace:
    def test_creation(self):
        formula = MathTex("\\Delta x")
        target = Line(LEFT, RIGHT)
        obj = MathTexBrace(target, formula, direction=UP, buff=0.3)
        assert isinstance(obj, VGroup)
        assert len(obj.submobjects) == 2


class TestMathTexDoublearrow:
    def test_creation(self):
        formula = MathTex("\\Leftrightarrow")
        obj = MathTexDoublearrow(formula, direction=DOWN, buff=0.4)
        assert isinstance(obj, VGroup)
        assert len(obj.submobjects) == 2


class TestExtendedLine:
    def test_extend(self):
        original = Line(LEFT, RIGHT)
        extended = ExtendedLine(original, extend_distance=1.0)
        assert isinstance(extended, Line)
        # Original line has length 2 (from -1 to 1 on x-axis)
        # Extended by 1.0 on each end should give length 4
        start = extended.get_start()
        end = extended.get_end()
        assert abs(start[0] - (-2.0)) < 1e-6
        assert abs(end[0] - 2.0) < 1e-6

    def test_degenerate_line(self):
        original = Line(ORIGIN, ORIGIN)
        extended = ExtendedLine(original, extend_distance=1.0)
        assert isinstance(extended, Line)

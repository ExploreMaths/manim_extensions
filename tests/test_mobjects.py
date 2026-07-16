import shutil
import subprocess

import numpy as np
import pytest
from manim import MathTex, VGroup, Line, LEFT, RIGHT, UP, DOWN, ORIGIN

from manim_extensions.mobjects import (
    ChineseMathTex,
    LabelDot,
    MathTexLine,
    MathTexBrace,
    MathTexDoublearrow,
    ExtendedLine,
    PerpendicularLine,
    PerpendicularSign,
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
        formula = MathTex(r"\Delta x")
        target = Line(LEFT, RIGHT)
        obj = MathTexBrace(target, formula, direction=UP, buff=0.3)
        assert isinstance(obj, VGroup)
        assert len(obj.submobjects) == 2


class TestMathTexDoublearrow:
    def test_creation(self):
        formula = MathTex(r"\Leftrightarrow")
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


class TestPerpendicularLine:
    def test_basic_perpendicular(self):
        line = Line(LEFT, RIGHT)
        perp = PerpendicularLine(UP, line)
        assert isinstance(perp, Line)
        start, end = perp.get_start(), perp.get_end()
        assert np.allclose(start, UP) or np.allclose(end, UP)
        foot = perp.foot
        assert np.allclose(foot, ORIGIN)

    def test_with_mobject_point(self):
        line = Line(LEFT, RIGHT)
        dot = LabelDot("P", UP * 2)
        perp = PerpendicularLine(dot, line)
        assert isinstance(perp, Line)
        assert np.allclose(perp.foot, ORIGIN)

    def test_degenerate_line(self):
        line = Line(ORIGIN, ORIGIN)
        perp = PerpendicularLine(UP, line)
        assert isinstance(perp, Line)
        # Falls back to the degenerate point
        assert np.allclose(perp.foot, ORIGIN)


class TestPerpendicularSign:
    def test_creation(self):
        line1 = Line(LEFT, RIGHT)
        line2 = Line(DOWN, UP)
        sign = PerpendicularSign(line1, line2, length=0.2)
        assert isinstance(sign, VGroup)
        assert len(sign.submobjects) == 2

    def test_intersection_at_origin(self):
        line1 = Line(LEFT, RIGHT)
        line2 = Line(DOWN, UP)
        sign = PerpendicularSign(line1, line2, length=0.2)
        # The sign should be created and its intersection should be near origin
        assert np.allclose(sign.intersection, ORIGIN, atol=1e-6)

    def test_parallel_lines(self):
        line1 = Line(LEFT, RIGHT)
        line2 = Line(UP, UP + RIGHT)
        sign = PerpendicularSign(line1, line2, length=0.2)
        # Parallel lines have no intersection, so sign should be empty
        assert len(sign.submobjects) == 0

    def test_different_lengths(self):
        line1 = Line(LEFT, RIGHT)
        line2 = Line(DOWN, UP)
        sign = PerpendicularSign(line1, line2, length=0.5)
        assert isinstance(sign, VGroup)
        assert len(sign.submobjects) == 2

    def test_corner_direction_ur(self):
        line1 = Line(LEFT, RIGHT)
        line2 = Line(DOWN, UP)
        # 指定折角画在右上（第一象限）
        sign = PerpendicularSign(line1, line2, length=0.2, corner_direction=[1, 1, 0])
        assert isinstance(sign, VGroup)
        assert len(sign.submobjects) == 2
        # 内角顶点应该在第一象限
        inner = sign.submobjects[0].get_end()
        assert inner[0] > 0
        assert inner[1] > 0

    def test_corner_direction_dl(self):
        line1 = Line(LEFT, RIGHT)
        line2 = Line(DOWN, UP)
        # 指定折角画在左下（第三象限）
        sign = PerpendicularSign(line1, line2, length=0.2, corner_direction=[-1, -1, 0])
        assert isinstance(sign, VGroup)
        assert len(sign.submobjects) == 2
        # 内角顶点应该在第三象限
        inner = sign.submobjects[0].get_end()
        assert inner[0] < 0
        assert inner[1] < 0

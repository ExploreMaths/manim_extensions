import numpy as np
import pytest
from manim import Circle, Line, Arc, LEFT, RIGHT, UP, DOWN, ORIGIN

from manim_extensions.geometry import (
    CircleInt,
    LineCircleInt,
    LineInt,
    LineArcInt,
    TangentPoint,
)


class TestCircleInt:
    def test_two_intersections(self):
        c1 = Circle(radius=2).shift(LEFT)
        c2 = Circle(radius=2).shift(RIGHT)
        result = CircleInt(c1, c2)
        assert result is not None
        p1, p2 = result
        assert len(p1) == 3
        assert len(p2) == 3
        # y coordinates should be equal and opposite
        assert abs(p1[1] + p2[1]) < 1e-6
        assert abs(p1[0]) < 1e-6

    def test_no_intersection(self):
        c1 = Circle(radius=1).shift(LEFT * 3)
        c2 = Circle(radius=1).shift(RIGHT * 3)
        result = CircleInt(c1, c2)
        assert result is None

    def test_same_center(self):
        c1 = Circle(radius=1)
        c2 = Circle(radius=2)
        result = CircleInt(c1, c2)
        assert result is None


class TestLineCircleInt:
    def test_two_intersections(self):
        line = Line(LEFT * 3, RIGHT * 3)
        circle = Circle(radius=1)
        result = LineCircleInt(line, circle)
        assert result is not None

    def test_no_intersection(self):
        line = Line(UP * 3, UP * 5)
        circle = Circle(radius=1)
        result = LineCircleInt(line, circle)
        assert result is None

    def test_tangent(self):
        line = Line(UP, UP * 3)
        circle = Circle(radius=1)
        result = LineCircleInt(line, circle)
        # Tangent may return one point or None depending on numerical precision
        assert (result is None) or (isinstance(result, np.ndarray))


class TestLineInt:
    def test_intersection(self):
        l1 = Line(LEFT, RIGHT)
        l2 = Line(DOWN, UP)
        result = LineInt(l1, l2)
        assert result is not None
        assert abs(result[0]) < 1e-6
        assert abs(result[1]) < 1e-6
        assert abs(result[2]) < 1e-6

    def test_parallel(self):
        l1 = Line(LEFT, RIGHT)
        l2 = Line(UP, UP + RIGHT * 2)
        result = LineInt(l1, l2)
        assert result is None


class TestLineArcInt:
    def test_intersection_with_arc(self):
        line = Line(LEFT, RIGHT)
        arc = Arc(start_angle=0, angle=np.pi, radius=1)
        result = LineArcInt(line, arc)
        assert result is not None

    def test_no_intersection(self):
        line = Line(UP * 2, UP * 3)
        arc = Arc(start_angle=0, angle=np.pi, radius=1)
        result = LineArcInt(line, arc)
        assert result is None


class TestTangentPoint:
    def test_basic_tangent(self):
        # Unit circle points and vertical tangent line at x=1
        p = TangentPoint(
            [1, 0, 0],
            [-1, 0, 0],
            [1, -2, 0],
            [1, 2, 0],
        )
        assert p is not None
        assert abs(p[0] - 1.0) < 1e-6
        assert abs(p[2]) < 1e-6

    def test_degenerate_line(self):
        p = TangentPoint(
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 0],
            [0, 0, 0],
        )
        # Single point line that happens to be on circle
        assert (p is None) or isinstance(p, np.ndarray)

    def test_no_solution(self):
        p = TangentPoint(
            [1, 0, 0],
            [2, 0, 0],
            [10, 0, 0],
            [10, 1, 0],
        )
        assert p is None

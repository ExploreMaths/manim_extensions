# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


from manim import *
import numpy as np
import pytest

from manim_extensions.geometry import (
    TangentPoint,
    VMobjectInt,
)


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


class TestVMobjectInt:
    def test_circle_circle(self):
        c1 = Circle(radius=2).shift(LEFT)
        c2 = Circle(radius=2).shift(RIGHT)
        pts = VMobjectInt(c1, c2)
        assert len(pts) == 2
        # Intersections lie on the y-axis and are symmetric about it.
        # Manim circles are cubic Bézier approximations (~3e-4 radial error).
        for p in pts:
            assert abs(p[0]) < 1e-5
            assert abs(abs(p[1]) - np.sqrt(3)) < 2e-3

    def test_line_line(self):
        pts = VMobjectInt(Line(LEFT, RIGHT), Line(DOWN, UP))
        assert len(pts) == 1
        assert np.linalg.norm(pts[0]) < 1e-5

    def test_line_circle(self):
        # Horizontal line y = 1 through a circle of radius 2
        line = Line(LEFT * 3 + UP, RIGHT * 3 + UP)
        pts = VMobjectInt(line, Circle(radius=2))
        assert len(pts) == 2
        xs = sorted(p[0] for p in pts)
        assert abs(xs[0] + np.sqrt(3)) < 2e-3
        assert abs(xs[1] - np.sqrt(3)) < 2e-3

    def test_arc_line(self):
        arc = Arc(radius=1, start_angle=0, angle=np.pi)  # upper half circle
        line = Line(LEFT * 2 + UP * 0.5, RIGHT * 2 + UP * 0.5)
        pts = VMobjectInt(arc, line)
        assert len(pts) == 2
        for p in pts:
            assert abs(p[1] - 0.5) < 2e-3
            assert abs(abs(p[0]) - np.sqrt(0.75)) < 2e-3

    def test_no_intersection(self):
        c1 = Circle(radius=1).shift(LEFT * 5)
        c2 = Circle(radius=1).shift(RIGHT * 5)
        assert VMobjectInt(c1, c2) == []

    def test_tangent(self):
        circle = Circle(radius=1)
        line = Line(LEFT * 2 + UP, RIGHT * 2 + UP)  # tangent at the top
        pts = VMobjectInt(circle, line)
        assert len(pts) >= 1
        for p in pts:
            assert abs(p[0]) < 1e-5
            assert abs(p[1] - 1.0) < 1e-5

    def test_parametric_curve(self):
        # A parabola y = x**2 crossed by the line y = 0.25 -> x = +/- 0.5
        parabola = ParametricFunction(
            lambda t: [t, t**2, 0], t_range=[-2, 2, 0.01]
        )
        line = Line(LEFT * 2 + UP * 0.25, RIGHT * 2 + UP * 0.25)
        pts = VMobjectInt(parabola, line)
        assert len(pts) == 2
        xs = sorted(p[0] for p in pts)
        assert abs(xs[0] + 0.5) < 1e-4
        assert abs(xs[1] - 0.5) < 1e-4

    def test_vgroup(self):
        group = VGroup(
            Circle(radius=1).shift(UP * 3),
            Circle(radius=1),
        )
        line = Line(LEFT * 3, RIGHT * 3)
        pts = VMobjectInt(group, line)
        assert len(pts) == 2
        for p in pts:
            assert abs(p[1]) < 1e-5
            assert abs(abs(p[0]) - 1.0) < 1e-5

    def test_points_are_3d_arrays(self):
        pts = VMobjectInt(Circle(radius=1), Line(LEFT * 2, RIGHT * 2))
        assert len(pts) == 2
        for p in pts:
            assert isinstance(p, np.ndarray)
            assert p.shape == (3,)

    def test_function_graphs_cross(self):
        # y = x**2 vs y = x -> intersections at (0, 0) and (1, 1)
        parabola = FunctionGraph(lambda x: x**2, x_range=[-2, 2])
        diagonal = FunctionGraph(lambda x: x, x_range=[-2, 2])
        pts = VMobjectInt(parabola, diagonal)
        assert len(pts) == 2
        got = sorted((round(float(p[0]), 3), round(float(p[1]), 3)) for p in pts)
        assert got == [(0.0, 0.0), (1.0, 1.0)]

    def test_function_graphs_sin_cos(self):
        # sin(x) = cos(x) at x = pi/4 + k*pi -> (pi/4, sqrt(2)/2),
        # (5*pi/4, -sqrt(2)/2) within [0, 2*pi]
        sin_curve = FunctionGraph(np.sin, x_range=[0, 2 * np.pi])
        cos_curve = FunctionGraph(np.cos, x_range=[0, 2 * np.pi])
        pts = VMobjectInt(sin_curve, cos_curve)
        assert len(pts) == 2
        xs = sorted(p[0] for p in pts)
        assert abs(xs[0] - np.pi / 4) < 1e-3
        assert abs(xs[1] - 5 * np.pi / 4) < 1e-3
        ys = sorted(p[1] for p in pts)
        assert abs(ys[0] + np.sqrt(2) / 2) < 1e-3
        assert abs(ys[1] - np.sqrt(2) / 2) < 1e-3

    def test_axes_plots(self):
        # Graphs produced by Axes.plot are ordinary VMobjects too.
        axes = Axes(
            x_range=[-2, 2], y_range=[-2, 2], x_length=5, y_length=5
        )
        g1 = axes.plot(lambda x: x**2, x_range=[-1.5, 1.5])
        g2 = axes.plot(lambda x: 0.5 * x + 0.5, x_range=[-1.5, 1.5])
        pts = VMobjectInt(g1, g2)
        # x**2 = 0.5*x + 0.5 -> 2x**2 - x - 1 = 0 -> x = 1 or x = -0.5
        assert len(pts) == 2
        # Convert intersection points back to axes coordinates
        coords = sorted((axes.p2c(p)[:2] for p in pts), key=lambda c: c[0])
        assert abs(coords[0][0] + 0.5) < 1e-3
        assert abs(coords[1][0] - 1.0) < 1e-3

    def test_symmetric_arguments(self):
        c1 = Circle(radius=2).shift(LEFT)
        c2 = Circle(radius=2).shift(RIGHT)
        pts1 = sorted(map(tuple, VMobjectInt(c1, c2)))
        pts2 = sorted(map(tuple, VMobjectInt(c2, c1)))
        assert len(pts1) == len(pts2) == 2
        for a, b in zip(pts1, pts2):
            assert np.linalg.norm(np.array(a) - np.array(b)) < 1e-6

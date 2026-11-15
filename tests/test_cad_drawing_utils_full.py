# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Behavioural coverage for the vendored CAD drawing utilities."""

import numpy as np
import pytest
from manim import (
    Circle,
    DOWN,
    Line,
    PI,
    RIGHT,
    Square,
    Text,
    UP,
    VMobject,
)

from manim_extensions.cad_drawing_utils.dimensions import (
    Angle_Dimension_3point,
    Angle_Dimension_Mob,
    CAD_ArrowHead,
    Linear_Dimension,
    Pointer_Label_Free,
    Pointer_To_Mob,
)
from manim_extensions.cad_drawing_utils.hatch import Hatch_lines, curve_intersection
from manim_extensions.cad_drawing_utils.path_mapper import (
    Dashed_line_mobject,
    DashDot_mobject,
    Path_Offset_Mobject,
    Path_mapper,
    Curve_Warp,
)
from manim_extensions.cad_drawing_utils.round_corners import (
    Chamfer_Corner_Param,
    Chamfer_Corners,
    Round_Corner_Param,
    Round_Corners,
)
from manim_extensions.cad_drawing_utils.utils import (
    Bezier_Handlebars,
    angle_between_vectors_signed,
)


def _square():
    return Square(side_length=2).set_fill(opacity=0)


def _line(points=4):
    line = Line([-2, 0, 0], [2, 0, 0])
    return line


# ------------------------------------------------------------------ utils


def test_signed_angle_and_bezier_handlebars_move():
    assert angle_between_vectors_signed(np.array([1, 0, 0]), np.array([1, 0, 0])) == 0
    assert angle_between_vectors_signed(
        np.array([1, 0, 0]), np.array([0, 1, 0])
    ) == pytest.approx(np.pi / 2)
    target = Line([0, 0, 0], [2, 0, 0])
    bars = Bezier_Handlebars(target)
    assert "dots" in bars and "lines" in bars
    target.shift(RIGHT)
    bars.move_circles()
    bars.move_lines()


# --------------------------------------------------------- round corners


def test_round_corner_param_and_closed_square():
    square = _square()
    curve1 = square.get_nth_curve_points(0)
    curve2 = square.get_nth_curve_points(1)
    params, k = Round_Corner_Param(0.2, curve1, curve2)
    assert params["radius"] > 0
    assert len(k) == 2
    rounded = Round_Corners(_square(), radius=0.2)
    assert rounded.get_num_curves() >= 4


def test_round_corners_open_path_hits_break():
    open_path = VMobject().set_points_as_corners(
        [[-2, 0, 0], [0, 0, 0], [0, 2, 0], [2, 2, 0]]
    )
    rounded = Round_Corners(open_path, radius=0.1)
    assert rounded.get_num_curves() >= 3


class _IterOffset:
    def __init__(self, values):
        self.values = values
        self.iter = True

    def __getitem__(self, index):
        return self.values[index]


def test_chamfer_scalar_iterable_and_open():
    square = _square()
    curve1 = square.get_nth_curve_points(0)
    curve2 = square.get_nth_curve_points(1)
    params, k = Chamfer_Corner_Param(0.2, curve1, curve2)
    assert "start" in params and len(k) == 2
    params2, _ = Chamfer_Corner_Param(_IterOffset([0.1, 0.4]), curve1, curve2)
    assert "start" in params2
    chamfered = Chamfer_Corners(_square(), offset=0.2)
    assert chamfered.get_num_curves() >= 4
    open_path = VMobject().set_points_as_corners(
        [[-2, 0, 0], [0, 0, 0], [0, 2, 0], [2, 2, 0]]
    )
    assert Chamfer_Corners(open_path, offset=0.1).get_num_curves() >= 3


# ---------------------------------------------------------------- hatch


def test_hatch_lines_on_square_and_intersection_helper():
    square = _square().scale(0.8)
    hatch = Hatch_lines(square, angle=PI / 6, offset=0.25)
    assert len(hatch) > 0
    line = Line([-5, 0, 0], [5, 0, 0])
    idx1, idx2 = curve_intersection(square, line)
    assert len(idx1) >= 2 and len(idx2) >= 2
    # a completely disjoint object produces empty index arrays
    far = Circle(radius=0.3).move_to([8, 0, 0])
    idx3, idx4 = curve_intersection(square, far)
    assert len(idx3) == 0 and len(idx4) == 0


# --------------------------------------------------------------- mapper


def test_path_mapper_lengths_alpha_and_points():
    square = _square().scale(1.2)
    pm = Path_mapper(square)
    length = pm.get_path_length()
    assert length > 0
    assert pm.alpha_from_length(length) == pytest.approx(1.0)
    assert pm.length_from_alpha(1.0) == pytest.approx(length)
    alpha_list = pm.alpha_from_length([0, length / 2, length])
    assert len(alpha_list) == 3
    lengths = pm.length_from_alpha([0, 0.5, 1])
    assert len(lengths) == 3
    assert pm.point_from_proportion(1.0).shape == (3,)
    many = pm.point_from_proportion(np.array([0, 0.5, 1.0]))
    assert many.shape == (3, 3)
    assert pm.get_length_between_points(1, 0) == pytest.approx(length)
    assert abs(pm.get_length_between_points_wrapped(0.9, 0.1)) <= length / 2
    shorter, longer = pm.get_length_between_points_tuple(0.9, 0.1)
    assert shorter <= longer
    assert pm.get_bezier_index_from_length(length)[0] == square.get_num_curves() - 1
    assert pm.get_tangent_unit_vector(length / 2).shape == (3,)
    assert pm.get_tangent_angle(length / 2) is not None
    assert pm.get_normal_unit_vector(length / 2).shape == (3,)
    assert pm.get_curvature_vector(length / 2).shape == (3,)
    assert pm.get_curvature(length / 2) >= 0
    assert pm.calc_len_with_quads() > 0
    assert pm.equalize_alpha(0.5) == pytest.approx(pm.alpha_from_length(0.5 * length))
    eq = pm.equalize_rate_func(lambda t: t)
    assert 0 <= eq(0.5) <= 1
    # cubic_to_quads output shape
    quads = pm.cubic_to_quads(square.get_nth_curve_points(0))
    assert quads.shape == (6, 3)
    # straight-line quadratic branch in calc_len_bezier_quad
    straight = np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0]])
    assert pm.calc_len_bezier_quad(straight) >= 0


def test_path_mapper_wrapping_helpers_and_iterable_inputs():
    pm = Path_mapper(_square())
    L = pm.get_path_length()
    # AB > L/2 path in the tuple helper
    a, b = pm.get_length_between_points_tuple(0.0, 0.5)
    assert a <= b
    # closed wrapping near the seam
    w = pm.get_length_between_points_wrapped(0.02, 0.98)
    assert w <= 0.2 * L


def test_dashed_dashdot_and_offset_mobject():
    square = _square()
    dashed = Dashed_line_mobject(square, num_dashes=8, dash_offset=0.1)
    assert len(dashed["dashes"]) > 0
    # negative dash starts and past-the-end starts are pruned
    pattern = dashed.generate_dash_pattern_metric(0.1, 0.1, 10, offset=1.0)
    assert len(pattern["dash_starts"]) == len(pattern["dash_ends"])
    pattern2 = dashed.generate_dash_pattern_metric(0.1, 0.1, 2, offset=-5.0)
    assert len(pattern2["dash_starts"]) <= 2
    dashdot = DashDot_mobject(square, num_dashes=6, dash_offset=0.05)
    assert "dots" in dashdot
    offset = Path_Offset_Mobject(
        square,
        lambda t, amount=0.2: np.array([0, amount, 0]),
        num_of_samples=12,
        discontinuities=[0.3],
    )
    assert offset.get_num_curves() >= 3
    offset.set_ofs_function_kwargs({"amount": 0.3})
    offset.generate_offset_paths(gen_ofs_point=False, gen_ref_curve=False)


def test_curve_warp_closed_and_open_branches():
    warp_curve = _square().scale(0.8)
    source = VMobject()
    source.set_points_as_corners([[-1, 0, 0], [0, 1, 0], [1, 0, 0]])
    warped = Curve_Warp(source, warp_curve, anchor_point=0.5)
    assert warped.get_num_curves() > 0
    open_curve = Line([-2, 0, 0], [2, 0, 0])
    # large x -> past-the-end tangent extension; negative x -> before-start branch
    source2 = VMobject()
    source2.set_points_as_corners([[-2, 1, 0], [2, -1, 0]])
    warped2 = Curve_Warp(source2, open_curve, anchor_point=0.0)
    assert len(warped2.points) > 0


# ------------------------------------------------------------ dimensions


def test_pointer_label_free_str_mobject_and_fallback():
    p1 = Pointer_Label_Free([1, 1, 0], "note", offset_vector=RIGHT + UP)
    assert "text" in p1 and "line" in p1
    p1.update_point([2, 2, 0], offset_vector=RIGHT + DOWN)
    p2 = Pointer_Label_Free([0, 0, 0], Text("label"))
    assert p2["text"].text == "label"
    p3 = Pointer_Label_Free([0, 0, 0], 123)
    assert p3["text"].text == "A"


def test_pointer_to_mob_normal_and_degenerate_center():
    mob = Line([-1, 0, 0], [1, 0, 0])
    pointer = Pointer_To_Mob(mob, 0.5, "mid")
    pointer.update_mob(mob, 0.2)
    # a one-point mob has its point at the center -> RIGHT+UP fallback
    dot = VMobject().set_points_as_corners([[0, 0, 0], [0, 0, 0]])
    Pointer_To_Mob(dot, 0.5, "dot")
    # explicit offset kwarg path
    Pointer_To_Mob(mob, 0.5, "off", offset=UP * 2)


def test_linear_dimension_inner_and_outside_arrow():
    inner = Linear_Dimension(np.array([-2.0, 0, 0]), np.array([2.0, 0, 0]))
    assert "text" in inner and "main_line" in inner
    outside = Linear_Dimension(
        np.array([-2.0, 0, 0]),
        np.array([2.0, 0, 0]),
        text="width",
        outside_arrow=True,
        direction=UP,
    )
    assert "text" in outside
    # explicit direction, text object and very long text triggering scale-down
    Linear_Dimension(
        np.array([-1.0, 0, 0]),
        np.array([1.0, 0, 0]),
        text=Text("long label"),
        direction=DOWN,
        offset=1,
    )
    # vertical dimension forces the vertical-text special case
    vertical = Linear_Dimension(np.array([0.0, -2, 0]), np.array([0.0, 2, 0]))
    assert "text" in vertical


def test_angle_dimensions_and_mob():
    angle = Angle_Dimension_3point(
        np.array([1.0, 0, 0]), np.array([0.0, 1, 0]), np.array([0.0, 0, 0])
    )
    assert "text" in angle and "base_arc" in angle
    outside = Angle_Dimension_3point(
        np.array([1.0, 0, 0]),
        np.array([0.0, 1, 0]),
        np.array([0.0, 0, 0]),
        outside_arrow=True,
    )
    assert "base_arc" in outside
    Angle_Dimension_3point(
        np.array([1.0, 0, 0]), np.array([0.0, 1, 0]), np.array([0.0, 0, 0]), text="90"
    )
    arc = Circle(radius=1)
    Angle_Dimension_Mob(arc, 0.0, 0.25)
    Angle_Dimension_Mob(arc, 0.1, 0.9, outside_arrow=True)


def test_cad_arrow_head_properties_updater_and_flip():
    curve = Line([0, 0, 0], [2, 0, 0])
    arrow = CAD_ArrowHead(curve, anchor_point=1, arrow_size=0.3)
    assert arrow.get_num_curves() > 0
    assert arrow.get_tip_pos() is not None
    arrow.default_updater(arrow)
    arrow.set_arrow_size(0.5)
    assert arrow.reversed_arrow is False
    arrow.reversed_arrow = True
    assert arrow.reversed_arrow is True
    arrow.flip_arrow()
    # setting the same value must not flip again
    arrow.reversed_arrow = True
    arrow.reversed_arrow = False
    arrow.update()

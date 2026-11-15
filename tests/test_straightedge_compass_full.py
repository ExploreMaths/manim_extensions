# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Behavioural coverage for the vendored straightedge-compass package."""

import numpy as np
import pytest
from manim import Arc, Line, TAU, UP

from manim_extensions.straightedge_compass.compass import (
    Compass,
    CompassDrawArc,
)
from manim_extensions.straightedge_compass.geometry import (
    P,
    angle_of,
    as_point,
    circle_circle_intersection,
    circle_line_intersection,
    distance,
    leftmost,
    line_line_intersection,
    lowermost,
    midpoint,
    other,
    point_on,
    rightmost,
    rotate_vec,
    unit,
    uppermost,
)
from manim_extensions.straightedge_compass.marks import MarkedPoint
from manim_extensions.straightedge_compass.scene import EuclidScene
from manim_extensions.straightedge_compass.straightedge import (
    PencilTip,
    RulerDraw,
    Straightedge,
)


class QuietEuclidScene(EuclidScene):
    """EuclidScene whose stage operations are no-ops, for fast unit checks."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.plays = []
        self.added = []

    def play(self, *args, **kwargs):
        self.plays.append((args, kwargs))

    def wait(self, *args, **kwargs):
        pass

    def add(self, *args, **kwargs):
        self.added.extend(args)


# ---------------------------------------------------------------- geometry


def test_point_helpers_cover_2d_and_3d_inputs():
    assert np.allclose(P(1, 2), [1.0, 2.0, 0.0])
    assert np.allclose(as_point([1, 2]), [1.0, 2.0, 0.0])
    assert np.allclose(as_point([1, 2, 3]), [1.0, 2.0, 3.0])
    assert distance([0, 0], [3, 4]) == pytest.approx(5.0)
    assert np.allclose(midpoint(P(0, 0), P(2, 4)), [1.0, 2.0, 0.0])
    assert angle_of(P(0, 0), P(0, 1)) == pytest.approx(np.pi / 2)
    assert np.allclose(unit(P(3, 4)), [0.6, 0.8, 0.0])
    with pytest.raises(ValueError):
        unit(P(0, 0))
    assert np.allclose(rotate_vec(P(1, 0), np.pi / 2), [0.0, 1.0, 0.0], atol=1e-9)
    assert np.allclose(point_on(P(0, 0), 2, 0), [2.0, 0.0, 0.0], atol=1e-9)


def test_circle_circle_all_intersection_branches():
    # concentric
    assert circle_circle_intersection(P(0, 0), 1, P(0, 0), 2) == []
    # too far apart
    assert circle_circle_intersection(P(0, 0), 1, P(10, 0), 1) == []
    # one contained in the other
    assert circle_circle_intersection(P(0, 0), 1, P(0.1, 0), 0.5) == []
    # tangent externally
    pts = circle_circle_intersection(P(0, 0), 1, P(2, 0), 1)
    assert len(pts) == 1
    assert np.allclose(pts[0], [1, 0, 0], atol=1e-7)
    # two intersections
    pts = circle_circle_intersection(P(0, 0), 2, P(2, 0), 2)
    assert len(pts) == 2
    assert {round(float(p[0]), 6) for p in pts} == {1.0}
    assert {round(float(p[1]), 6) for p in pts} == {
        round(np.sqrt(3), 6),
        -round(np.sqrt(3), 6),
    }


def test_line_line_parallel_and_intersecting():
    assert line_line_intersection(P(0, 0), P(1, 0), P(0, 1), P(1, 1)) is None
    hit = line_line_intersection(P(0, 0), P(1, 1), P(0, 1), P(1, 0))
    assert np.allclose(hit, [0.5, 0.5, 0.0])


def test_circle_line_none_tangent_and_two_points():
    # line misses the circle entirely
    assert circle_line_intersection(P(0, 0), 1, P(-2, 2), P(2, 2)) == []
    # tangent at (0, 1)
    pts = circle_line_intersection(P(0, 0), 1, P(-2, 1), P(2, 1))
    assert len(pts) == 1
    # secant
    pts = circle_line_intersection(P(0, 0), 1, P(-2, 0), P(2, 0))
    assert len(pts) == 2
    assert {round(float(p[0]), 6) for p in pts} == {-1.0, 1.0}


def test_selectors_and_other_error():
    pts = [P(0, 0), P(2, 1), P(-1, -3)]
    assert np.allclose(uppermost(pts), [2, 1, 0])
    assert np.allclose(lowermost(pts), [-1, -3, 0])
    assert np.allclose(leftmost(pts), [-1, -3, 0])
    assert np.allclose(rightmost(pts), [2, 1, 0])
    assert np.allclose(other([P(0, 0), P(1, 1)], P(0, 0)), [1, 1, 0])
    with pytest.raises(ValueError):
        other([P(0, 0), P(0, 0)], P(0, 0))


# ----------------------------------------------------------------- marks


def test_marked_point_with_label_direction_and_without_label():
    marked = MarkedPoint(P(1, 2), "A", direction=UP, radius=0.1)
    assert marked.label_mob is not None
    assert np.allclose(marked.point, [1, 2, 0])
    bare = MarkedPoint(P(0, 0), None)
    assert bare.label_mob is None
    # zero direction -> next_to(UP) fallback
    zero = MarkedPoint(P(0, 0), "B", direction=P(0, 0))
    assert zero.label_mob is not None


# --------------------------------------------------------------- compass


def test_compass_layout_clip_pose_and_copy():
    compass = Compass(radius=1.5)
    # the clamped radius is used for layout, while the stored radius stays
    clipped = compass._layout(P(0, 0), 99, 0)
    assert np.linalg.norm(clipped[1] - clipped[0]) <= 2 * 2.1
    compass.pose(P(0, 0), radius=99)
    assert np.linalg.norm(compass.pencil_lead.get_center()) <= 2 * 2.1
    assert np.allclose(compass.needle_leg.get_start(), [0, 0, 0])
    # zero radius clipped up to the minimum for the geometry
    compass.pose(P(1, 1), radius=0)
    assert np.linalg.norm(compass.pencil_lead.get_center() - P(1, 1)) == pytest.approx(
        0.05
    )
    # pencil_point uses the stored radius
    compass.radius = 0.05
    assert np.allclose(compass.pencil_point(), [1.05, 1, 0])
    assert np.allclose(compass.pencil_point(np.pi / 2), [1, 1.05, 0])
    copy = compass.rotated_copy(0)
    assert copy.radius == compass.radius


def test_compass_draw_arc_interpolates_both_ends():
    compass = Compass()
    arc = Arc(radius=1.5, start_angle=0, angle=1e-6, arc_center=P(0, 0))
    anim = CompassDrawArc(compass, arc, TAU)
    anim.interpolate_mobject(1.0)
    assert arc.get_num_curves() > 0
    anim.interpolate_mobject(0.0)


# ------------------------------------------------------------ straightedge


def test_straightedge_build_and_pose():
    ruler = Straightedge(ruler_length=4, ruler_width=0.5)
    assert ruler.ruler_length == 4
    assert len(ruler) >= 3
    ruler.pose(P(-1, 0), P(1, 0))
    assert np.allclose(ruler.get_center()[1], 0.25, atol=0.3)
    ruler.pose(P(0, 0), P(0, 1))


def test_pencil_tip_and_ruler_draw():
    tip = PencilTip(P(1, 1))
    assert np.allclose(tip.get_center()[:2], [1, 1], atol=1e-6)
    line = Line(P(0, 0), P(0, 0))
    draw = RulerDraw(line, tip, P(0, 0), P(2, 0))
    draw.interpolate_mobject(0.5)
    assert np.allclose(line.get_end()[:2], [1, 0], atol=1e-6)
    assert np.allclose(tip.get_center()[:2], [1, 0], atol=1e-6)
    draw.interpolate_mobject(1.0)
    assert np.allclose(line.get_end()[:2], [2, 0], atol=1e-6)


# ----------------------------------------------------------------- scene


def test_euclid_scene_setup_intro_and_marks():
    scene = QuietEuclidScene()
    scene.setup()
    assert scene._compass_away and scene._ruler_away
    scene.intro("Demo")
    assert scene.plays
    marked = scene.mark_point(P(0, 0), "A")
    assert marked.label_mob is not None
    scene.mark_point(P(1, 1))
    scene.flash_points(P(0, 0), P(1, 1))


def test_euclid_scene_draw_arc_and_circle():
    scene = QuietEuclidScene()
    scene.setup()
    arc = scene.draw_arc(P(0, 0), 1, angle=TAU / 2, run_time=0.2, keep_compass=True)
    assert isinstance(arc, Arc)
    assert not scene._compass_away
    # compass already on stage -> the short re-pose branch
    arc2 = scene.draw_arc(P(1, 0), 1, run_time=0.2, keep_compass=True)
    assert isinstance(arc2, Arc)
    # circle with explicit radius
    circle = scene.draw_circle(P(0, 0), radius=2, run_time=0.2)
    assert isinstance(circle, Arc)
    # circle through a point
    circle2 = scene.draw_circle(P(0, 0), through=P(3, 0), run_time=0.2)
    assert isinstance(circle2, Arc)
    with pytest.raises(ValueError):
        scene.draw_circle(P(0, 0))


def test_euclid_scene_ruler_branches_and_error():
    scene = QuietEuclidScene()
    scene.setup()
    segment = scene.draw_segment(P(0, 0), P(2, 0), run_time=0.2, keep_ruler=True)
    assert isinstance(segment, Line)
    assert not scene._ruler_away
    # ruler already present -> short re-pose branch, and keep it
    segment2 = scene.draw_segment(P(0, 0), P(0, 2), run_time=0.2, keep_ruler=True)
    assert isinstance(segment2, Line)
    scene.retire_ruler()
    assert scene._ruler_away

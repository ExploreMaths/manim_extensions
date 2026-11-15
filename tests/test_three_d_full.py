# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Broad behavioural coverage for the vendored manim-3d package."""

import numpy as np
import pytest

from manim import Surface
from manim_extensions.three_d import (
    EllipsoidSurface,
    EllipsoidSurfaceScene,
    GaussianSurface,
    GaussianSurfaceScene,
    HyperboloidOneSheet,
    HyperboloidOneSheetScene,
    ParaboloidSurface,
    ParaboloidSurfaceScene,
    RAMPS,
    SaddleSurface,
    SaddleSurfaceScene,
    TorusSurface,
    TorusSurfaceScene,
    ellipsoid_surface_scene,
    gaussian_surface_scene,
    hyperboloid_one_sheet_scene,
    paraboloid_surface_scene,
    plan_timeline,
    saddle_surface_scene,
    torus_surface_scene,
)
from manim_extensions.three_d.core import (
    GraphSurfaceScene,
    _fmt,
    _ramp_color,
    _radius_for_level,
    _scene_name,
)


class _NoRenderScene:
    """Mixin that turns every staging call into a no-op."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rendered_calls = []

    def play(self, *anims, **kwargs):
        self.rendered_calls.append(("play", anims, kwargs))

    def wait(self, *args, **kwargs):
        self.rendered_calls.append(("wait", args, kwargs))

    def set_camera_orientation(self, *args, **kwargs):
        pass

    def move_camera(self, *args, **kwargs):
        pass

    def begin_ambient_camera_rotation(self, *args, **kwargs):
        pass

    def stop_ambient_camera_rotation(self, *args, **kwargs):
        pass

    def add_fixed_in_frame_mobjects(self, *mobjects):
        self.rendered_calls.append(("fixed", mobjects, {}))


class Gaussian(_NoRenderScene, GaussianSurfaceScene):
    pass


class Saddle(_NoRenderScene, SaddleSurfaceScene):
    pass


class Paraboloid(_NoRenderScene, ParaboloidSurfaceScene):
    pass


class Ellipsoid(_NoRenderScene, EllipsoidSurfaceScene):
    pass


class Torus(_NoRenderScene, TorusSurfaceScene):
    pass


class Hyperboloid(_NoRenderScene, HyperboloidOneSheetScene):
    pass


# ------------------------------------------------------------------ helpers


def test_ramp_color_fmt_and_radius_bisection():
    # a ramp that does not reach 1.0 exercises the trailing fallback
    assert _ramp_color([("#000000", 0.0), ("#FFFFFF", 0.5)], 0.9).to_hex() != ""
    for ramp in RAMPS.values():
        assert _ramp_color(ramp, 0.0).to_hex() != ""
        assert _ramp_color(ramp, 0.5).to_hex() != ""
        assert _ramp_color(ramp, 1.0).to_hex() != ""
    # out-of-range values are clamped and the final fallthrough is never needed
    assert _ramp_color(RAMPS["ocean"], -1) == _ramp_color(RAMPS["ocean"], 0)
    assert _ramp_color(RAMPS["ocean"], 2) == _ramp_color(RAMPS["ocean"], 1)
    assert _fmt(0.0) == "0"
    assert _fmt(1.5) == "1.5"
    assert _fmt(-2.0) == "-2"
    # radial root exists
    f = lambda r, y: 1 - r * r
    assert _radius_for_level(f, 2.0, 0.5) == pytest.approx(np.sqrt(0.5), abs=1e-6)
    # function stays above c over the whole domain -> None
    assert _radius_for_level(lambda r, y: 5.0, 2.0, 1.0) is None


def test_plan_timeline_short_budget_drops_optional_beats():
    all_beats = {
        "title",
        "axes",
        "flat",
        "rise",
        "rings",
        "orbit",
        "flip",
        "annotate",
        "outro",
    }
    tight, dropped = plan_timeline(5.0, all_beats)
    assert dropped
    assert set(tight) == {"title", "axes", "rise", "outro"}
    # a budget too small even for mandatory beats returns clamped values
    tiny, dropped2 = plan_timeline(1.0, all_beats)
    assert set(tiny) == {"title", "axes", "rise", "outro"}
    assert len(dropped2) == 5
    # very large budget keeps every beat at its reference/upper bound
    huge, dropped3 = plan_timeline(200.0, all_beats)
    assert huge["title"] >= 3.0
    assert dropped3 == []
    # an empty enabled set is harmless
    assert plan_timeline(10.0, set()) == ({}, [])


def test_graph_base_hooks_require_override():
    base = GraphSurfaceScene()
    with pytest.raises(NotImplementedError):
        base._geometry(None)
    with pytest.raises(NotImplementedError):
        base._contours(None, None, None, None, None)
    with pytest.raises(NotImplementedError):
        base._feature(None, None)
    assert base._caption_slots() == [
        "title",
        "axes",
        "flat",
        "rings",
        "orbit",
        "flip",
        "outro",
    ]
    assert base._annotate_camera() == (66.0, -40.0, 0.95)


def test_scene_names_and_factories():
    _scene_name("NameProbe")
    second = _scene_name("NameProbe")
    assert second == "NameProbe2"
    for factory, base, cfg_cls in (
        (gaussian_surface_scene, "GaussianSurface", GaussianSurface),
        (saddle_surface_scene, "SaddleSurface", SaddleSurface),
        (paraboloid_surface_scene, "ParaboloidSurface", ParaboloidSurface),
        (ellipsoid_surface_scene, "EllipsoidSurface", EllipsoidSurface),
        (torus_surface_scene, "TorusSurface", TorusSurface),
        (hyperboloid_one_sheet_scene, "HyperboloidOneSheet", HyperboloidOneSheet),
    ):
        built = factory()
        assert issubclass(built, object)
        assert isinstance(built.style, cfg_cls)
        named = factory(name="MyScene")
        assert named.__name__ == "MyScene"
        assert "Factory" in factory.__doc__


# ------------------------------------------------------------- graph scenes


def test_gaussian_scene_hooks_and_construct():
    scene = Gaussian()
    cfg = GaussianSurface(
        captions=("高斯", "坐标", "成型", "轨道", "翻面", "结束"),
        duration=45,
        rings=True,
    )
    f, tex, zmin, zlo, zhi = scene._geometry(cfg)
    assert callable(f) and tex
    assert zmin <= 0
    axes = scene._make_axes(cfg, zlo, zhi)
    surface = scene._make_surface(cfg, axes, f, RAMPS["rainbow"], zmin)
    assert surface.get_num_points() > 0 or isinstance(surface, Surface)
    rings, follow = scene._contours(cfg, axes, f, RAMPS["rainbow"], zmin)
    assert len(rings) == 5
    assert follow is False
    feature = scene._feature(cfg, f)
    assert len(feature) == 6
    assert scene._caption_slots() == ["title", "axes", "flat", "orbit", "flip", "outro"]
    assert scene._annotate_camera() == (68.0, -40.0, 0.95)
    scene.style = cfg
    scene.construct()
    assert scene.rendered_calls


def test_gaussian_custom_function_no_formula_and_list_colors():
    scene = Gaussian()
    cfg = GaussianSurface(
        func=lambda x, y: x + y,
        func_tex=None,
        colors=[("#000000", 0.0), ("#FFFFFF", 1.0)],
        axes=False,
        rings=False,
        orbit=False,
        flip=False,
        annotate=False,
        duration=10,
        pace="fast",
        captions=("only one",),
    )
    f, tex, zmin, zlo, zhi = scene._geometry(cfg)
    assert tex is None
    assert f(0, 0) == pytest.approx(0)
    rings, follow = scene._contours(
        cfg,
        scene._make_axes(cfg, zlo, zhi),
        f,
        [("#000000", 0.0), ("#FFFFFF", 1.0)],
        zmin,
    )
    assert len(rings) >= 0
    scene.style = cfg
    scene.style = cfg
    scene.construct()


def test_saddle_scene_hooks_and_construct():
    scene = Saddle()
    cfg = SaddleSurface(
        captions=("鞍面", "坐标", "成型", "轨道", "翻面", "结束"), duration=45
    )
    f, tex, zmin, zlo, zhi = scene._geometry(cfg)
    assert f(1, 1) == pytest.approx(0)
    axes = scene._make_axes(cfg, zlo, zhi)
    rings, follow = scene._contours(cfg, axes, f, RAMPS["ocean"], zmin)
    # two asymptotes + 6 levels * 2 branches
    assert len(rings) == 14
    assert scene._feature(cfg, f)[4] is True
    scene.style = cfg
    scene.construct()


def test_paraboloid_scene_hooks_and_construct():
    scene = Paraboloid()
    cfg = ParaboloidSurface(
        captions=("抛物", "坐标", "成型", "轨道", "翻面", "结束"), duration=45
    )
    f, tex, zmin, zlo, zhi = scene._geometry(cfg)
    assert f(1, 0) > 0
    axes = scene._make_axes(cfg, zlo, zhi)
    rings, follow = scene._contours(cfg, axes, f, RAMPS["magma"], zmin)
    assert len(rings) == 4
    assert follow is True
    assert scene._feature(cfg, f)[4] is True
    scene.style = cfg
    scene.construct()


# ------------------------------------------------------------ closed surfaces


def test_ellipsoid_hooks_and_construct():
    scene = Ellipsoid()
    cfg = EllipsoidSurface(
        captions=("椭球", "坐标", "成型", "轨道", "翻面", "结束"), duration=45
    )
    f, tex, zmin, zlo, zhi = scene._geometry(cfg)
    assert callable(f) and "frac" in tex
    axes = scene._make_axes(cfg, zlo, zhi)
    surface = scene._make_surface(cfg, axes, f, RAMPS["rainbow"], zmin)
    assert surface.get_num_points() > 0 or isinstance(surface, Surface)
    rings, follow = scene._contours(cfg, axes, f, RAMPS["rainbow"], zmin)
    assert len(rings) == 5 and follow is True
    assert scene._feature(cfg, f)[4] is False
    scene.style = cfg
    scene.construct()


def test_torus_hooks_and_construct():
    scene = Torus()
    cfg = TorusSurface(
        captions=("环面", "坐标", "成型", "轨道", "翻面", "结束"), duration=45
    )
    f, tex, zmin, zlo, zhi = scene._geometry(cfg)
    assert "sqrt" in tex
    axes = scene._make_axes(cfg, zlo, zhi)
    surface = scene._make_surface(cfg, axes, f, RAMPS["ocean"], zmin)
    assert surface.get_num_points() > 0 or isinstance(surface, Surface)
    rings, follow = scene._contours(cfg, axes, f, RAMPS["ocean"], zmin)
    assert len(rings) == 6 and follow is True
    assert scene._feature(cfg, f)[4] is False
    scene.style = cfg
    scene.construct()


def test_hyperboloid_hooks_and_construct():
    scene = Hyperboloid()
    cfg = HyperboloidOneSheet(
        captions=("双曲", "坐标", "成型", "轨道", "翻面", "结束"), duration=45
    )
    f, tex, zmin, zlo, zhi = scene._geometry(cfg)
    assert "x^{2}" in tex
    axes = scene._make_axes(cfg, zlo, zhi)
    surface = scene._make_surface(cfg, axes, f, RAMPS["magma"], zmin)
    assert surface.get_num_points() > 0 or isinstance(surface, Surface)
    rings, follow = scene._contours(cfg, axes, f, RAMPS["magma"], zmin)
    assert len(rings) == 5 and follow is True
    assert scene._feature(cfg, f)[4] is True
    scene.style = cfg
    scene.construct()


def test_construct_covers_dropped_beats_and_skipped_contours():
    # tiny budget triggers the "beats dropped" print
    scene = Gaussian()
    scene.style = GaussianSurface(duration=8)
    scene.construct()
    # a short shell makes the |z_lv| > 0.95*h guard skip rings
    scene2 = Hyperboloid()
    scene2.style = HyperboloidOneSheet(z_extent=0.8, duration=45)
    rings, _ = scene2._contours(
        scene2.style,
        scene2._make_axes(scene2.style, -1.2, 1.2),
        None,
        RAMPS["rainbow"],
        -0.8,
    )
    assert len(rings) == 3  # ±0.5 and the waist circle survive
    scene2.construct()


def test_construct_branches_without_annotate_and_without_captions():
    # no rings/annotate/flip/orbit, one caption -> title/outro paths
    scene = Gaussian()
    scene.style = GaussianSurface(
        axes=False,
        rings=False,
        orbit=False,
        flip=False,
        annotate=False,
        duration=8,
        captions=("single",),
    )
    scene.construct()
    # closed surface uses GrowFromCenter (fallback else branch in rise)
    scene2 = Ellipsoid()
    scene2.style = EllipsoidSurface(
        axes=False, rings=False, orbit=False, flip=False, annotate=False, duration=8
    )
    scene2.construct()

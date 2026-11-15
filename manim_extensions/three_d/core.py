# SPDX-FileCopyrightText: 2026 FTZ-OPUS
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
# patched: use the package-wide CJK font resolver instead of the macOS-only PingFang SC

# -*- coding: utf-8 -*-
"""manim_extensions.three_d —— Manim 三维几何与动画库(闭式管面与图曲面预设)。

六件已封装:高斯曲面 / 马鞍面 / 抛物面 / 椭球面 / 圆环面 / 单叶双曲面。
目标是"几行代码出片":
节拍(标题/坐标轴/成型/等高线/环绕/翻面/标注/收尾)的时长与去留全部参数化,
总时长按权重配速——压到 10 秒动画主线一个不少,放不下时自动按优先级砍可选拍。

用法(见 examples/demo_*.py):

    from manim_extensions.three_d import gaussian_surface_scene, saddle_surface_scene, paraboloid_surface_scene

    class GaussianSurface(gaussian_surface_scene(captions=(...), duration=12)): pass
    class SaddleSurface(saddle_surface_scene(captions=(...))): pass
    class ParaboloidSurface(paraboloid_surface_scene(pace="fast", name="ParaboloidFast")): pass

    # ~/venvs/manim/bin/manim -qh demo_saddle.py SaddleSurface

约定:duration 指"内容预算"(不含字幕换行,每次换行另加 ~0.9s 随配速缩放);
每拍时间 = 参考时长 × (duration/45) 再夹进 [下限, 参考×上限倍率],
压不下时按可砍优先级(等高线→平面→标注→环绕→翻面)自动砍拍并打印。
字幕槽按曲面各自的节拍序列对位(见各 Scene 的 _caption_slots)。
"""

from __future__ import annotations
from manim import (
    BLUE,
    Create,
    DEGREES,
    DOWN,
    DashedLine,
    DashedVMobject,
    Dot3D,
    FadeIn,
    FadeOut,
    GREEN,
    GrowFromCenter,
    LaggedStart,
    ManimColor,
    MathTex,
    ORANGE,
    ORIGIN,
    PI,
    ParametricFunction,
    RED,
    RIGHT,
    Rotate,
    Surface,
    TAU,
    TEAL,
    Text,
    ThreeDAxes,
    ThreeDScene,
    Transform,
    UP,
    UR,
    VGroup,
    WHITE,
    Write,
    YELLOW,
    interpolate_color,
    smooth,
)

from ..mobjects import DEFAULT_CJK_FONT
import numpy as np
from dataclasses import dataclass
from typing import Any, Callable, Optional, Sequence

__all__ = [
    "GaussianSurface",
    "SaddleSurface",
    "ParaboloidSurface",
    "EllipsoidSurface",
    "TorusSurface",
    "HyperboloidOneSheet",
    "gaussian_surface_scene",
    "saddle_surface_scene",
    "paraboloid_surface_scene",
    "ellipsoid_surface_scene",
    "torus_surface_scene",
    "hyperboloid_one_sheet_scene",
    "GaussianSurfaceScene",
    "SaddleSurfaceScene",
    "ParaboloidSurfaceScene",
    "EllipsoidSurfaceScene",
    "TorusSurfaceScene",
    "HyperboloidOneSheetScene",
    "plan_timeline",
    "RAMPS",
    "PACE",
]

# ---------------- 配色主题 ----------------
RAMPS = {
    "rainbow": [
        ("#123a6d", 0.00),
        ("#1e6fd9", 0.15),
        ("#18a5a5", 0.32),
        ("#63c74d", 0.50),
        ("#f5d033", 0.68),
        ("#f28c28", 0.84),
        ("#e34a33", 1.00),
    ],
    "ocean": [
        ("#0b1d3a", 0.00),
        ("#14508c", 0.40),
        ("#1e88b5", 0.70),
        ("#7fd4c1", 1.00),
    ],
    "magma": [
        ("#1a0533", 0.00),
        ("#5b1a8a", 0.35),
        ("#c0369d", 0.60),
        ("#f2603c", 0.80),
        ("#ffd166", 1.00),
    ],
}

# ---------------- 节拍表 ----------------
# (名称, 参考时长s, 下限s, 时长上限=参考×倍率, 可砍优先级:1最先砍,None=必留)
BEATS = [
    ("title", 3.0, 1.6, 2.0, None),
    ("axes", 2.4, 1.2, 1.6, None),
    ("flat", 2.2, 1.0, 1.6, 2),
    ("rise", 4.2, 2.0, 1.8, None),
    ("rings", 2.6, 1.2, 1.8, 1),
    ("orbit", 9.0, 2.5, 2.5, 4),
    ("flip", 10.0, 3.0, 1.8, 5),
    ("annotate", 5.4, 2.4, 1.8, 3),
    ("outro", 6.2, 2.6, 1.8, None),
]
PACE = {"fast": 10.0, "normal": 24.0, "full": 45.0}


def plan_timeline(duration: float, enabled: set) -> tuple[dict, list]:
    """把 duration 分配到启用的节拍。

    等比缩放,每拍夹在 [下限, 参考×上限倍率] 内,迭代到收敛;
    全体顶到下限仍放不下 → 按优先级砍可选拍重排;全体顶到上限还不够填 → 接受偏短。
    返回 (节拍时长dict, 被砍节拍list)。
    """
    active = [b for b in BEATS if b[0] in enabled]
    dropped = []
    while True:
        t = {b[0]: float(b[1]) for b in active}
        for _ in range(80):
            total = sum(t.values())
            if total <= 0:
                break
            k = duration / total
            moved = False
            for b in active:
                lo, hi = b[2], b[1] * b[3]
                nt = min(max(t[b[0]] * k, lo), hi)
                if abs(nt - t[b[0]]) > 1e-9:
                    moved = True
                t[b[0]] = nt
            if not moved:
                break
        if sum(t.values()) <= duration + 0.05:
            return t, dropped
        cands = [b for b in active if b[4] is not None]
        if not cands:
            return t, dropped
        victim = min(cands, key=lambda b: b[4])
        active = [b for b in active if b[0] is not victim[0]]
        dropped.append(victim[0])


def _ramp_color(ramp: Any, t: float) -> Any:
    """色带取色:t∈[0,1] 为色带位置。"""
    t = min(max(t, 0.0), 1.0)
    for (c1, v1), (c2, v2) in zip(ramp, ramp[1:]):
        if v1 <= t <= v2:
            return interpolate_color(
                ManimColor(c1), ManimColor(c2), (t - v1) / (v2 - v1)
            )
    return ManimColor(ramp[-1][0])


def _radius_for_level(f: Any, d_max: float, c: float, n: int = 60) -> Optional[float]:
    """解 f(r,0)=c 的最近根(沿 +x 二分;径向单调曲面精确,其他近似)。"""
    lo, hi = 0.0, d_max
    if f(hi, 0.0) > c:
        return None
    for _ in range(n):
        mid = (lo + hi) / 2
        if f(mid, 0.0) > c:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def _fmt(v: float) -> str:
    """0.00→0, 1.50→1.5:坐标标注去尾零。"""
    return f"{v:.2f}".rstrip("0").rstrip(".")


# ---------------- 配置 ----------------
@dataclass
class GaussianSurface:
    """高斯曲面(泛化为任意 z=f(x,y) 图曲面)的全部可调参数。"""

    func: Optional[Callable] = None  # z=f(x,y);None=内置高斯
    func_tex: Optional[str] = None  # 角落公式;None=自定义函数且不显示公式
    domain: tuple = (-2.6, 2.6)  # x/y 定义域
    resolution: tuple = (40, 40)  # 曲面网格密度
    colors: object = "rainbow"  # RAMPS 主题名或 [(hex,0~1)...]
    height: float = 1.0  # 峰值自动归一化到该高度
    axes: bool = True
    rings: bool = True  # 底面等高线(径向近似)
    orbit: bool = True  # 360° 环绕
    flip: bool = True  # 翻面展示底面
    annotate: bool = True  # 峰顶标注
    captions: Optional[Sequence] = None  # 字幕按槽位对位,不传=无
    duration: Optional[float] = None  # 内容预算(秒);None=用 pace
    pace: str = "full"  # fast=10 / normal=24 / full=45
    background: str = "#050810"
    camera_phi: float = 72.0
    camera_theta: float = -55.0
    zoom: float = 0.95

    def resolve(self) -> Any:
        """返回 (f, tex):函数补默认,公式补默认。"""
        if self.func is None:
            f = lambda x, y: float(np.exp(-(x * x + y * y)))
            tex = r"z = e^{-x^{2}-y^{2}}" if self.func_tex is None else self.func_tex
        else:
            f = self.func
            tex = self.func_tex
        return f, tex


@dataclass
class SaddleSurface:
    """马鞍面 z = x² - y²(双曲抛物面),几何固定、呈现全参数化。"""

    domain: tuple = (-2.2, 2.2)
    resolution: tuple = (44, 44)
    colors: object = "rainbow"
    height: float = 1.2  # 归一化:山脊 = +H,低谷 = -H(对称)
    axes: bool = True
    rings: bool = True  # 双曲线族等高线 + 渐近线(地板)
    orbit: bool = True
    flip: bool = True
    annotate: bool = True  # 鞍点标注(投影 HUD 标签)
    captions: Optional[Sequence] = None
    duration: Optional[float] = None
    pace: str = "full"
    background: str = "#050810"
    camera_phi: float = 70.0
    camera_theta: float = -50.0
    zoom: float = 0.95


@dataclass
class ParaboloidSurface:
    """抛物面 z = x² + y²(椭圆抛物面),几何固定、呈现全参数化。"""

    domain: tuple = (-2.2, 2.2)
    resolution: tuple = (44, 44)
    colors: object = "rainbow"
    height: float = 1.2  # 归一化:碗沿 = H,碗底 = 0
    axes: bool = True
    rings: bool = True  # 贴面同心圆等高线(翻面随曲面转)
    orbit: bool = True
    flip: bool = True
    annotate: bool = True  # 顶点标注(投影 HUD 标签)
    captions: Optional[Sequence] = None
    duration: Optional[float] = None
    pace: str = "full"
    background: str = "#050810"
    camera_phi: float = 70.0
    camera_theta: float = -50.0
    zoom: float = 0.95


@dataclass
class EllipsoidSurface:
    """椭球面 x²/a²+y²/b²+z²/c²=1 —— 闭曲面(参数曲面模式首个成员)。"""

    semi_axes: tuple = (2.4, 1.6, 1.2)  # (a, b, c) 半轴
    resolution: tuple = (44, 56)  # 经纬网格密度
    colors: object = "rainbow"
    axes: bool = True
    rings: bool = True  # 贴面水平椭圆环(翻面随转)
    orbit: bool = True
    flip: bool = True  # 闭曲面翻转 = 转到背面
    annotate: bool = True  # 上顶点标注(3D 标签)
    captions: Optional[Sequence] = None
    duration: Optional[float] = None
    pace: str = "full"
    background: str = "#050810"
    camera_phi: float = 70.0
    camera_theta: float = -50.0
    zoom: float = 0.95


@dataclass
class TorusSurface:
    """圆环面 (√(x²+y²)−R)²+z²=r² —— 闭曲面,参考图比例 R:r=4:1。"""

    major_radius: float = 2.0  # 环半径 R(管中心圆)
    minor_radius: float = 0.5  # 管半径 r
    resolution: tuple = (56, 24)  # (大圆 θ, 管 φ) 网格密度
    colors: object = "rainbow"
    axes: bool = True
    rings: bool = True  # 贴面水平成对圆环(翻面随转)
    orbit: bool = True
    flip: bool = True
    annotate: bool = True  # 最高点标注(3D 标签+天线)
    captions: Optional[Sequence] = None
    duration: Optional[float] = None
    pace: str = "full"
    background: str = "#050810"
    camera_phi: float = 70.0
    camera_theta: float = -50.0
    zoom: float = 0.95


@dataclass
class HyperboloidOneSheet:
    """单叶双曲面 x²+y²−z²=1 —— 闭式管面(参数曲面),腰圆为签名特征。"""

    waist_radius: float = 1.0  # 腰圆半径 a(=b)
    z_extent: float = 1.5  # 上下截断高度 ±h
    resolution: tuple = (36, 48)  # (z 向, 周 向) 网格密度
    colors: object = "rainbow"
    axes: bool = True
    rings: bool = True  # 贴面水平圆族(含腰圆,翻面随转)
    orbit: bool = True
    flip: bool = True
    annotate: bool = True  # 腰圆前点标注(HUD 标签,无虚线)
    captions: Optional[Sequence] = None
    duration: Optional[float] = None
    pace: str = "full"
    background: str = "#050810"
    camera_phi: float = 70.0
    camera_theta: float = -50.0
    zoom: float = 0.95


# ---------------- 节拍骨架(图曲面通用) ----------------
class _GraphSurfaceScene(ThreeDScene):
    """子类提供 style(配置)与钩子:_geometry/_contours/_feature/_caption_slots。

    图曲面(高斯/马鞍/抛物面)直接用;闭曲面(椭球等)设 uses_flat=False:
    无"平面起步"拍,成型拍改为 GrowFromCenter 充气,坐标轴三轴等比缩放防畸变。
    """

    style = None
    uses_flat = True

    # ---- 钩子 ----
    def _geometry(self, cfg: Any) -> Any:
        """-> (f 归一化函数, tex 公式, zmin_n, ax_z_lo, ax_z_hi)"""
        raise NotImplementedError

    def _contours(self, cfg: Any, axes: Any, f: Any, ramp: Any, zmin_n: Any) -> Any:
        """-> (等高线 VGroup, 是否跟随曲面翻面)"""
        raise NotImplementedError

    def _feature(self, cfg: Any, f: Any) -> Any:
        """-> (px, py, pz, tag_tex, 用HUD标签, 虚线起点z)"""
        raise NotImplementedError

    def _caption_slots(self) -> Any:
        """字幕槽位序列(位置对位)。"""
        return ["title", "axes", "flat", "rings", "orbit", "flip", "outro"]

    def _annotate_camera(self) -> Any:
        """标注拍相机角度 (phi, theta, zoom)。"""
        return 66.0, -40.0, 0.95

    def _make_axes(self, cfg: Any, ax_z_lo: Any, ax_z_hi: Any) -> Any:
        """图曲面默认轴:x/y 等长,z 按高度范围。"""
        d0, d1 = cfg.domain
        axes = ThreeDAxes(
            x_range=[d0 - 0.4, d1 + 0.4, 1],
            y_range=[d0 - 0.4, d1 + 0.4, 1],
            z_range=[ax_z_lo, ax_z_hi, cfg.height / 2],
            x_length=7.2,
            y_length=7.2,
            z_length=3.4,
        )
        return axes.set_stroke(opacity=0.55)

    def _make_surface(self, cfg: Any, axes: Any, f: Any, ramp: Any, zmin_n: Any) -> Any:
        """图曲面默认:z=f(x,y) 图,色带铺满 [zmin_n, height]。"""
        d0, d1 = cfg.domain
        s = Surface(
            lambda u, v: axes.c2p(u, v, f(u, v)),
            u_range=(d0, d1),
            v_range=(d0, d1),
            resolution=cfg.resolution,
            fill_opacity=1.0,
            stroke_color=WHITE,
            stroke_width=0.35,
            stroke_opacity=0.16,
        )
        s.set_fill_by_value(
            axes=axes,
            colorscale=[(c, zmin_n + p * (cfg.height - zmin_n)) for c, p in ramp],
            axis=2,
        )
        return s

    # ---- 主流程 ----
    def construct(self) -> Any:
        """construct."""
        cfg = self.style
        ramp = RAMPS[cfg.colors] if isinstance(cfg.colors, str) else list(cfg.colors)
        f_n, func_tex, zmin_n, ax_z_lo, ax_z_hi = self._geometry(cfg)
        duration = (
            cfg.duration if cfg.duration is not None else PACE.get(cfg.pace, 45.0)
        )

        enabled = {"title", "rise", "outro"}
        if self.uses_flat:
            enabled.add("flat")
        for name, flag in (
            ("axes", cfg.axes),
            ("rings", cfg.rings),
            ("orbit", cfg.orbit),
            ("flip", cfg.flip),
            ("annotate", cfg.annotate),
        ):
            if flag:
                enabled.add(name)
        t, dropped = plan_timeline(duration, enabled)
        if dropped:
            print(
                f"[manim_extensions.three_d] {duration}s 预算放不下全部节拍,自动砍掉: {' → '.join(dropped)}"
            )
        swap_t = min(max(0.9 * duration / 45.0, 0.35), 1.0)
        print(
            "[manim_extensions.three_d] 节拍预算:",
            ", ".join(f"{k}={v:.1f}s" for k, v in t.items()),
            f"(字幕换行 {swap_t:.2f}s/次)",
        )

        slots = self._caption_slots()
        cap_map = dict(zip(slots, list(cfg.captions) if cfg.captions else []))
        self.camera.background_color = cfg.background
        self.set_camera_orientation(
            phi=cfg.camera_phi * DEGREES,
            theta=cfg.camera_theta * DEGREES,
            zoom=cfg.zoom,
        )

        # ---------- 字幕 HUD(文字+公式 VGroup,固定屏幕系) ----------
        cur_cap = None

        def make_cap(text: str, tex: Optional[str] = None, live: bool = True) -> VGroup:
            """make_cap."""
            if tex:
                text = f"{text} ·" if not text.rstrip().endswith("·") else text.rstrip()
            parts = [Text(text, font=DEFAULT_CJK_FONT, font_size=42, color="#e8d9a0")]
            if tex:
                parts.append(MathTex(tex, font_size=52, color="#e8d9a0"))
            g = VGroup(*parts).arrange(RIGHT, buff=0.2).to_edge(DOWN, buff=0.55)
            g.set_z_index(50)
            if live:
                self.add_fixed_in_frame_mobjects(
                    g
                )  # 注册即入场,调用方须 self.remove 摘下
            return g

        def swap_caption(text: str, tex: Optional[str] = None) -> Any:
            """换字幕不用 Transform:旧行整行淡出,新行整行淡入。"""
            nonlocal cur_cap
            new_cap = make_cap(text, tex)
            self.remove(new_cap)  # 摘下防提前露字,由 FadeIn 加回
            if cur_cap is not None:
                self.play(FadeOut(cur_cap), run_time=0.44 * swap_t)
            self.play(FadeIn(new_cap), run_time=0.56 * swap_t)
            cur_cap = new_cap

        # ---------- 几何 ----------
        axes_obj = self._make_axes(cfg, ax_z_lo, ax_z_hi)
        surface = self._make_surface(cfg, axes_obj, f_n, ramp, zmin_n)

        flat = None
        if self.uses_flat:
            d0, d1 = cfg.domain
            flat = Surface(
                lambda u, v: axes_obj.c2p(u, v, 0.001),
                u_range=(d0, d1),
                v_range=(d0, d1),
                resolution=cfg.resolution,
                fill_opacity=0.95,
                stroke_color="#8899bb",
                stroke_width=0.35,
                stroke_opacity=0.25,
            )
            flat.set_fill_by_value(
                axes=axes_obj,
                colorscale=[("#14304f", zmin_n), ("#27507d", cfg.height)],
                axis=2,
            )

        rings_grp, rings_follow = (VGroup(), False)
        if "rings" in t:
            rings_grp, rings_follow = self._contours(cfg, axes_obj, f_n, ramp, zmin_n)

        feat = self._feature(cfg, f_n) if "annotate" in t else None

        # ---------- 角落公式 ----------
        formula = None
        if func_tex:
            formula = MathTex(func_tex, font_size=112)
            formula.set_color_by_gradient(BLUE, TEAL, GREEN, YELLOW, ORANGE, RED)
            self.add_fixed_in_frame_mobjects(formula)

        # ================= title =================
        if cap_map.get("title"):
            cur_cap = make_cap(cap_map["title"], tex=func_tex)  # 片头字幕直接在场
        if "title" in t:
            fade = max(0.8, 0.53 * t["title"])
            if formula is not None:
                self.play(FadeIn(formula, shift=UP * 0.5), run_time=fade)
            self.wait(t["title"] - fade)

        # ================= axes =================
        if "axes" in t:
            if cap_map.get("axes"):
                swap_caption(cap_map["axes"])
            anims = []
            if formula is not None:
                anims.append(formula.animate.scale(0.55).to_corner(UR, buff=0.45))
            anims.append(Create(axes_obj))
            self.play(*anims, run_time=t["axes"])

        # ================= 成型(图曲面:平面隆起 / 闭曲面:充气) =================
        if "flat" in t and flat is not None:
            if cap_map.get("flat"):
                swap_caption(cap_map["flat"])
            self.play(Create(flat), run_time=t["flat"])
        if "rise" in t:
            if flat is not None:
                self.play(
                    Transform(flat, surface), run_time=t["rise"], rate_func=smooth
                )
                surface = flat  # Transform 后它已是目标形状
            else:
                self.play(GrowFromCenter(surface), run_time=t["rise"])  # 闭曲面充气成型

        # ================= rings =================
        if "rings" in t and len(rings_grp) > 0:
            if cap_map.get("rings"):
                swap_caption(cap_map["rings"])
            self.play(
                LaggedStart(*[Create(r) for r in rings_grp], lag_ratio=0.12),
                run_time=t["rings"],
            )

        # ================= orbit =================
        if "orbit" in t:
            if cap_map.get("orbit"):
                swap_caption(cap_map["orbit"])
            settle = 0.4 if t["orbit"] >= 2.0 else 0.0
            spin = t["orbit"] - settle
            self.begin_ambient_camera_rotation(rate=TAU / spin)  # 恰好转满一整圈
            self.wait(spin)
            self.stop_ambient_camera_rotation()
            if settle:
                self.wait(settle)

        # ================= flip =================
        if "flip" in t:
            if cap_map.get("flip"):
                swap_caption(cap_map["flip"])
            about = surface.get_center()
            rot_anims = [Rotate(surface, PI, axis=RIGHT, about_point=about)]
            if rings_follow and len(rings_grp) > 0:
                rot_anims.append(Rotate(rings_grp, PI, axis=RIGHT, about_point=about))
            self.move_camera(
                phi=80 * DEGREES,
                theta=25 * DEGREES,
                zoom=0.88,
                run_time=0.2 * t["flip"],
            )
            self.play(*rot_anims, run_time=0.32 * t["flip"])
            self.wait(0.16 * t["flip"])
            rot_back = [Rotate(surface, -PI, axis=RIGHT, about_point=about)]
            if rings_follow and len(rings_grp) > 0:
                rot_back.append(Rotate(rings_grp, -PI, axis=RIGHT, about_point=about))
            self.play(*rot_back, run_time=0.32 * t["flip"])

        # ================= annotate =================
        dot = stem = tag = None
        if "annotate" in t and feat is not None:
            px, py, pz, tag_tex, use_hud, stem_z0 = feat
            phi_a, theta_a, zoom_a = self._annotate_camera()
            self.move_camera(
                phi=phi_a * DEGREES,
                theta=theta_a * DEGREES,
                zoom=zoom_a,
                run_time=0.33 * t["annotate"],
            )
            dot = Dot3D(radius=0.09, color=RED, resolution=(16, 16)).move_to(
                axes_obj.c2p(px, py, pz)
            )
            stem = None
            if stem_z0 is not None and abs(stem_z0 - pz) > 1e-9:
                # stem_z0==pz → 免虚线(腰圆类特征点:竖直虚线会扎进曲面内部被吞)
                stem = DashedLine(
                    axes_obj.c2p(px, py, stem_z0),
                    axes_obj.c2p(px, py, pz),
                    stroke_width=2.5,
                    color=WHITE,
                )
                stem.set_z_index(60)
            if use_hud:
                # 特征点被曲面四壁环绕:相机定格后投影到屏幕坐标,标签固定挂其右上,
                # 永不被曲面按深度盖住(红点/虚线仍留在 3D 锚定)。
                proj = self.camera.project_point(axes_obj.c2p(px, py, pz))
                tag = MathTex(tag_tex, font_size=44, color=WHITE).move_to(
                    proj + RIGHT * 1.05 + UP * 0.4
                )
                self.add_fixed_in_frame_mobjects(tag)
            else:
                tag = MathTex(tag_tex, font_size=44, color=WHITE).next_to(
                    dot, RIGHT, buff=0.28
                )
            ann_anims = [FadeIn(dot, scale=0.3)]
            if stem is not None:
                ann_anims.append(Create(stem))
            ann_anims.append(Write(tag))
            self.play(*ann_anims, run_time=0.37 * t["annotate"])
            self.wait(0.30 * t["annotate"])

        # ================= outro =================
        f1, capin, hold, f2 = (
            0.32 * t["outro"],
            0.13 * t["outro"],
            0.35 * t["outro"],
            0.20 * t["outro"],
        )
        anims = [
            FadeOut(m)
            for m in (axes_obj, surface, rings_grp, stem, dot, tag)
            if m is not None
        ]
        if cur_cap is not None:
            anims.append(FadeOut(cur_cap))
        if formula is not None:
            anims.append(formula.animate.move_to(ORIGIN).scale(1.5))
        self.play(*anims, run_time=f1)
        # 大扫除:强制清掉漏网对象
        self.remove(*[m for m in list(self.mobjects) if m is not formula])
        if cap_map.get("outro") and len(list(cfg.captions)) >= 2:
            last_cap = make_cap(cap_map["outro"])
            self.remove(last_cap)
            self.play(FadeIn(last_cap), run_time=capin)
            self.wait(hold)
            end_anims = [FadeOut(last_cap)]
            if formula is not None:
                end_anims.append(FadeOut(formula))
            self.play(*end_anims, run_time=f2)
        else:
            self.wait(hold + f2)
            if formula is not None:
                self.play(FadeOut(formula), run_time=f2)


# ---------------- 三个曲面场景 ----------------
class GaussianSurfaceScene(_GraphSurfaceScene):
    """GaussianSurfaceScene."""

    def _geometry(self, cfg: Any) -> Any:
        """_geometry."""
        f_raw, tex = cfg.resolve()
        n = 160
        gx = np.linspace(cfg.domain[0], cfg.domain[1], n)
        zs = np.array([[f_raw(x, y) for x in gx] for y in gx])
        zmax = max(float(zs.max()), 1e-9)
        zmin = min(0.0, float(zs.min()))
        scale = cfg.height / zmax
        self._gx, self._zs = gx, zs  # 供峰顶标注
        self._stem_z0 = zmin * scale
        f = lambda x, y: f_raw(x, y) * scale
        return f, tex, zmin * scale, min(0.0, zmin * scale), cfg.height * 1.5

    def _contours(self, cfg: Any, axes: Any, f: Any, ramp: Any, zmin_n: Any) -> Any:
        """_contours."""
        g = VGroup()
        for c in [0.8, 0.55, 0.33, 0.15, 0.045]:
            r = _radius_for_level(f, cfg.domain[1], c)
            if r is None:
                continue
            g.add(
                ParametricFunction(
                    lambda tt, r=r: axes.c2p(r * np.cos(tt), r * np.sin(tt), 0.002),
                    t_range=[0, TAU],
                    color=_ramp_color(ramp, c),
                    stroke_width=2.0,
                    stroke_opacity=0.65,
                )
            )
        return g, False  # 地板投影,不随翻面

    def _feature(self, cfg: Any, f: Any) -> Any:
        """_feature."""
        iy, ix = np.unravel_index(int(self._zs.argmax()), self._zs.shape)
        px, py = float(self._gx[ix]), float(self._gx[iy])
        return (
            px,
            py,
            f(px, py),
            rf"({_fmt(px)},\,{_fmt(py)},\,{_fmt(f(px, py))})",
            False,
            self._stem_z0,
        )

    def _caption_slots(self) -> Any:
        """_caption_slots."""
        return ["title", "axes", "flat", "orbit", "flip", "outro"]

    def _annotate_camera(self) -> Any:
        """_annotate_camera."""
        return 68.0, -40.0, 0.95


class SaddleSurfaceScene(_GraphSurfaceScene):
    """SaddleSurfaceScene."""

    def _geometry(self, cfg: Any) -> Any:
        """_geometry."""
        d1 = cfg.domain[1]
        scale = cfg.height / (d1 * d1)
        f = lambda x, y: (x * x - y * y) * scale
        return f, r"z = x^{2} - y^{2}", -cfg.height, -cfg.height * 1.3, cfg.height * 1.3

    def _contours(self, cfg: Any, axes: Any, f: Any, ramp: Any, zmin_n: Any) -> Any:
        """_contours."""
        d1 = cfg.domain[1]
        H = cfg.height
        g = VGroup()
        # 渐近线 x=±y(k=0 的退化等高线,鞍面签名)
        for s in (+1, -1):
            line = ParametricFunction(
                lambda t, s=s: axes.c2p(t, s * t, 0.003),
                t_range=[-d1, d1],
                color="#9fb3c8",
                stroke_width=2.0,
                stroke_opacity=0.55,
            )
            g.add(DashedVMobject(line, num_dashes=24))
        # 双曲线族 x²-y²=k 两支,按水平上色
        for z_lv in [1.0, 0.6, 0.25, -0.25, -0.6, -1.0]:
            k = z_lv * d1 * d1 / H  # 归一化前原始水平
            col = _ramp_color(ramp, (z_lv - zmin_n) / (H - zmin_n))
            if k > 0:  # x = ±√(k+y²)
                ymax = np.sqrt(d1 * d1 - k)
                for s in (+1, -1):
                    g.add(
                        ParametricFunction(
                            lambda t, k=k, s=s: axes.c2p(
                                s * np.sqrt(k + t * t), t, 0.002
                            ),
                            t_range=[-ymax, ymax],
                            color=col,
                            stroke_width=2.4,
                            stroke_opacity=0.75,
                        )
                    )
            elif k < 0:  # y = ±√(|k|+x²)
                xmax = np.sqrt(d1 * d1 + k)
                for s in (+1, -1):
                    g.add(
                        ParametricFunction(
                            lambda t, k=k, s=s: axes.c2p(
                                t, s * np.sqrt(-k + t * t), 0.002
                            ),
                            t_range=[-xmax, xmax],
                            color=col,
                            stroke_width=2.4,
                            stroke_opacity=0.75,
                        )
                    )
        return g, False  # 地板等高线,不随翻面

    def _feature(self, cfg: Any, f: Any) -> Any:
        """_feature."""
        return 0.0, 0.0, 0.0, r"(0,\,0,\,0)", True, -cfg.height * 1.3  # 鞍点:HUD 标签


class ParaboloidSurfaceScene(_GraphSurfaceScene):
    """ParaboloidSurfaceScene."""

    def _geometry(self, cfg: Any) -> Any:
        """_geometry."""
        d1 = cfg.domain[1]
        scale = cfg.height / (d1 * d1)
        f = lambda x, y: (x * x + y * y) * scale
        return f, r"z = x^{2} + y^{2}", 0.0, -cfg.height * 0.6, cfg.height * 1.3

    def _contours(self, cfg: Any, axes: Any, f: Any, ramp: Any, zmin_n: Any) -> Any:
        """_contours."""
        d1 = cfg.domain[1]
        H = cfg.height
        g = VGroup()
        # 贴面同心圆(海拔环线):碗沿高,地板投影会被近侧碗壁挡住。
        # 水平 z_lv 的圆半径 r = D·√(z_lv/H),抬高 0.004 防 z-fighting。
        for z_lv in [1.0, 0.7, 0.45, 0.25]:
            r = d1 * np.sqrt(z_lv / H)
            g.add(
                ParametricFunction(
                    lambda t, r=r, z_lv=z_lv: axes.c2p(
                        r * np.cos(t), r * np.sin(t), z_lv + 0.004
                    ),
                    t_range=[0, TAU],
                    color=_ramp_color(ramp, z_lv / H),
                    stroke_width=2.6,
                    stroke_opacity=0.85,
                )
            )
        return g, True  # 贴在曲面上,翻面必须跟着转

    def _feature(self, cfg: Any, f: Any) -> Any:
        """_feature."""
        return 0.0, 0.0, 0.0, r"(0,\,0,\,0)", True, -cfg.height * 0.6  # 顶点:HUD 标签


class EllipsoidSurfaceScene(_GraphSurfaceScene):
    """椭球面:闭曲面。uses_flat=False → 充气成型;坐标轴三轴等比缩放防畸变。"""

    uses_flat = False

    def _geometry(self, cfg: Any) -> Any:
        """_geometry."""
        a, b, c = cfg.semi_axes
        f = lambda x, y: 0.0  # 闭曲面不经图构造,占位
        tex = (
            rf"\frac{{x^{{2}}}}{{{_fmt(a)}^{{2}}}} + "
            rf"\frac{{y^{{2}}}}{{{_fmt(b)}^{{2}}}} + "
            rf"\frac{{z^{{2}}}}{{{_fmt(c)}^{{2}}}} = 1"
        )
        return f, tex, -c, -c - 0.5, c + 0.9

    def _make_axes(self, cfg: Any, ax_z_lo: Any, ax_z_hi: Any) -> Any:
        """三轴等比缩放:x 轴定标,y/z 同比例,否则闭曲面会 visibly 畸变。"""
        a, b, c = cfg.semi_axes
        k = 7.2 / (2 * (a + 0.4))
        axes = ThreeDAxes(
            x_range=[-a - 0.4, a + 0.4, 1],
            y_range=[-b - 0.4, b + 0.4, 1],
            z_range=[ax_z_lo, ax_z_hi, c / 2],
            x_length=7.2,
            y_length=2 * (b + 0.4) * k,
            z_length=(ax_z_hi - ax_z_lo) * k,
        )
        return axes.set_stroke(opacity=0.55)

    def _make_surface(self, cfg: Any, axes: Any, f: Any, ramp: Any, zmin_n: Any) -> Any:
        """_make_surface."""
        a, b, c = cfg.semi_axes
        s = Surface(
            lambda u, v: axes.c2p(
                a * np.sin(u) * np.cos(v), b * np.sin(u) * np.sin(v), c * np.cos(u)
            ),
            u_range=(0, PI),
            v_range=(0, TAU),
            resolution=cfg.resolution,
            fill_opacity=1.0,
            stroke_color=WHITE,
            stroke_width=0.35,
            stroke_opacity=0.16,
        )
        s.set_fill_by_value(
            axes=axes, colorscale=[(col, -c + p * 2 * c) for col, p in ramp], axis=2
        )
        return s

    def _contours(self, cfg: Any, axes: Any, f: Any, ramp: Any, zmin_n: Any) -> Any:
        """_contours."""
        a, b, c = cfg.semi_axes
        g = VGroup()
        for h in [0.66, 0.33, 0.0, -0.33, -0.66]:  # z/c 高度比例
            z0 = c * h
            s = np.sqrt(max(1.0 - h * h, 0.0)) * 1.005  # 微胀防 z-fighting
            g.add(
                ParametricFunction(
                    lambda t, s=s, z0=z0: axes.c2p(
                        a * s * np.cos(t), b * s * np.sin(t), z0
                    ),
                    t_range=[0, TAU],
                    color=_ramp_color(ramp, (z0 + c) / (2 * c)),
                    stroke_width=2.6,
                    stroke_opacity=0.85,
                )
            )
        return g, True  # 贴面环,翻面随转

    def _feature(self, cfg: Any, f: Any) -> Any:
        """_feature."""
        a, b, c = cfg.semi_axes
        # 上顶点外露,3D 标签即可;虚线从上方垂下(顶点以下在曲面内部,会被遮挡)
        return 0.0, 0.0, c, rf"(0,\,0,\,{_fmt(c)})", False, c + 0.75


class TorusSurfaceScene(_GraphSurfaceScene):
    """圆环面:闭曲面。充气成型;坐标轴三轴等比缩放;按管截面高度上彩虹色。"""

    uses_flat = False

    def _geometry(self, cfg: Any) -> Any:
        """_geometry."""
        R, r = cfg.major_radius, cfg.minor_radius
        f = lambda x, y: 0.0  # 闭曲面不经图构造,占位
        tex = rf"(\sqrt{{x^{{2}}+y^{{2}}}} - {_fmt(R)})^{{2}} + z^{{2}} = {_fmt(r * r)}"
        return f, tex, -r, -r - 0.4, r + 0.9

    def _make_axes(self, cfg: Any, ax_z_lo: Any, ax_z_hi: Any) -> Any:
        """_make_axes."""
        R, r = cfg.major_radius, cfg.minor_radius
        outer = R + r
        k = 7.2 / (2 * (outer + 0.4))  # x 定标,y/z 同比例防畸变
        axes = ThreeDAxes(
            x_range=[-outer - 0.4, outer + 0.4, 1],
            y_range=[-outer - 0.4, outer + 0.4, 1],
            z_range=[ax_z_lo, ax_z_hi, r / 2],
            x_length=7.2,
            y_length=7.2,
            z_length=(ax_z_hi - ax_z_lo) * k,
        )
        return axes.set_stroke(opacity=0.55)

    def _make_surface(self, cfg: Any, axes: Any, f: Any, ramp: Any, zmin_n: Any) -> Any:
        """_make_surface."""
        R, r = cfg.major_radius, cfg.minor_radius
        s = Surface(
            lambda u, v: axes.c2p(
                (R + r * np.cos(v)) * np.cos(u),
                (R + r * np.cos(v)) * np.sin(u),
                r * np.sin(v),
            ),
            u_range=(0, TAU),
            v_range=(0, TAU),
            resolution=cfg.resolution,
            fill_opacity=1.0,
            stroke_color=WHITE,
            stroke_width=0.35,
            stroke_opacity=0.16,
        )
        s.set_fill_by_value(
            axes=axes, colorscale=[(col, -r + p * 2 * r) for col, p in ramp], axis=2
        )
        return s

    def _contours(self, cfg: Any, axes: Any, f: Any, ramp: Any, zmin_n: Any) -> Any:
        """_contours."""
        R, r = cfg.major_radius, cfg.minor_radius
        g = VGroup()
        for z_lv in [0.6, 0.0, -0.6]:  # 管截面高度比例(×r)
            z0 = r * z_lv
            half = np.sqrt(max(r * r - z0 * z0, 0.0))
            for sgn in (+1, -1):  # 水平截面切出外/内两支圆
                rho = (R + sgn * half) * 1.004  # 微胀防 z-fighting
                g.add(
                    ParametricFunction(
                        lambda t, rho=rho, z0=z0: axes.c2p(
                            rho * np.cos(t), rho * np.sin(t), z0
                        ),
                        t_range=[0, TAU],
                        color=_ramp_color(ramp, (z0 + r) / (2 * r)),
                        stroke_width=2.6,
                        stroke_opacity=0.85,
                    )
                )
        return g, True  # 贴面环,翻面随转

    def _feature(self, cfg: Any, f: Any) -> Any:
        """_feature."""
        R, r = cfg.major_radius, cfg.minor_radius
        # 最高点外露,3D 标签;天线虚线自上垂下(其余方向在曲面/孔洞里)
        return 0.0, 0.0, r, rf"(0,\,0,\,{_fmt(r)})", False, r + 0.75


class HyperboloidOneSheetScene(_GraphSurfaceScene):
    """单叶双曲面:闭式管面。充气成型;坐标轴三轴等比缩放;按高度对称铺彩虹。"""

    uses_flat = False

    def _geometry(self, cfg: Any) -> Any:
        """_geometry."""
        a, h = cfg.waist_radius, cfg.z_extent
        f = lambda x, y: 0.0  # 闭式管面不经图构造,占位
        rhs = "1" if abs(a * a - 1.0) < 1e-9 else _fmt(a * a)
        tex = rf"x^{{2}} + y^{{2}} - z^{{2}} = {rhs}"
        return f, tex, -h, -h - 0.4, h + 0.4

    def _make_axes(self, cfg: Any, ax_z_lo: Any, ax_z_hi: Any) -> Any:
        """_make_axes."""
        a, h = cfg.waist_radius, cfg.z_extent
        max_r = (a * a + h * h) ** 0.5  # 端口半径
        k = 7.2 / (2 * (max_r + 0.4))  # x 定标,y/z 同比例防畸变
        axes = ThreeDAxes(
            x_range=[-max_r - 0.4, max_r + 0.4, 1],
            y_range=[-max_r - 0.4, max_r + 0.4, 1],
            z_range=[ax_z_lo, ax_z_hi, h / 2],
            x_length=7.2,
            y_length=7.2,
            z_length=(ax_z_hi - ax_z_lo) * k,
        )
        return axes.set_stroke(opacity=0.55)

    def _make_surface(self, cfg: Any, axes: Any, f: Any, ramp: Any, zmin_n: Any) -> Any:
        """_make_surface."""
        a, h = cfg.waist_radius, cfg.z_extent
        s = Surface(
            lambda u, v: axes.c2p(
                (a * a + u * u) ** 0.5 * np.cos(v),
                (a * a + u * u) ** 0.5 * np.sin(v),
                u,
            ),  # u 即 z
            u_range=(-h, h),
            v_range=(0, TAU),
            resolution=cfg.resolution,
            fill_opacity=1.0,
            stroke_color=WHITE,
            stroke_width=0.35,
            stroke_opacity=0.16,
        )
        s.set_fill_by_value(
            axes=axes, colorscale=[(col, -h + p * 2 * h) for col, p in ramp], axis=2
        )
        return s

    def _contours(self, cfg: Any, axes: Any, f: Any, ramp: Any, zmin_n: Any) -> Any:
        """_contours."""
        a, h = cfg.waist_radius, cfg.z_extent
        g = VGroup()
        for z_lv in [1.0, 0.5, 0.0, -0.5, -1.0]:  # 水平圆族(0 = 腰圆)
            if abs(z_lv) > h * 0.95:
                continue
            rho = ((a * a + z_lv * z_lv) ** 0.5) * 1.004  # 微胀防 z-fighting
            g.add(
                ParametricFunction(
                    lambda t, rho=rho, z_lv=z_lv: axes.c2p(
                        rho * np.cos(t), rho * np.sin(t), z_lv
                    ),
                    t_range=[0, TAU],
                    color=_ramp_color(ramp, (z_lv + h) / (2 * h)),
                    stroke_width=2.6,
                    stroke_opacity=0.85,
                )
            )
        return g, True  # 贴面环,翻面随转

    def _feature(self, cfg: Any, f: Any) -> Any:
        """_feature."""
        a, h = cfg.waist_radius, cfg.z_extent
        # 腰圆前点(a,0,0):竖直虚线两端都扎进曲面,免虚线,点+HUD 标签
        return a, 0.0, 0.0, rf"({_fmt(a)},\,0,\,0)", True, 0.0


_name_seq: dict = {}


def _scene_name(base: str) -> str:
    """_scene_name."""
    n = _name_seq.get(base, 0) + 1
    _name_seq[base] = n
    return base if n == 1 else f"{base}{n}"


def _make_factory(cfg_cls: Any, scene_cls: Any, base_name: Any) -> Any:
    """_make_factory."""

    def factory(name: Optional[str] = None, **kw) -> Any:
        """factory."""
        cfg = cfg_cls(**kw)
        return type(name or _scene_name(base_name), (scene_cls,), {"style": cfg})

    factory.__doc__ = f"工厂:返回配置好的 {base_name} Scene 类。"
    return factory


gaussian_surface_scene = _make_factory(
    GaussianSurface, GaussianSurfaceScene, "GaussianSurface"
)
saddle_surface_scene = _make_factory(SaddleSurface, SaddleSurfaceScene, "SaddleSurface")
paraboloid_surface_scene = _make_factory(
    ParaboloidSurface, ParaboloidSurfaceScene, "ParaboloidSurface"
)
ellipsoid_surface_scene = _make_factory(
    EllipsoidSurface, EllipsoidSurfaceScene, "EllipsoidSurface"
)
torus_surface_scene = _make_factory(TorusSurface, TorusSurfaceScene, "TorusSurface")
hyperboloid_one_sheet_scene = _make_factory(
    HyperboloidOneSheet, HyperboloidOneSheetScene, "HyperboloidOneSheet"
)

# SPDX-FileCopyrightText: 2026 FTZ-OPUS
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-
""":class:`~manim_extensions.radar.poly.PolyRadarChart` —— 正十二面体立体雷达图（12 轴标满，面板模式）。

12 个数据轴 = 十二面体 12 块五边形面板的中心方向。
满量程 = 数据球顶到自己面板的中心；越界 = 球刺穿面板鼓出外壳。
数据点连成"内芯二十面体"（十二面体的对偶），随数据实时变形。

用法（ThreeDScene 内）::

    from manim_extensions.radar import PolyRadarChart, PolyMorph

    poly = PolyRadarChart(stats_names, values, spin_rate=7)   # 慢速自旋
    self.add(poly)
    poly.grow_in(self)                       # 骨架由内向外生长（可跳过：
                                             #   grow=False 直接出现）
    self.play(PolyMorph(poly, new_values))   # 立体变形（球滑动+棱面跟随）
    poly.spin_to(axis_index)                 # 把某轴转到正对镜头

架构要点：多面体不持有相机对象（渲染缓存会 pickle 整个对象家族）；
环绕运动 = 内容绕自身竖轴自旋（theta 为普通浮点属性）；标签用
look-at billboard（世界 up 投影），任意自转角度下水平可读。
"""

import math

import numpy as np
from manim import *
from manim.mobject.three_d.three_dimensions import Dot3D
from manim.utils.space_ops import rotation_matrix

# ============================================================================
# 十二面体常数表（暴力推导 + 自校验，杜绝手写错误）
# ============================================================================
PHI = (1.0 + math.sqrt(5.0)) / 2.0

_DODECA_RAW = [
    (-1.0, -1.0, -1.0),
    (+1.0, -1.0, -1.0),
    (-1.0, +1.0, -1.0),
    (+1.0, +1.0, -1.0),
    (-1.0, -1.0, +1.0),
    (+1.0, -1.0, +1.0),
    (-1.0, +1.0, +1.0),
    (+1.0, +1.0, +1.0),
    (0.0, -1.0 / PHI, -PHI),
    (0.0, -1.0 / PHI, +PHI),
    (0.0, +1.0 / PHI, -PHI),
    (0.0, +1.0 / PHI, +PHI),
    (-1.0 / PHI, -PHI, 0.0),
    (-1.0 / PHI, +PHI, 0.0),
    (+1.0 / PHI, -PHI, 0.0),
    (+1.0 / PHI, +PHI, 0.0),
    (-PHI, 0.0, -1.0 / PHI),
    (-PHI, 0.0, +1.0 / PHI),
    (+PHI, 0.0, -1.0 / PHI),
    (+PHI, 0.0, +1.0 / PHI),
]


def _unit(v):
    v = np.asarray(v, dtype=float)
    return v / np.linalg.norm(v)


DODECA_VERTICES = [_unit(v) for v in _DODECA_RAW]

from itertools import combinations

_pair_d = {
    (i, j): float(np.linalg.norm(DODECA_VERTICES[i] - DODECA_VERTICES[j]))
    for i, j in combinations(range(20), 2)
}
EDGE_LEN = min(_pair_d.values())
DODECA_EDGES = [e for e, d in _pair_d.items() if d < EDGE_LEN * 1.5]

_EDGE_SET = {frozenset(e) for e in DODECA_EDGES}
DODECA_FACES = []
for combo in combinations(range(20), 5):
    pts = [DODECA_VERTICES[i] for i in combo]
    mean = np.mean(pts, axis=0)
    n = _unit(mean)
    dots = [float(np.dot(p, n)) for p in pts]
    if max(dots) - min(dots) > 1e-6:
        continue
    deg = [0, 0, 0, 0, 0]
    for a, b in combinations(combo, 2):
        if frozenset((a, b)) in _EDGE_SET:
            deg[combo.index(a)] += 1
            deg[combo.index(b)] += 1
    if deg == [2, 2, 2, 2, 2]:
        DODECA_FACES.append(list(combo))

FACE_NORMAL_DIRS = []
for face in DODECA_FACES:
    mean = np.mean([DODECA_VERTICES[i] for i in face], axis=0)
    FACE_NORMAL_DIRS.append(_unit(mean))
INRADIUS = float(np.dot(DODECA_VERTICES[DODECA_FACES[0][0]], FACE_NORMAL_DIRS[0]))

FACE_ADJ = []
for a in range(len(DODECA_FACES)):
    for b in range(a + 1, len(DODECA_FACES)):
        shared = sum(
            1
            for e in DODECA_EDGES
            if e[0] in DODECA_FACES[a]
            and e[0] in DODECA_FACES[b]
            and e[1] in DODECA_FACES[a]
            and e[1] in DODECA_FACES[b]
        )
        if shared == 1:
            FACE_ADJ.append((a, b))

assert len(DODECA_VERTICES) == 20
assert len(DODECA_EDGES) == 30, f"棱数 {len(DODECA_EDGES)} != 30"
assert len(DODECA_FACES) == 12, f"面数 {len(DODECA_FACES)} != 12"
assert all(len(f) == 5 for f in DODECA_FACES)
_cnt = np.zeros(20, dtype=int)
for f in DODECA_FACES:
    for i in f:
        _cnt[i] += 1
assert (_cnt == 3).all()
assert len(FACE_ADJ) == 30, f"对偶棱数 {len(FACE_ADJ)} != 30"
assert 0.5 < INRADIUS < 0.95, f"内切比异常 {INRADIUS:.3f}"

# ============================================================================
# PolyRadarChart
# ============================================================================
SKIN_EDGE_W = 2.0
SKIN_EDGE_C = "#5B7A9E"
SKIN_FACE_OP = 0.08
DYE_C = "#00F5FF"
EDGE_C = "#00E5CC"
OVERFLOW_C = "#FF5A3C"
LABEL_C = "#EAF2FF"


class PolyRadarChart(VGroup):
    """正十二面体立体雷达（12 轴标满，面板模式）。

    参数
    ----
    spin_rate:
        自转速度（度/秒）。默认 7（缓慢环绕）；炫酷特效可临时调高，
        但快速旋转易视觉疲劳，不建议长开。
    grow:
        True（默认）= 骨架从隐藏状态开始，用 :meth:`~manim_extensions.radar.poly.PolyRadarChart.grow_in` 逐层生长；
        False = 构造时骨架直接完整出现（跳过生长动画）。

    其余：radius 外接半径、skins 嵌套壳比例、max_value 满量程。
    """

    def __init__(
        self,
        axes_names,
        values,
        *,
        max_value=10.0,
        radius=2.6,
        skins=(0.4, 0.7, 1.0),
        spin_rate=7.0,
        grow=True,
        cam_pos=(0.0, 0.0, 20.0),
        center=(0.0, -0.15, 0.0),
        sphere_color=DYE_C,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.axes_names = list(axes_names)
        if len(self.axes_names) != 12:
            raise ValueError(
                f"PolyRadarChart 需要 12 个轴，收到 {len(self.axes_names)}"
            )
        self.max_value = float(max_value)
        self.poly_radius = float(radius)
        self.inr = INRADIUS * self.poly_radius  # 满量程时面板中心的世界半径
        self.center = np.array(center, dtype=float)  # 自转轴（世界坐标）
        self.cam_pos = np.array(cam_pos, dtype=float)
        self.theta = 0.0  # 自转角（普通浮点）
        self.spin_rate = float(spin_rate)  # 度/秒（默认慢速）
        self.grow = bool(grow)
        self._frac = np.array(values, dtype=float) / self.max_value
        if len(self._frac) != 12:
            raise ValueError(f"需要 12 个数值，收到 {len(self._frac)}")

        # ---- 骨架：嵌套十二面体壳 ----
        self.skins = VGroup()
        self.skin_parts = {}
        for s in skins:
            edges = VGroup()
            for i, j in DODECA_EDGES:
                p0 = self.center + np.array(DODECA_VERTICES[i]) * s * self.poly_radius
                p1 = self.center + np.array(DODECA_VERTICES[j]) * s * self.poly_radius
                edges.add(
                    Line(
                        p0,
                        p1,
                        stroke_width=SKIN_EDGE_W * (1.15 if s == 1.0 else 1.0),
                        color=SKIN_EDGE_C,
                        stroke_opacity=(0.7 if s == 1.0 else 0.42),
                    )
                )
            g = VGroup(edges)
            part = {"edges": edges, "dots": None, "faces": None}
            if s == max(skins):
                dots = VGroup(
                    *[
                        Dot3D(
                            point=self.center + np.array(v) * s * self.poly_radius,
                            radius=0.045,
                            color="#9FC4E8",
                            resolution=(8, 8),
                        )
                        for v in DODECA_VERTICES
                    ]
                )
                faces = VGroup(
                    *[
                        Polygon(
                            *[
                                self.center
                                + np.array(DODECA_VERTICES[i]) * s * self.poly_radius
                                for i in face
                            ],
                            stroke_width=0,
                            fill_color="#7FA8C9",
                            fill_opacity=SKIN_FACE_OP,
                        )
                        for face in DODECA_FACES
                    ]
                )
                g.add(faces, dots)
                part["dots"], part["faces"] = dots, faces
            self.skin_parts[s] = part
            self.skins.add(g)
        if grow:
            self.skins.set_opacity(0.0)  # grow_in 时逐层显现
        self.add(self.skins)

        # ---- 数据层：球 / 棱 / 三角面 / 标签 ----
        self.spheres = VGroup()
        for i in range(12):
            self.spheres.add(
                Dot3D(radius=0.13, color=sphere_color, resolution=(12, 12))
            )
        self.data_edges = VGroup()
        for a, b in FACE_ADJ:
            self.data_edges.add(
                Line(
                    ORIGIN, ORIGIN, stroke_width=6.0, color=EDGE_C, stroke_opacity=0.20
                )
            )
            self.data_edges.add(
                Line(ORIGIN, ORIGIN, stroke_width=2.6, color=EDGE_C, stroke_opacity=0.9)
            )
        self.data_faces = VGroup()
        for tri in self._data_triangles():
            self.data_faces.add(
                Polygon(
                    ORIGIN,
                    ORIGIN,
                    ORIGIN,
                    stroke_width=0,
                    fill_color=DYE_C,
                    fill_opacity=0.13,
                )
            )
        self.labels = VGroup()
        for name in self.axes_names:
            self.labels.add(Text(name, font_size=21, color=LABEL_C, weight="BOLD"))

        self.data_group = VGroup(
            self.data_faces, self.data_edges, self.spheres, self.labels
        )
        self.add(self.data_group)

        self._rebuild()
        self._attach_billboards()
        self.add_updater(self._tick)

    # ------------------------------------------------------------------
    def _data_triangles(self):
        """内芯二十面体的 20 个三角面 = 每个十二面体顶点周围的 3 个面法向。"""
        tris = []
        for v in range(20):
            fs = [fi for fi, face in enumerate(DODECA_FACES) if v in face]
            tris.append(tuple(fs))
        return tris

    def _world(self, i: int, extra: float = 0.0) -> np.ndarray:
        """轴 i 的数据球世界坐标（含自转）。"""
        local = np.array(FACE_NORMAL_DIRS[i]) * (
            self.inr * float(self._frac[i]) + extra
        )
        th = math.radians(self.theta)
        Rz = np.array(
            [
                [math.cos(th), -math.sin(th), 0.0],
                [math.sin(th), math.cos(th), 0.0],
                [0.0, 0.0, 1.0],
            ]
        )
        return self.center + Rz @ local

    def _rebuild(self) -> None:
        pos = [self._world(i) for i in range(12)]
        for i in range(12):
            self.spheres[i].move_to(pos[i])
            self.spheres[i].set_color(OVERFLOW_C if self._frac[i] > 1.0 else DYE_C)
        for k, (a, b) in enumerate(FACE_ADJ):
            self.data_edges[2 * k].put_start_and_end_on(pos[a], pos[b])
            self.data_edges[2 * k + 1].put_start_and_end_on(pos[a], pos[b])
        for k, tri in enumerate(self._data_triangles()):
            pts = [pos[t] for t in tri]
            self.data_faces[k].set_points_as_corners([*pts, pts[0]])
        for i in range(12):
            self.labels[i].set_color(OVERFLOW_C if self._frac[i] > 1.0 else LABEL_C)

    def _tick(self, m: VGroup, dt: float) -> None:
        """自旋 + 标签 billboard（绑定方法，可序列化）。"""
        if self.spin_rate:
            delta = self.spin_rate * dt
            self.rotate(delta, axis=Z_AXIS, about_point=self.center)
            self.theta = (self.theta + delta) % 360.0
        # 标签朝向由 _billboard（become+look-at）负责，见 _attach_billboards

    def _attach_billboards(self) -> None:
        """标签 look-at billboard：抵消自转（Rz(-θ)）+ 面向固定相机（Ry(φ)）。

        become 重置标签的点的世界坐标（不继承父级烘焙的旋转），
        因此朝向 = Ry(φ)（面向固定相机），位置跟随自转与数据球。
        """
        self._label_base = [lab.copy().move_to(ORIGIN) for lab in self.labels]
        Rbill = rotation_matrix(75 * DEGREES, Y_AXIS)[:3, :3]

        def upd(m: VGroup, dt: float = 0.0) -> None:
            th = math.radians(self.theta)
            M = rotation_matrix(-th, Z_AXIS)[:3, :3] @ Rbill
            for k, lab in enumerate(m):
                anchor = self.center + rotation_matrix(th, Z_AXIS)[:3, :3] @ (
                    np.array(FACE_NORMAL_DIRS[k])
                    * (self.inr * float(self._frac[k]) + 0.55)
                )
                lab.become(self._label_base[k].copy().apply_matrix(M).move_to(anchor))

        self.labels.add_updater(upd)

    # ------------------------------------------------------------------
    def grow_in(self, scene, run_time: float = 0.45) -> "PolyRadarChart":
        """骨架由内向外逐层生长（grow=True 时用；grow=False 无效）。"""
        if not self.grow:
            return self
        for s in sorted(self.skin_parts):
            part = self.skin_parts[s]
            part["edges"].set_stroke(
                opacity=(0.7 if s == max(self.skin_parts) else 0.42)
            )
            anims = [Create(part["edges"])]
            if part["faces"] is not None:
                anims.append(FadeIn(part["faces"]))
            if part["dots"] is not None:
                anims.append(FadeIn(part["dots"]))
            scene.play(*anims, run_time=run_time)
        return self

    def spin_to(self, axis_index: int, run_time: float = 1.2):
        """转动自转角，把轴 axis_index 的面板转到正对镜头（theta=0）。"""

        class _Spin(Animation):
            def __init__(self, poly, delta, **kw):
                self.poly = poly
                self.delta = delta
                super().__init__(poly, **kw)

            def begin(self) -> None:
                self.t0 = self.poly.theta

            def interpolate_mobject(self, alpha: float) -> None:
                new = self.t0 + self.delta * alpha
                self.poly.rotate(
                    new - self.poly.theta, axis=Z_AXIS, about_point=self.poly.center
                )
                self.poly.theta = new

            def finish(self) -> None:
                self.poly.rotate(
                    self.t0 + self.delta - self.poly.theta,
                    axis=Z_AXIS,
                    about_point=self.poly.center,
                )
                self.poly.theta = (self.t0 + self.delta) % 360.0

        az = math.atan2(
            FACE_NORMAL_DIRS[axis_index][1], FACE_NORMAL_DIRS[axis_index][0]
        )
        delta = -math.radians(self.theta) - az
        delta = (delta + math.pi) % (2 * math.pi) - math.pi
        return _Spin(self, delta, run_time=run_time)

    def set_values(self, values) -> None:
        self._frac = np.array(values, dtype=float) / self.max_value
        self._rebuild()


class PolyMorph(Animation):
    """立体变形：数据球沿各自面板方向滑动，棱面实时跟随。"""

    def __init__(self, poly: PolyRadarChart, target_values, **kwargs) -> None:
        self.poly = poly
        self.target = np.array(target_values, dtype=float) / poly.max_value
        super().__init__(poly, **kwargs)

    def begin(self) -> None:
        self.start = self.poly._frac.copy()

    def interpolate_mobject(self, alpha: float) -> None:
        self.poly._frac = self.start + (self.target - self.start) * alpha

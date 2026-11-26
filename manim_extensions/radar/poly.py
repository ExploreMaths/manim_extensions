# SPDX-FileCopyrightText: 2026 FTZ-OPUS
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Utilities for the poly module."""

from __future__ import annotations
from collections.abc import Sequence
from typing import Any, cast

# -*- coding: utf-8 -*-


""":class:`~manim_extensions.radar.poly.PolyRadarChart` — a dodecahedral radar.

The twelve data axes point along the centres of the twelve pentagonal faces.
At full scale the value sphere sits exactly on its panel centre; an overflowing
value pushes the sphere through the panel and out of the shell. The data
spheres are joined into an inner icosahedron, the dual of the dodecahedron,
which deforms with the values.

Typical use inside a :class:`~manim.scene.three_d_scene.ThreeDScene`::

    from manim_extensions.radar import PolyRadarChart, PolyMorph

    poly = PolyRadarChart(stats_names, values, spin_rate=7)
    self.add(poly)
    poly.grow_in(self)
    self.play(PolyMorph(poly, new_values))

    poly.spin_to(axis_index)                 # face the chosen axis forward

Architecture notes: the polyhedron never stores a camera object, because
Manim pickles the whole object family when caching a render. Orbiting is
therefore implemented as the content spinning around its own vertical axis,
with ``theta`` a plain float attribute. Labels use look-at billboards
projected onto world up, so they stay readable at any rotation angle.
"""

import math

import numpy as np
from manim import (
    Mobject,
    Animation,
    Create,
    DEGREES,
    FadeIn,
    Line,
    ORIGIN,
    Polygon,
    Scene,
    Text,
    VGroup,
    Y_AXIS,
    Z_AXIS,
)
from manim.mobject.three_d.three_dimensions import Dot3D
from manim.typing import Point3D
from manim.utils.color import ParsableManimColor
from manim.utils.space_ops import rotation_matrix

# ============================================================================
# Dodecahedron constant table (brute-force derivation + self-check; no hand-written values)
# ============================================================================
#: Golden ratio used to derive the dodecahedron coordinates.
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


def _unit(v: Point3D | tuple[float, float, float]) -> Point3D:
    """Normalize a vector to unit length.

    Parameters
    ----------
    v
        Input vector.

    Returns
    -------
        A unit-length copy of the vector.
    """

    v = np.asarray(v, dtype=float)
    return v / np.linalg.norm(v)


#: The 20 normalized dodecahedron vertex coordinates.
DODECA_VERTICES = [_unit(v) for v in _DODECA_RAW]

from itertools import combinations

_pair_d = {
    (i, j): float(np.linalg.norm(DODECA_VERTICES[i] - DODECA_VERTICES[j]))
    for i, j in combinations(range(20), 2)
}
"""Cached pairwise distances between dodecahedron vertices."""
#: Length of a dodecahedron edge.
EDGE_LEN = min(_pair_d.values())
#: Vertex index pairs connected by a dodecahedron edge.
DODECA_EDGES = [e for e, d in _pair_d.items() if d < EDGE_LEN * 1.5]

_EDGE_SET = {frozenset(e) for e in DODECA_EDGES}
#: Five-vertex faces of the dodecahedron.
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

#: Outward unit normal vector for each face.
FACE_NORMAL_DIRS = []
for face in DODECA_FACES:
    mean = np.mean([DODECA_VERTICES[i] for i in face], axis=0)
    FACE_NORMAL_DIRS.append(_unit(mean))
#: Distance from the center to a face plane (inradius).
INRADIUS = float(np.dot(DODECA_VERTICES[DODECA_FACES[0][0]], FACE_NORMAL_DIRS[0]))

#: Pairs of face indices that share an edge.
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
assert len(DODECA_EDGES) == 30, f"edge count {len(DODECA_EDGES)} != 30"
assert len(DODECA_FACES) == 12, f"face count {len(DODECA_FACES)} != 12"
assert all(len(f) == 5 for f in DODECA_FACES)
_cnt = np.zeros(20, dtype=int)
for f in DODECA_FACES:
    for i in f:
        _cnt[i] += 1
assert (_cnt == 3).all()
assert len(FACE_ADJ) == 30, f"dual edge count {len(FACE_ADJ)} != 30"
assert 0.5 < INRADIUS < 0.95, f"inradius ratio out of range: {INRADIUS:.3f}"

# ============================================================================
# PolyRadarChart
# ============================================================================
#: Stroke width of the skin surface edges.
SKIN_EDGE_W = 2.0
#: Colour of the skin surface edges.
SKIN_EDGE_C = "#5B7A9E"
#: Opacity of the skin surface faces.
SKIN_FACE_OP = 0.08
#: Highlight colour for dyed vertices.
DYE_C = "#00F5FF"
#: Highlight colour for edges.
EDGE_C = "#00E5CC"
#: Colour used for values above the full scale.
OVERFLOW_C = "#FF5A3C"
#: Colour of the axis labels.
LABEL_C = "#EAF2FF"


class PolyRadarChart(VGroup):
    """A twelve-axis radar drawn on a rotating dodecahedron.

    .. doc-example-covers: spin_to


    Parameters
    ----------
    axes_names
        Twelve axis labels.
    values
        One value per axis.
    max_value
        Full-scale value.
    radius
        Circumscribed radius of the dodecahedron.
    skins
        Nested shell scale factors.
    spin_rate
        Rotation speed in degrees per second.
    grow
        Whether the skeleton waits for :meth:`~manim_extensions.radar.poly.PolyRadarChart.grow_in` instead of appearing
        fully built.
    cam_pos
        Camera position used to orient the billboard labels.
    center
        World-space centre and rotation axis.
    sphere_color
        Default colour of the value spheres.
    kwargs
        Further keyword arguments forwarded to
        :class:`~manim.mobject.types.vectorized_mobject.VGroup`.

    Examples
    --------
    .. manim:: PolyRadarScene
       :save_last_frame:

       from manim import *
       from manim_extensions.radar.poly import PolyRadarChart

       class PolyRadarScene(ThreeDScene):
           def construct(self):
               chart = PolyRadarChart(
                   [str(i) for i in range(12)],
                   [3, 5, 7, 4, 6, 8, 5, 9, 4, 6, 7, 5],
               )
               self.add(chart)
    """

    def __init__(
        self,
        axes_names: Sequence[str],
        values: Sequence[float],
        *,
        max_value: float = 10.0,
        radius: float = 2.6,
        skins: Sequence[float] = (0.4, 0.7, 1.0),
        spin_rate: float = 7.0,
        grow: bool = True,
        cam_pos: Point3D | tuple[float, float, float] = (0.0, 0.0, 20.0),
        center: Point3D | tuple[float, float, float] = (0.0, -0.15, 0.0),
        sphere_color: ParsableManimColor = DYE_C,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.axes_names = list(axes_names)
        if len(self.axes_names) != 12:
            raise ValueError(
                f"PolyRadarChart requires 12 axes, got {len(self.axes_names)}"
            )
        self.max_value = float(max_value)
        self.poly_radius = float(radius)
        self.inr = (
            INRADIUS * self.poly_radius
        )  # world radius of the panel centre at full scale
        self.pivot = np.array(center, dtype=float)  # rotation axis (world coordinates)
        self.cam_pos = np.array(cam_pos, dtype=float)
        self.theta = 0.0  # rotation angle (plain float)
        self.spin_rate = float(spin_rate)  # degrees/second (slow by default)
        self.grow = bool(grow)
        self._frac = np.array(values, dtype=float) / self.max_value
        if len(self._frac) != 12:
            raise ValueError(f"requires 12 values, got {len(self._frac)}")

        # ---- skeleton: nested dodecahedron shells ----
        self.skins = VGroup()
        self.skin_parts = {}
        for s in skins:
            edges = VGroup()
            for i, j in DODECA_EDGES:
                p0 = self.pivot + np.array(DODECA_VERTICES[i]) * s * self.poly_radius
                p1 = self.pivot + np.array(DODECA_VERTICES[j]) * s * self.poly_radius
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
                            point=self.pivot + np.array(v) * s * self.poly_radius,
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
                                self.pivot
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
            self.skins.set_opacity(0.0)  # reveals layer by layer during grow_in
        self.add(self.skins)

        # ---- data layer: spheres / edges / triangular faces / labels ----
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
    def _data_triangles(self) -> list[tuple[int, ...]]:
        """Group the dodecahedron faces around each inner vertex.

        Returns
        -------
            Twenty face-index triples, one per dodecahedron vertex.
        """

        tris = []
        for v in range(20):
            fs = [fi for fi, face in enumerate(DODECA_FACES) if v in face]
            tris.append(tuple(fs))
        return tris

    def _world(self, i: int, extra: float = 0.0) -> np.ndarray:
        """Compute the rotated world position of an axis marker.

        Parameters
        ----------
        i
            Axis index.
        extra
            Additional radial offset.

        Returns
        -------
            The world-space position of the marker.
        """

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
        return self.pivot + Rz @ local

    def _rebuild(self) -> None:
        """Recompute sphere, edge, face and label geometry from ``_frac``."""
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

    def _tick(self, m: Mobject, dt: float) -> None:
        """Advance the automatic rotation.

        Parameters
        ----------
        m
            Mobject carrying the updater.
        dt
            Time step in seconds.
        """

        if self.spin_rate:
            delta = self.spin_rate * dt
            self.rotate(delta, axis=Z_AXIS, about_point=self.pivot)
            self.theta = (self.theta + delta) % 360.0
        # label orientation is handled by _billboard (become + look-at), see _attach_billboards

    def _attach_billboards(self) -> None:
        """Orient each label towards the camera and keep it upright.

        The updater cancels the chart rotation and applies a fixed camera
        tilt, so labels stay readable while their anchors spin with the
        data spheres.
        """

        self._label_base = [lab.copy().move_to(ORIGIN) for lab in self.labels]
        Rbill = rotation_matrix(75 * DEGREES, Y_AXIS)[:3, :3]

        def upd(m: Mobject, dt: float = 0.0) -> None:
            """Re-orient the labels after the chart rotates.

            Parameters
            ----------
            m
                Label group carrying the updater.
            dt
                Time step in seconds; unused because orientation depends on
                the absolute rotation angle.
            """

            th = math.radians(self.theta)
            M = rotation_matrix(-th, Z_AXIS)[:3, :3] @ Rbill
            for k, lab in enumerate(cast(Any, m)):
                anchor = self.pivot + rotation_matrix(th, Z_AXIS)[:3, :3] @ (
                    np.array(FACE_NORMAL_DIRS[k])
                    * (self.inr * float(self._frac[k]) + 0.55)
                )
                lab.become(self._label_base[k].copy().apply_matrix(M).move_to(anchor))

        self.labels.add_updater(upd)

    # ------------------------------------------------------------------
    def grow_in(self, scene: Scene, run_time: float = 0.45) -> "PolyRadarChart":
        """Animate the skeleton growing from the inner shell outwards.

        Parameters
        ----------
        scene
            Scene used to play the growth.
        run_time
            Duration of each shell animation.

        Returns
        -------
            This chart, allowing calls to be chained.
        """

        if not self.grow:
            return self
        for s in sorted(self.skin_parts):
            part = self.skin_parts[s]
            cast(Any, part["edges"]).set_stroke(
                opacity=(0.7 if s == max(self.skin_parts) else 0.42)
            )
            anims: list[Animation] = [Create(cast(Any, part["edges"]))]
            if part["faces"] is not None:
                anims.append(FadeIn(part["faces"]))
            if part["dots"] is not None:
                anims.append(FadeIn(part["dots"]))
            scene.play(*anims, run_time=run_time)
        return self

    def spin_to(self, axis_index: int, run_time: float = 1.2) -> Animation:
        """Rotate so one panel faces the camera.

        Parameters
        ----------
        axis_index
            Axis whose panel should end up facing the viewer.
        run_time
            Duration of the spin.

        Returns
        -------
            An animation that performs the rotation.
        """

        class Spin(Animation):
            """Rotate a poly chart by a fixed angular delta.

            Parameters
            ----------
                    poly
                        Chart to rotate.
                    delta
                        Rotation in radians.
                    kw
                        Further keyword arguments forwarded to
                        :class:`~manim.animation.animation.Animation`.

            Examples
            --------
            .. manim:: SpinScene

               from manim import *
               from manim_extensions.radar.poly import PolyRadarChart

               class SpinScene(ThreeDScene):
                   def construct(self):
                       chart = PolyRadarChart(
                           [str(i) for i in range(12)],
                           [3, 5, 7, 4, 6, 8, 5, 9, 4, 6, 7, 5],
                           grow=False,
                       )
                       self.add(chart)
                       self.play(chart.spin_to(axis_index=0, run_time=1.0))
            """

            def __init__(self, poly: PolyRadarChart, delta: float, **kw: Any) -> None:
                self.poly = poly
                self.delta = delta
                super().__init__(poly, **kw)

            def begin(self) -> None:
                """Record the starting rotation angle."""
                self.t0 = self.poly.theta

            def interpolate_mobject(self, alpha: float) -> None:
                r"""Rotate the chart from the recorded angle by :math:`\delta \alpha`."""
                new = self.t0 + self.delta * alpha
                self.poly.rotate(
                    new - self.poly.theta, axis=Z_AXIS, about_point=self.poly.pivot
                )
                self.poly.theta = new

            def finish(self) -> None:
                """Snap to the final angle and normalize the stored theta."""
                self.poly.rotate(
                    self.t0 + self.delta - self.poly.theta,
                    axis=Z_AXIS,
                    about_point=self.poly.pivot,
                )
                self.poly.theta = (self.t0 + self.delta) % 360.0

        az = math.atan2(
            FACE_NORMAL_DIRS[axis_index][1], FACE_NORMAL_DIRS[axis_index][0]
        )
        delta = -math.radians(self.theta) - az
        delta = (delta + math.pi) % (2 * math.pi) - math.pi
        return Spin(self, delta, run_time=run_time)

    def set_values(self, values: Sequence[float]) -> None:
        """Replace the data values and rebuild the geometry.

        Parameters
        ----------
        values
            New value per axis.
        """

        self._frac = np.array(values, dtype=float) / self.max_value
        self._rebuild()


class PolyMorph(Animation):
    """Morph the data spheres along their panel directions.

    Parameters
    ----------
    poly
        Chart to morph.
    target_values
        Destination value per axis.
    kwargs
        Further keyword arguments forwarded to
        :class:`~manim.animation.animation.Animation`.

    Examples
    --------
    .. manim:: PolyMorphScene

       from manim import *
       from manim_extensions.radar.poly import PolyMorph, PolyRadarChart

       class PolyMorphScene(ThreeDScene):
           def construct(self):
               chart = PolyRadarChart(
                   [str(i) for i in range(12)],
                   [3, 5, 7, 4, 6, 8, 5, 9, 4, 6, 7, 5],
                   grow=False,
               )
               self.add(chart)
               self.play(PolyMorph(chart, [9, 7, 8, 6, 5, 9, 4, 8, 6, 7, 5, 9]))
    """

    def __init__(
        self, poly: PolyRadarChart, target_values: Sequence[float], **kwargs: Any
    ) -> None:
        self.poly = poly
        self.target = np.array(target_values, dtype=float) / poly.max_value
        super().__init__(poly, **kwargs)

    def begin(self) -> None:
        """Snapshot the current fractions as the morph start state."""
        self.start = self.poly._frac.copy()

    def interpolate_mobject(self, alpha: float) -> None:
        """Blend the geometry towards the target values.

        Parameters
        ----------
        alpha
            Raw animation progress in the range 0 to 1.
        """

        self.poly._frac = self.start + (self.target - self.start) * alpha

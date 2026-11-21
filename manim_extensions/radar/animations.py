# SPDX-FileCopyrightText: 2026 FTZ-OPUS
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""All animations: the morph, the intro/outro and the transition effects.

New in 0.1.1: :class:`~manim_extensions.radar.animations.RadarMorph` morphs *lists* of datasets (comparison
mode) with an optional per-dataset ``stagger``, the ``"burst"`` transition
stabs values past their target (for :class:`~manim_extensions.radar.overflow.OverflowRadarChart`),
and :class:`~manim_extensions.radar.animations.RadarBurstIn` is the matching entrance.
"""

from __future__ import annotations
from typing import Any, Callable, Optional, Sequence, TYPE_CHECKING, cast

import math

from manim.typing import Point3D
from manim.utils.color import ParsableManimColor

import numpy as np
from manim import (
    DOWN,
    UP,
    Animation,
    ManimColor,
    Polygon,
    Rectangle,
    Scene,
    VGroup,
    smooth,
)

from .utils import ease_in_out_cubic, ease_out_overshoot, mix

if TYPE_CHECKING:
    from .chart import RadarChart
    from .data import RadarData

__all__ = [
    "RadarMorph",
    "RadarReveal",
    "RadarBurstIn",
    "RadarFade",
    "Shockwave",
    "GlitchFlash",
    "TRANSITIONS",
]

#: Named transition presets understood by :meth:`~manim_extensions.radar.chart.RadarChart.morph_to`.
TRANSITIONS = {
    "smooth": dict(dip=False, shockwave=False),
    "dip": dict(dip=True, shockwave=False),
    "shockwave": dict(dip=True, shockwave=True),
    "zoom": dict(dip=True, shockwave=True, dim=True),
    "glitch": dict(dip=True, shockwave=False, glitch=True),
    "stepped": dict(dip=True, shockwave=False, stepped=True),
    "burst": dict(dip=True, shockwave=True, burst=True),
}


# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------
def _ring_points(center: np.ndarray, radius: float, segments: int = 64) -> np.ndarray:
    """Build a closed polygonal approximation of a circle.

    Parameters
    ----------
    center
        World-space circle centre.
    radius
        Circle radius.
    segments
        Number of sides in the approximation.

    Returns
    -------
        Closed polygon points.
    """

    angles = np.linspace(0.0, 2.0 * math.pi, segments, endpoint=False)
    pts = np.array(
        [
            center + np.array([radius * math.cos(a), radius * math.sin(a), 0.0])
            for a in angles
        ]
    )
    return np.vstack([pts, pts[:1]])


class Ring(Polygon):
    """A ring whose radius, stroke width and opacity change every frame.

    Parameters
    ----------
    center
        World-space centre of the ring.
    color
        Stroke colour.
    kwargs
        Further keyword arguments forwarded to
        :class:`~manim.mobject.geometry.polygram.Polygon`.

    Examples
    --------
    .. manim:: RingScene
        :save_last_frame:

       from manim import *
       from manim_extensions.radar.animations import Ring

       class RingScene(Scene):
           def construct(self):
               ring = Ring(ORIGIN, "#E868C8", stroke_width=4.5)
               self.add(ring)
               ring.restyle(2.0, 1.0, 0.5)
    """

    def __init__(
        self, center: Point3D, color: ParsableManimColor, **kwargs: Any
    ) -> None:
        center = np.asarray(center, dtype=float)
        super().__init__(*(np.tile(center, (3, 1))), stroke_color=color, **kwargs)
        self.ring_center = center
        self.ring_color = ManimColor(color)

    def restyle(self, radius: float, width: float, opacity: float) -> None:
        """Resize and restyle the ring.

        Parameters
        ----------
        radius
            New radius.
        width
            New stroke width, clamped to a visible minimum.
        opacity
            New stroke opacity in the range 0 to 1.
        """

        self.set_points_as_corners(_ring_points(self.ring_center, radius))
        self.set_stroke(
            color=self.ring_color,
            width=max(0.05, width),
            opacity=float(np.clip(opacity, 0.0, 1.0)),
        )


def _flicker(alpha: float, steps: int = 6) -> float:
    """Alternate between dim and full opacity for a glitch effect.

    Parameters
    ----------
    alpha
        Animation progress in the range 0 to 1.
    steps
        Number of alternations across the animation.

    Returns
    -------
        Either 0.25 or 1.0.
    """

    return 0.25 if int(alpha * steps) % 2 == 0 else 1.0


# ---------------------------------------------------------------------------
# shockwave
# ---------------------------------------------------------------------------
class Shockwave(Animation):
    """An expanding (or imploding) ring.

    Cheap on its own, and a great way to cover a shape change.

    Parameters
    ----------
    center
        Centre of the ring; defaults to the origin.
    color
        Stroke colour.
    radius_start
        Initial ring radius.
    radius_end
        Final ring radius.
    width_start
        Initial stroke width.
    width_end
        Final stroke width.
    expand
        Whether the ring grows instead of collapsing.
    run_time
        Duration of the animation.
    rate_func
        Easing function.
    kwargs
        Further keyword arguments forwarded to
        :class:`~manim.animation.animation.Animation`.

    Examples
    --------
    ``self.play(chart.shockwave(color="#E868C8"))``
    """

    def __init__(
        self,
        center: Optional[Point3D] = None,
        *,
        color: ParsableManimColor = "#FFFFFF",
        radius_start: float = 0.18,
        radius_end: float = 5.0,
        width_start: float = 4.5,
        width_end: float = 0.7,
        expand: bool = True,
        run_time: float = 0.42,
        rate_func: Callable[[float], float] = smooth,
        **kwargs: Any,
    ) -> None:
        if center is None:
            center = np.zeros(3)
        self._expand = expand
        self._r0, self._r1 = (
            (radius_start, radius_end) if expand else (radius_end, radius_start)
        )
        self._w0, self._w1 = (
            (width_start, width_end) if expand else (width_end, width_start)
        )
        super().__init__(
            Ring(np.asarray(center, dtype=float), color, stroke_width=width_start),
            run_time=run_time,
            rate_func=rate_func,
            **kwargs,
        )

    def interpolate_mobject(self, alpha: float) -> None:
        """Restyle the ring for the current animation progress.

        Parameters
        ----------
        alpha
            Raw animation progress in the range 0 to 1.
        """
        k = self.rate_func(alpha)
        cast(Any, self.mobject).restyle(
            self._r0 + (self._r1 - self._r0) * k,
            self._w0 + (self._w1 - self._w0) * k,
            0.9 * (1.0 - k),
        )


# ---------------------------------------------------------------------------
# the morph
# ---------------------------------------------------------------------------
class RadarMorph(Animation):
    """Morph a :class:`~manim_extensions.radar.chart.RadarChart` into another snapshot.

    Values, full scale, colours, emphasis outlines and opacity are
    interpolated in a single pass. The shape can first "dip" and then roll up
    to the target (the signature move of style ``neo``), snap in integer
    steps (``classic``), or stab past the target and settle back
    (``"burst"``, the signature move of the overflow chart).

    ``target`` may be a single snapshot or a **list** of snapshots — a list
    morphs every dataset of a comparison at once, optionally with a
    per-dataset ``stagger`` delay.

    Usually you do not instantiate this directly — call
    :meth:`~manim_extensions.radar.chart.RadarChart.morph_to`.

    Parameters
    ----------
    chart
        Chart to morph.
    target
        Destination snapshot, or a list of snapshots for comparison mode.
    transition
        Named transition preset.
    run_time
        Duration; defaults to the chart configuration.
    rate_func
        Easing function.
    dip
        Whether values dip before rising.
    dip_ratio
        Relative depth of the dip.
    shockwave
        Whether to emit a shockwave ring.
    shock_color
        Colour of that ring.
    stepped
        Whether values move in integer steps.
    dim
        Whether to dim the grid during the morph.
    glitch
        Whether to add a chromatic glitch.
    burst
        Whether to overshoot the target before settling.
    colors
        Whether target colours are blended into the chart.
    rim
        Optional rim strength override.
    opacity
        Optional chart opacity target.
    fade_name
        Whether the nameplate crossfades to the target name.
    name_shift
        Vertical travel of the nameplate crossfade.
    stagger
        Per-dataset delay in comparison mode.
    kwargs
        Further keyword arguments forwarded to
        :class:`~manim.animation.animation.Animation`.

    Examples
    --------
    .. code-block:: python

        from manim_extensions.radar.chart import RadarChart
        from manim_extensions.radar.animations import RadarMorph

        chart = RadarChart(axes=["Speed", "Power", "Range", "Comfort", "Price", "Safety"], values=[8, 6, 7, 9, 5, 8])
        morph = RadarMorph(chart, [7, 8, 6, 5, 9, 7])
    """

    def __init__(
        self,
        chart: RadarChart,
        target: Sequence[RadarData],
        *,
        transition: Optional[str] = None,
        run_time: Optional[float] = None,
        rate_func: Callable[[float], float] = smooth,
        dip: Optional[bool] = None,
        dip_ratio: Optional[float] = None,
        shockwave: Optional[bool] = None,
        shock_color: Optional[ParsableManimColor] = None,
        stepped: Optional[bool] = None,
        dim: Optional[bool] = None,
        glitch: Optional[bool] = None,
        burst: Optional[bool] = None,
        colors: bool = True,
        rim: Optional[float] = None,
        opacity: Optional[float] = None,
        fade_name: bool = True,
        name_shift: float = 0.30,
        stagger: Optional[float] = None,
        **kwargs: Any,
    ) -> None:
        if transition is not None and transition not in TRANSITIONS:
            raise ValueError(
                f"unknown transition {transition!r}; available: "
                f"{', '.join(TRANSITIONS)}, or None"
            )
        preset = dict(TRANSITIONS.get(transition, {})) if transition else {}
        cfg = chart.config

        self.chart = chart
        self.targets = chart._coerce_dataset_list(target)
        self.dip = preset.get("dip", True) if dip is None else dip
        self.dip_ratio = (
            (cfg.dip_ratio if dip_ratio is None else dip_ratio) if self.dip else 0.0
        )
        self.shockwave = (
            preset.get("shockwave", cfg.shockwave) if shockwave is None else shockwave
        )
        self.shock_color = shock_color
        self.stepped = (
            preset.get("stepped", cfg.stepped) if stepped is None else stepped
        )
        self.dim = preset.get("dim", False) if dim is None else dim
        self.glitch = preset.get("glitch", False) if glitch is None else glitch
        self.burst = preset.get("burst", False) if burst is None else burst
        self.colors = colors
        self.rim_override = rim
        self.opacity_target = opacity
        self.fade_name = fade_name
        self.name_shift = name_shift
        self.stagger = cfg.stagger if stagger is None else float(stagger)
        self._ring: Optional[Ring] = None
        self._cam: Optional[dict[str, Any]] = None
        self._legend_path: Optional[str] = None
        super().__init__(
            chart,
            run_time=run_time if run_time is not None else cfg.morph_run_time,
            rate_func=rate_func,
            **kwargs,
        )

    # ------------------------------------------------------------------
    def begin(self) -> None:
        """Capture the starting state and prepare the animation targets."""
        chart = self.chart
        cfg = chart.config
        self.start_count = len(chart._series)
        chart._ensure_series_count(len(self.targets), self.targets)
        self.k = max(self.start_count, len(self.targets))

        self.start_scale = float(chart._scale)
        self.end_scale = float(max(t.scale_for(cfg.levels) for t in self.targets))
        self.start_opacity = float(chart._opacity)
        self.end_chart_opacity = (
            float(self.opacity_target)
            if self.opacity_target is not None
            else self.start_opacity
        )

        self.slots: list[dict[str, Any]] = []
        for i in range(self.k):
            s = chart._series[i] if i < len(chart._series) else None
            t = self.targets[i] if i < len(self.targets) else None
            start_values = list(s.values) if s is not None else [0.0] * chart._n
            end_values = (
                [float(v) for v in t.values] if t is not None else [0.0] * chart._n
            )
            if s is not None:
                start_color = ManimColor(s.color)
            elif t is not None:
                start_color = chart._resolve_color(t.color, i)
            else:
                start_color = ManimColor("#FFFFFF")
            end_color = (
                chart._resolve_color(t.color, i)
                if (t is not None and self.colors)
                else start_color
            )
            start_rim = float(s.rim) if s is not None else 0.0
            if t is None:
                end_rim = 0.0
            elif self.rim_override is not None:
                end_rim = float(self.rim_override)
            elif t.rim or t.emphasis == "rim":
                end_rim = 1.0
            else:
                end_rim = 1.0 if cfg.rim else 0.0
            start_op = float(s.opacity) if s is not None else 0.0
            end_op = 0.0 if t is None else 1.0
            if self.burst:
                # a burst gathers values low (20% of target) so the stab has
                # a long run-up — the regular dip would leave it no overshoot
                dip_values = [0.20 * e for e in end_values]
            elif self.dip:
                dip_values = [max(cfg.dip_floor, e - cfg.dip_drop) for e in end_values]
            else:
                dip_values = list(start_values)
            self.slots.append(
                dict(
                    start_values=start_values,
                    end_values=end_values,
                    dip_values=dip_values,
                    start_color=start_color,
                    end_color=end_color,
                    start_rim=start_rim,
                    end_rim=end_rim,
                    start_op=start_op,
                    end_op=end_op,
                )
            )

        if self.shockwave:
            self._ring = Ring(
                chart._anchor[0].get_center(),
                self.shock_color or self.slots[0]["end_color"],
                stroke_width=4.5,
            )
            chart.add(self._ring)

        if len(self.targets) > 1 or self.start_count > 1:
            if len(self.targets) > 1:
                chart._begin_legend_swap(self.targets)
                self._legend_path = "swap"
            else:
                chart._begin_legend_fadeout()
                self._legend_path = "fadeout"
        elif self.fade_name:
            chart._begin_name_swap(self.targets[0].name or "", shift=self.name_shift)

        self._cam = self._prepare_camera()

    def _prepare_camera(self) -> Optional[dict[str, Any]]:
        """Compute the automatic micro-push target for a burst morph.

        Returns
        -------
            Camera target when a rig is attached and a spike overflows,
            otherwise ``None``.
        """

        chart = self.chart
        if not self.burst or chart._rig is None:
            return None
        frame = getattr(chart._rig, "frame", None)
        if frame is None:
            return None
        best_over, best_axis = 0.0, None
        for t in self.targets:
            for j, val in enumerate(t.values):
                if val - self.end_scale > best_over:
                    best_over = val - self.end_scale
                    best_axis = j
        if best_axis is None:
            return None
        a, u, v = chart._frame()
        local = chart._polar_local(chart._angles[best_axis], 1.0)
        w = chart._to_world(np.array([local]), a, u, v)[0] - a
        norm = float(np.linalg.norm(w))
        if norm < 1e-6:
            return None
        dip0 = self.slots[0]["dip_values"][best_axis]
        end0 = self.slots[0]["end_values"][best_axis]
        frac = (self.end_scale - dip0) / (end0 - dip0) if end0 > dip0 else 0.0
        r = self.dip_ratio
        frac_alpha = r + (1.0 - r) * min(1.0, max(0.05, frac))
        return dict(
            frame=frame,
            direction=w / norm,
            frac_alpha=frac_alpha,
            center=frame.get_center().copy(),
            width=frame.width,
            height=frame.height,
            # the envelope must complete *inside* the morph: a high spike
            # fires the push late, so scale the duration to the time left
            duration=min(0.7, max(0.25, (1.0 - frac_alpha) * self.run_time * 0.9)),
            fired=False,
            t0=0.0,
            restored=False,
        )

    def _update_camera(self, alpha: float) -> None:
        """Advance the automatic camera push during a burst morph.

        Parameters
        ----------
        alpha
            Raw animation progress in the range 0 to 1.
        """

        cam = self._cam
        if cam is None or cam["restored"]:
            return
        if not cam["fired"]:
            if alpha < cam["frac_alpha"]:
                return
            cam["fired"] = True
            cam["t0"] = alpha
        t = (alpha - cam["t0"]) * self.run_time
        duration = cam["duration"]
        if t >= duration:
            cam["frame"].move_to(cam["center"])
            cam["frame"].stretch_to_fit_width(cam["width"])
            cam["frame"].stretch_to_fit_height(cam["height"])
            cam["restored"] = True
            return
        envelope = math.sin(math.pi * t / duration)
        frame = cam["frame"]
        frame.move_to(cam["center"] + cam["direction"] * 0.30 * envelope)
        factor = 1.0 - 0.08 * envelope
        frame.stretch_to_fit_width(cam["width"] * factor)
        frame.stretch_to_fit_height(cam["height"] * factor)

    def _restore_camera(self) -> None:
        """Force the camera home if a morph ended mid-push."""
        cam = self._cam
        if cam is not None and not cam["restored"]:
            cam["frame"].move_to(cam["center"])
            cam["frame"].stretch_to_fit_width(cam["width"])
            cam["frame"].stretch_to_fit_height(cam["height"])
            cam["restored"] = True

    # ------------------------------------------------------------------
    def interpolate_mobject(self, alpha: float) -> None:
        """Blend values, colours, rims, opacity and effects for one frame.

        Parameters
        ----------
        alpha
            Raw animation progress in the range 0 to 1.
        """
        a = self.rate_func(alpha)
        chart = self.chart
        cfg = chart.config
        r = self.dip_ratio
        k = self.k
        st = self.stagger if (k > 1 and self.stagger > 1e-6) else 0.0
        total = 1.0 + (k - 1) * st if st > 0 else 1.0

        # -- shared full scale ------------------------------------------
        if r > 1e-6 and a < r:
            scale = self.start_scale
        else:
            t = (a - r) / (1.0 - r) if r < 1.0 - 1e-6 else 1.0
            scale = self.start_scale + (
                self.end_scale - self.start_scale
            ) * ease_in_out_cubic(max(0.0, min(1.0, t)))
        chart._scale = max(1e-6, scale)

        # -- per-dataset values / colours / rims --------------------------
        for i, slot in enumerate(self.slots):
            ai = min(1.0, max(0.0, a * total - i * st)) if st > 0 else a
            if r > 1e-6 and ai < r:
                t = ease_in_out_cubic(ai / r)
                values = [
                    s0 + (d - s0) * t
                    for s0, d in zip(slot["start_values"], slot["dip_values"])
                ]
            else:
                t = (ai - r) / (1.0 - r) if r < 1.0 - 1e-6 else 1.0
                t = max(0.0, min(1.0, t))
                t = (
                    ease_out_overshoot(t, cfg.burst_overshoot)
                    if self.burst
                    else ease_in_out_cubic(t)
                )
                values = [
                    b + (e - b) * t
                    for b, e in zip(slot["dip_values"], slot["end_values"])
                ]
            if self.stepped:
                values = [float(round(v)) for v in values]
            s = chart._series[i]
            s.values = values
            s.color = mix(slot["start_color"], slot["end_color"], min(1.0, ai * 1.15))
            s.rim = slot["start_rim"] + (slot["end_rim"] - slot["start_rim"]) * ai
            s.opacity = slot["start_op"] + (slot["end_op"] - slot["start_op"]) * ai

        # keep the 0.1.0 mirrors pointing at dataset 0
        chart._values = list(chart._series[0].values)
        chart._color = chart._series[0].color
        chart._rim = chart._series[0].rim

        # -- global dim / glitch / opacity -------------------------------
        dim_factor = 1.0
        if self.dim:
            dim_factor = 0.15 + 0.85 * abs(2.0 * a - 1.0)
        if self.glitch:
            chart._glitch = max(0.0, 1.0 - a / 0.45)
            dim_factor *= _flicker(a)
        else:
            chart._glitch = 0.0
        chart._opacity = (
            self.start_opacity + (self.end_chart_opacity - self.start_opacity) * a
        ) * dim_factor

        # -- shockwave ring ----------------------------------------------
        if self._ring is not None:
            k_wave = min(1.0, a / 0.55)
            radius = 0.18 + (chart.config.shock_radius - 0.18) * k_wave
            self._ring.restyle(radius, 4.5 * (1.0 - k_wave) + 0.7, 0.9 * (1.0 - k_wave))

        # -- nameplate / legend crossfade ---------------------------------
        t_name = min(1.0, max(0.0, (a - 0.25) / 0.75))
        if self._legend_path is not None:
            chart._legend_swap_progress(t_name)
        elif self.fade_name:
            chart._swap_name_progress(t_name, shift=self.name_shift)

        # -- burst camera micro-push --------------------------------------
        self._update_camera(a)

    # ------------------------------------------------------------------
    def finish(self) -> None:
        """Write the final values back and release temporary effects."""
        chart = self.chart
        while len(chart._series) > len(self.targets):
            chart._drop_series(len(chart._series) - 1)
        for i, slot in enumerate(self.slots):
            if i >= len(self.targets):
                break
            s = chart._series[i]
            s.values = list(slot["end_values"])
            s.color = slot["end_color"]
            s.rim = slot["end_rim"]
            s.opacity = slot["end_op"]
            s.opacity_target = slot["end_op"]
            s.data = self.targets[i]
        chart._scale = self.end_scale
        chart._values = list(chart._series[0].values)
        chart._color = chart._series[0].color
        chart._rim = chart._series[0].rim
        chart._glitch = 0.0
        chart._opacity = self.end_chart_opacity
        chart._sync_number_scale()

        if self._ring is not None:
            chart.remove(self._ring)
            self._ring = None
        if self._legend_path is not None:
            chart._end_legend_swap()
        elif self.fade_name:
            chart._end_name_swap()

    def clean_up_from_scene(self, scene: Scene) -> None:
        """Remove temporary morph effects from the scene.

        Parameters
        ----------
        scene
            Scene being cleaned up.
        """
        self._drop_ring()
        super().clean_up_from_scene(scene)

    def _drop_ring(self) -> None:
        """Remove the transient shockwave ring from the chart, if present."""
        if self._ring is not None:
            try:
                self.chart.remove(self._ring)
            except ValueError:  # pragma: no cover - already removed
                pass
            self._ring = None


# ---------------------------------------------------------------------------
# intro / outro
# ---------------------------------------------------------------------------
class RadarReveal(Animation):
    """Grow the chart out of its centre while fading in every dataset.

    Parameters
    ----------
    chart
        Chart to reveal.
    run_time
        Duration of the animation.
    rate_func
        Easing function.
    from_values
        Initial values for dataset 0; others start at zero.
    with_shockwave
        Whether to emit a shockwave ring during the reveal.
    kwargs
        Further keyword arguments forwarded to
        :class:`~manim.animation.animation.Animation`.

    Examples
    --------
    .. code-block:: python

        from manim_extensions.radar.chart import RadarChart
        from manim_extensions.radar.animations import RadarReveal

        chart = RadarChart(axes=["A", "B", "C"], values=[1, 2, 3])
        reveal = RadarReveal(chart)
    """

    def __init__(
        self,
        chart: RadarChart,
        *,
        run_time: float = 0.9,
        rate_func: Callable[[float], float] = smooth,
        from_values: Optional[Sequence[float]] = None,
        with_shockwave: Optional[bool] = None,
        **kwargs: Any,
    ) -> None:
        self.chart = chart
        self.from_values = (
            list(from_values) if from_values is not None else [0.0] * chart.axis_count
        )
        self.with_shockwave = (
            chart.config.shockwave if with_shockwave is None else with_shockwave
        )
        self._ring: Optional[Ring] = None
        super().__init__(chart, run_time=run_time, rate_func=rate_func, **kwargs)

    def begin(self) -> None:
        """Capture the starting state and prepare the animation targets."""
        chart = self.chart
        self.to_values = [list(s.values) for s in chart._series]
        self.to_opacity = float(chart._opacity) or 1.0
        for s in chart._series:
            s.values = [0.0] * chart.axis_count
        chart._values = list(chart._series[0].values)
        chart._opacity = 0.0
        if self.with_shockwave:
            self._ring = Ring(
                chart._anchor[0].get_center(), chart._series[0].color, stroke_width=4.5
            )
            chart.add(self._ring)

    def interpolate_mobject(self, alpha: float) -> None:
        """Advance the animation for the given progress.

        Parameters
        ----------
        alpha
            Raw animation progress in the range 0 to 1.
        """
        a = self.rate_func(alpha)
        chart = self.chart
        for i, s in enumerate(chart._series):
            src = self.from_values if i == 0 else [0.0] * chart.axis_count
            s.values = [f + (t - f) * a for f, t in zip(src, self.to_values[i])]
        chart._values = list(chart._series[0].values)
        chart._opacity = self.to_opacity * a
        if self._ring is not None:
            k = min(1.0, a / 0.6)
            radius = 0.18 + (chart.config.shock_radius - 0.18) * k
            self._ring.restyle(radius, 4.5 * (1.0 - k) + 0.7, 0.9 * (1.0 - k))

    def finish(self) -> None:
        """Write the final values back and release temporary effects."""
        chart = self.chart
        for i, s in enumerate(chart._series):
            s.values = list(self.to_values[i])
        chart._values = list(chart._series[0].values)
        chart._opacity = self.to_opacity
        if self._ring is not None:
            chart.remove(self._ring)
            self._ring = None

    def clean_up_from_scene(self, scene: Scene) -> None:
        """Remove temporary rings and call the base cleanup.

        Parameters
        ----------
        scene
            Scene being cleaned up.
        """
        if self._ring is not None:
            try:
                self.chart.remove(self._ring)
            except ValueError:  # pragma: no cover
                pass
            self._ring = None
        super().clean_up_from_scene(scene)


class RadarBurstIn(Animation):
    """The overflow entrance: values stab *past* their target, then settle.

    Typical use on an :class:`~manim_extensions.radar.overflow.OverflowRadarChart`::

        self.play(chart.burst_in())

    Parameters
    ----------
    chart
        Overflow chart to reveal.
    run_time
        Duration of the animation.
    rate_func
        Easing function.
    with_shockwave
        Whether to emit a shockwave ring during the entrance.
    kwargs
        Further keyword arguments forwarded to
        :class:`~manim.animation.animation.Animation`.

    Examples
    --------
    .. code-block:: python

        from manim_extensions.radar.chart import RadarChart
        from manim_extensions.radar.animations import RadarBurstIn

        chart = RadarChart(axes=["A", "B", "C"], values=[1, 2, 3])
        burst = RadarBurstIn(chart)
    """

    def __init__(
        self,
        chart: RadarChart,
        *,
        run_time: float = 1.1,
        rate_func: Callable[[float], float] = smooth,
        with_shockwave: Optional[bool] = None,
        **kwargs: Any,
    ) -> None:
        self.chart = chart
        self.overshoot = chart.config.burst_overshoot
        self.with_shockwave = (
            chart.config.shockwave if with_shockwave is None else with_shockwave
        )
        self._ring: Optional[Ring] = None
        super().__init__(chart, run_time=run_time, rate_func=rate_func, **kwargs)

    def begin(self) -> None:
        """Capture the starting state and prepare the animation targets."""
        chart = self.chart
        self.to_values = [list(s.values) for s in chart._series]
        self.to_opacity = float(chart._opacity) or 1.0
        for s in chart._series:
            s.values = [0.0] * chart.axis_count
        chart._values = list(chart._series[0].values)
        chart._opacity = 0.0
        if self.with_shockwave:
            self._ring = Ring(
                chart._anchor[0].get_center(), chart._series[0].color, stroke_width=4.5
            )
            chart.add(self._ring)

    def interpolate_mobject(self, alpha: float) -> None:
        """Advance the animation for the given progress.

        Parameters
        ----------
        alpha
            Raw animation progress in the range 0 to 1.
        """
        a = self.rate_func(alpha)
        chart = self.chart
        f = ease_out_overshoot(a, self.overshoot)
        for i, s in enumerate(chart._series):
            s.values = [t * f for t in self.to_values[i]]
        chart._values = list(chart._series[0].values)
        chart._opacity = self.to_opacity * min(1.0, a * 2.5)
        if self._ring is not None:
            k = min(1.0, a / 0.6)
            radius = 0.18 + (chart.config.shock_radius - 0.18) * k
            self._ring.restyle(radius, 4.5 * (1.0 - k) + 0.7, 0.9 * (1.0 - k))

    def finish(self) -> None:
        """Write the final values back and release temporary effects."""
        chart = self.chart
        for i, s in enumerate(chart._series):
            s.values = list(self.to_values[i])
        chart._values = list(chart._series[0].values)
        chart._opacity = self.to_opacity
        if self._ring is not None:
            chart.remove(self._ring)
            self._ring = None

    def clean_up_from_scene(self, scene: Scene) -> None:
        """Remove temporary rings and call the base cleanup.

        Parameters
        ----------
        scene
            Scene being cleaned up.
        """
        if self._ring is not None:
            try:
                self.chart.remove(self._ring)
            except ValueError:  # pragma: no cover
                pass
            self._ring = None
        super().clean_up_from_scene(scene)


class RadarFade(Animation):
    """Fade the whole chart, including every painted layer.

    Parameters
    ----------
    chart
        Chart to fade.
    to
        Target opacity in the range 0 to 1.
    run_time
        Duration of the animation.
    rate_func
        Easing function.
    kwargs
        Further keyword arguments forwarded to
        :class:`~manim.animation.animation.Animation`.

    Examples
    --------
    .. code-block:: python

        from manim_extensions.radar.chart import RadarChart
        from manim_extensions.radar.animations import RadarFade

        chart = RadarChart(axes=["A", "B", "C"], values=[1, 2, 3])
        fade = RadarFade(chart, to=0.0)
    """

    def __init__(
        self,
        chart: RadarChart,
        to: float = 0.0,
        *,
        run_time: float = 0.8,
        rate_func: Callable[[float], float] = smooth,
        **kwargs: Any,
    ) -> None:
        self.chart = chart
        self.to = float(np.clip(to, 0.0, 1.0))
        super().__init__(chart, run_time=run_time, rate_func=rate_func, **kwargs)

    def begin(self) -> None:
        """Capture the starting state and prepare the animation targets."""
        self.start = float(self.chart._opacity)

    def interpolate_mobject(self, alpha: float) -> None:
        """Advance the animation for the given progress.

        Parameters
        ----------
        alpha
            Raw animation progress in the range 0 to 1.
        """
        a = self.rate_func(alpha)
        self.chart._opacity = self.start + (self.to - self.start) * a

    def finish(self) -> None:
        """Write the final values back and release temporary effects."""
        self.chart._opacity = self.to


class GlitchFlash(Animation):
    """Chromatic split and scan bars for a glitch-style entrance.

    Typical use::

        self.play(chart.disappear())   # fade to black
        self.wait(1.5)
        self.play(chart.glitch_in())   # snap back on

    Parameters
    ----------
    chart
        Chart to bring back.
    run_time
        Duration of the animation.
    rate_func
        Easing function.
    bars
        Whether to draw horizontal scan bars.
    flickers
        Number of opacity flickers during the entrance.
    kwargs
        Further keyword arguments forwarded to
        :class:`~manim.animation.animation.Animation`.

    Examples
    --------
    .. code-block:: python

        from manim_extensions.radar.chart import RadarChart
        from manim_extensions.radar.animations import GlitchFlash

        chart = RadarChart(axes=["A", "B", "C"], values=[1, 2, 3])
        flash = GlitchFlash(chart)
    """

    def __init__(
        self,
        chart: RadarChart,
        *,
        run_time: float = 0.75,
        rate_func: Callable[[float], float] = smooth,
        bars: bool = True,
        flickers: int = 3,
        **kwargs: Any,
    ) -> None:
        self.chart = chart
        self.bars = bars
        self.flickers = max(1, int(flickers))
        self._bars: Optional[VGroup] = None
        super().__init__(chart, run_time=run_time, rate_func=rate_func, **kwargs)

    def begin(self) -> None:
        """Capture the starting state and prepare the animation targets."""
        chart = self.chart
        self._to_opacity = max(0.6, float(chart._opacity) or 1.0)
        chart._opacity = 0.0
        chart.set_glitch(1.0)
        if self.bars:
            width = chart.config.glitch_bar_width
            self._bars = VGroup(
                Rectangle(
                    width=width,
                    height=0.16,
                    fill_color="#FFFFFF",
                    fill_opacity=0.40,
                    stroke_width=0,
                ),
                Rectangle(
                    width=width,
                    height=0.07,
                    fill_color="#FFFFFF",
                    fill_opacity=0.30,
                    stroke_width=0,
                ),
            )
            center = chart._anchor[0].get_center()
            self._bars[0].move_to(center + DOWN * 3.4)
            self._bars[1].move_to(center + UP * 3.2)
            chart.add(self._bars)

    def interpolate_mobject(self, alpha: float) -> None:
        """Advance the animation for the given progress.

        Parameters
        ----------
        alpha
            Raw animation progress in the range 0 to 1.
        """
        a = self.rate_func(alpha)
        chart = self.chart
        chart.set_glitch(max(0.0, 1.0 - a / 0.6))
        chart._opacity = (
            self._to_opacity
            if a > 0.6
            else self._to_opacity * _flicker(a, self.flickers + 1)
        )
        if self._bars is not None:
            center = chart._anchor[0].get_center()
            self._bars[0].set_y(center[1] - 3.4 + 8.0 * a)
            self._bars[1].set_y(center[1] + 3.2 - 8.0 * a)
            self._bars.set_opacity(max(0.0, 1.0 - a * 1.5))

    def finish(self) -> None:
        """Write the final values back and release temporary effects."""
        chart = self.chart
        chart.set_glitch(0.0)
        chart._opacity = self._to_opacity
        if self._bars is not None:
            chart.remove(self._bars)
            self._bars = None

    def clean_up_from_scene(self, scene: Scene) -> None:
        """Remove temporary rings and call the base cleanup.

        Parameters
        ----------
        scene
            Scene being cleaned up.
        """
        if self._bars is not None:
            try:
                self.chart.remove(self._bars)
            except ValueError:  # pragma: no cover
                pass
            self._bars = None
        super().clean_up_from_scene(scene)

# SPDX-FileCopyrightText: 2026 FTZ-OPUS
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
# patched: use the package-wide CJK font resolver instead of the macOS-only PingFang SC

"""Utilities for the core module."""

from __future__ import annotations
from collections.abc import Callable, Sequence
from typing import Any, Optional, Union, cast

# -*- coding: utf-8 -*-
"""Three-dimensional geometry and animation presets for Manim.

The package ships six ready-made surfaces: Gaussian, saddle, paraboloid,
ellipsoid, torus, and one-sheet hyperboloid. The goal is a complete scene
from a few lines of code. The beats (title, axes, formation, contours,
orbit, flip, annotation, outro) are fully parameterized, and the total
duration is allocated by weight. A ten-second animation can keep every
essential beat; optional beats are dropped by priority when time runs out.

Typical use::

    from manim_extensions.three_d import (
        GaussianSurface,
        GaussianSurfaceScene,
        SaddleSurface,
        SaddleSurfaceScene,
    )

    class MyGaussian(GaussianSurfaceScene):
        style = GaussianSurface(captions=(...), duration=12)

        def construct(self):
            super().construct()

    class MySaddle(SaddleSurfaceScene):
        style = SaddleSurface(captions=(...))

        def construct(self):
            super().construct()

Conventions: ``duration`` is the content budget excluding caption swaps,
each of which adds roughly 0.9 seconds scaled by the pace. Beat durations
start from their reference length times ``duration / 45`` and are clamped
to their minimum and maximum. When the budget cannot fit everything, beats
are dropped in priority order (contours, flat plane, annotation, orbit,
flip) and the choice is printed. Caption slots follow each surface's beat
sequence through ``_caption_slots``.
"""

from manim import (
    Animation,
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
    VMobject,
    WHITE,
    Write,
    YELLOW,
    interpolate_color,
    smooth,
)

from manim.mobject.mobject import _AnimationBuilder
from manim.typing import Point3D

from ..mobjects import DEFAULT_CJK_FONT
import numpy as np
from dataclasses import dataclass

SurfaceFunction = Callable[[float, float], float]
ColorRamp = Sequence[tuple[Union[str, ManimColor], float]]
GeometrySpec = tuple[SurfaceFunction, Optional[str], float, float, float]
ContourSpec = tuple[VGroup, bool]
FeatureSpec = tuple[float, float, float, str, bool, float]

__all__ = [
    "GaussianSurface",
    "SaddleSurface",
    "ParaboloidSurface",
    "EllipsoidSurface",
    "TorusSurface",
    "HyperboloidOneSheet",
    "GraphSurfaceScene",
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

# ---------------- Colour themes ----------------
#: Named colour ramps used to colour the timeline.
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

# ---------------- Beat table ----------------
# (name, reference seconds, minimum seconds, maximum = reference x factor, cut priority: 1 first, None = keep)
#: Beat table: name, reference/min/max seconds, and cut priority.
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
#: Per-pace total duration in seconds for the timeline.
PACE = {"fast": 10.0, "normal": 24.0, "full": 45.0}


def plan_timeline(
    duration: float, enabled: set[str]
) -> tuple[dict[str, float], list[str]]:
    """Distribute a duration across the enabled beats.

    Parameters
    ----------
    duration
        Total content budget in seconds.
    enabled
        Names of beats that should be scheduled.

    Returns
    -------
        A mapping from beat name to duration, and the names of dropped beats.

        Durations are scaled proportionally, clamped between each beat's
        minimum and reference times the cap multiplier, and iterated until they
        converge. If every optional beat can be removed and the budget still
        does not fit, optional beats are dropped by priority. If every beat
        reaches its maximum before the budget is filled, the shorter result is
        accepted.
    """

    active = [b for b in BEATS if b[0] in enabled]
    dropped: list[str] = []
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
        victim = min(cands, key=lambda b: b[4] if b[4] is not None else 0)
        active = [b for b in active if b[0] is not victim[0]]
        dropped.append(victim[0])


def _ramp_color(ramp: ColorRamp, t: float) -> ManimColor:
    """Sample a colour ramp at a normalized position.

    Parameters
    ----------
    ramp
        Sequence of ``(colour, position)`` stops.
    t
        Position in the range 0 to 1.

    Returns
    -------
        The interpolated colour at that position.
    """

    t = min(max(t, 0.0), 1.0)
    for (c1, v1), (c2, v2) in zip(ramp, ramp[1:]):
        if v1 <= t <= v2:
            return interpolate_color(
                ManimColor(c1), ManimColor(c2), (t - v1) / (v2 - v1)
            )
    return ManimColor(ramp[-1][0])


def _radius_for_level(
    f: SurfaceFunction, d_max: float, c: float, n: int = 60
) -> Optional[float]:
    """Find the nearest radius where the surface reaches a level.

    Parameters
    ----------
    f
        Surface height function.
    d_max
        Outer search radius.
    c
        Target height.
    n
        Number of bisection steps.

    Returns
    -------
        The radius of the nearest root along the positive x direction, or
        ``None`` when the surface never reaches the target.
    """

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
    """Format a coordinate label without trailing zeros.

    Parameters
    ----------
    v
        Coordinate value.

    Returns
    -------
        The value rounded to two decimals, with trailing zeros and a trailing
        decimal point removed.
    """

    return f"{v:.2f}".rstrip("0").rstrip(".")


# ---------------- Configuration ----------------
@dataclass
class GaussianSurface:
    """Tunable parameters for a Gaussian surface, generalized to :math:`z=f(x, y)`.

    Examples
    --------
    .. manim:: GaussianSurfaceConfigScene
       :save_last_frame:

       from manim import *
       from manim_extensions.three_d.core import GaussianSurface, GaussianSurfaceScene

       class GaussianSurfaceConfigScene(GaussianSurfaceScene):
           style = GaussianSurface(height=1.4, rings=True, orbit=True, pace='fast')
    """

    func: Optional[Callable[..., float]] = None  # z=f(x,y); None = built-in Gaussian
    func_tex: Optional[str] = (
        None  # corner formula; None = custom function without a displayed formula
    )
    domain: tuple[float, float] = (-2.6, 2.6)  # x/y domain
    resolution: tuple[int, int] = (40, 40)  # surface mesh density
    colors: str | Sequence[tuple[str, float]] = (
        "rainbow"  # RAMPS theme name or [(hex, 0-1), ...]
    )
    height: float = 1.0  # peak auto-normalised to this height
    axes: bool = True
    rings: bool = True  # floor contours (radial approximation)
    orbit: bool = True  # 360° orbit
    flip: bool = True  # flip to show the underside
    annotate: bool = True  # peak label
    captions: Optional[Sequence[str]] = None  # captions aligned by slot; omit for none
    duration: Optional[float] = None  # content budget in seconds; None = use pace
    pace: str = "full"  # fast=10 / normal=24 / full=45
    background: str = "#050810"
    camera_phi: float = 72.0
    camera_theta: float = -55.0
    zoom: float = 0.95

    def resolve(self) -> tuple[SurfaceFunction, Optional[str]]:
        """Resolve the surface function and its displayed formula.

        Returns
        -------
            The height function and the formula string, with defaults filled in.
        """

        tex: Optional[str]
        if self.func is None:
            f = lambda x, y: float(np.exp(-(x * x + y * y)))
            tex = r"z = e^{-x^{2}-y^{2}}" if self.func_tex is None else self.func_tex
        else:
            f = self.func
            tex = self.func_tex
        return f, tex


@dataclass
class SaddleSurface:
    """Tunable presentation for the fixed saddle surface :math:`z = x^{2} - y^{2}`.

    Examples
    --------
    .. manim:: SaddleSurfaceConfigScene
       :save_last_frame:

       from manim import *
       from manim_extensions.three_d.core import SaddleSurface, SaddleSurfaceScene

       class SaddleSurfaceConfigScene(SaddleSurfaceScene):
           style = SaddleSurface(height=1.5, annotate=True, pace='fast')
    """

    domain: tuple[float, float] = (-2.2, 2.2)
    resolution: tuple[int, int] = (44, 44)
    colors: str | Sequence[tuple[str, float]] = "rainbow"
    height: float = 1.2  # normalise: ridge = +H, valley = -H (symmetric)
    axes: bool = True
    rings: bool = True  # hyperbola-family contours + asymptotes (floor)
    orbit: bool = True
    flip: bool = True
    annotate: bool = True  # saddle label (projected HUD label)
    captions: Optional[Sequence[str]] = None
    duration: Optional[float] = None
    pace: str = "full"
    background: str = "#050810"
    camera_phi: float = 70.0
    camera_theta: float = -50.0
    zoom: float = 0.95


@dataclass
class ParaboloidSurface:
    """Tunable presentation for the fixed paraboloid :math:`z = x^{2} + y^{2}`.

    Examples
    --------
    .. manim:: ParaboloidSurfaceConfigScene
       :save_last_frame:

       from manim import *
       from manim_extensions.three_d.core import ParaboloidSurface, ParaboloidSurfaceScene

       class ParaboloidSurfaceConfigScene(ParaboloidSurfaceScene):
           style = ParaboloidSurface(height=1.5, annotate=True, pace='fast')
    """

    domain: tuple[float, float] = (-2.2, 2.2)
    resolution: tuple[int, int] = (44, 44)
    colors: str | Sequence[tuple[str, float]] = "rainbow"
    height: float = 1.2  # normalise: rim = H, bottom = 0
    axes: bool = True
    rings: bool = True  # surface-attached concentric contours (follow the flip)
    orbit: bool = True
    flip: bool = True
    annotate: bool = True  # top label (projected HUD label)
    captions: Optional[Sequence[str]] = None
    duration: Optional[float] = None
    pace: str = "full"
    background: str = "#050810"
    camera_phi: float = 70.0
    camera_theta: float = -50.0
    zoom: float = 0.95


@dataclass
class EllipsoidSurface:
    """Configuration for an ellipsoid, the first closed parametric surface.

    Examples
    --------
    .. manim:: EllipsoidSurfaceConfigScene
       :save_last_frame:

       from manim import *
       from manim_extensions.three_d.core import EllipsoidSurface, EllipsoidSurfaceScene

       class EllipsoidSurfaceConfigScene(EllipsoidSurfaceScene):
           style = EllipsoidSurface(pace='fast')
    """

    semi_axes: tuple[float, float, float] = (2.4, 1.6, 1.2)  # (a, b, c) semi-axes
    resolution: tuple[int, int] = (44, 56)  # latitude/longitude mesh density
    colors: str | Sequence[tuple[str, float]] = "rainbow"
    axes: bool = True
    rings: bool = True  # surface-attached horizontal ellipses (follow the flip)
    orbit: bool = True
    flip: bool = True  # closed-surface flip = rotate to the back
    annotate: bool = True  # top vertex label (3D label)
    captions: Optional[Sequence[str]] = None
    duration: Optional[float] = None
    pace: str = "full"
    background: str = "#050810"
    camera_phi: float = 70.0
    camera_theta: float = -50.0
    zoom: float = 0.95


@dataclass
class TorusSurface:
    """Configuration for a torus with a 4:1 major-to-minor radius ratio.

    Examples
    --------
    .. manim:: TorusSurfaceConfigScene
       :save_last_frame:

       from manim import *
       from manim_extensions.three_d.core import TorusSurface, TorusSurfaceScene

       class TorusSurfaceConfigScene(TorusSurfaceScene):
           style = TorusSurface(pace='fast')
    """

    major_radius: float = 2.0  # torus radius R (tube-centre circle)
    minor_radius: float = 0.5  # tube radius r
    resolution: tuple[int, int] = (56, 24)  # (major θ, tube φ) mesh density
    colors: str | Sequence[tuple[str, float]] = "rainbow"
    axes: bool = True
    rings: bool = True  # surface-attached paired horizontal rings (follow the flip)
    orbit: bool = True
    flip: bool = True
    annotate: bool = True  # highest-point label (3D label + antenna)
    captions: Optional[Sequence[str]] = None
    duration: Optional[float] = None
    pace: str = "full"
    background: str = "#050810"
    camera_phi: float = 70.0
    camera_theta: float = -50.0
    zoom: float = 0.95


@dataclass
class HyperboloidOneSheet:
    """Configuration for a one-sheet hyperboloid, recognizable by its waist.

    Examples
    --------
    .. manim:: HyperboloidOneSheetConfigScene
       :save_last_frame:

       from manim import *
       from manim_extensions.three_d.core import HyperboloidOneSheet, HyperboloidOneSheetScene

       class HyperboloidOneSheetConfigScene(HyperboloidOneSheetScene):
           style = HyperboloidOneSheet(pace='fast')
    """

    waist_radius: float = 1.0  # waist radius a (= b)
    z_extent: float = 1.5  # upper/lower truncation ±h
    resolution: tuple[int, int] = (36, 48)  # (z, circumferential) mesh density
    colors: str | Sequence[tuple[str, float]] = "rainbow"
    axes: bool = True
    rings: bool = (
        True  # surface-attached horizontal circle family (including the waist; follows the flip)
    )
    orbit: bool = True
    flip: bool = True
    annotate: bool = True  # waist front label (HUD label, no dashed line)
    captions: Optional[Sequence[str]] = None
    duration: Optional[float] = None
    pace: str = "full"
    background: str = "#050810"
    camera_phi: float = 70.0
    camera_theta: float = -50.0
    zoom: float = 0.95


# These aliases must follow the classes they name: assignment expressions are
# evaluated at import time, unlike annotations postponed by the future import.
SurfaceConfig = Union[
    GaussianSurface,
    SaddleSurface,
    ParaboloidSurface,
    EllipsoidSurface,
    TorusSurface,
    HyperboloidOneSheet,
]
GraphSurfaceConfig = Union[GaussianSurface, SaddleSurface, ParaboloidSurface]
SurfaceConfigClass = Union[
    type[GaussianSurface],
    type[SaddleSurface],
    type[ParaboloidSurface],
    type[EllipsoidSurface],
    type[TorusSurface],
    type[HyperboloidOneSheet],
]


# ---------------- Beat skeleton (shared graph surfaces) ----------------
class GraphSurfaceScene(ThreeDScene):
    """Shared beat skeleton for graph and closed surfaces.

    Subclasses provide a ``style`` configuration and implement the hooks
    ``_geometry``, ``_contours``, ``_feature``, and ``_caption_slots``. Graph
    surfaces use the flat start beat; closed surfaces set ``uses_flat=False``
    so the formation beat inflates the surface with ``GrowFromCenter`` and
    the axes scale uniformly to avoid distortion.

    Parameters
    ----------
    config
        A configuration dataclass instance or a mapping of its fields.
        When omitted, remaining keyword arguments are passed to
        ``config_cls``; a subclass-level ``style`` is kept as-is.
    **kwargs
        Scene constructor arguments (``renderer``, ``camera_class`` ...) or
        configuration fields such as ``pace``, ``duration`` and
        ``captions``.

    Raises
    ------
    TypeError
        If a mapping config or configuration keyword is given to a scene
        without ``config_cls``.

    Examples
    --------
    .. manim:: GraphSurfaceDemo

       from manim import *
       from manim_extensions.three_d.core import GaussianSurfaceScene

       class GraphSurfaceDemo(GaussianSurfaceScene, pace="fast"):
           def construct(self):
               super().construct()
    """

    #: Render style forwarded to the surface configuration.
    style: SurfaceConfig | None = None
    #: Configuration class used to normalise ``config`` mappings.
    config_cls: SurfaceConfigClass | None = None
    #: Whether this surface scene uses a flat parameterisation.
    uses_flat = True

    def __init__(
        self,
        config: SurfaceConfig | dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        scene_keys = {
            "renderer",
            "camera_class",
            "always_update_mobjects",
            "random_seed",
            "skip_animations",
        }
        scene_kwargs: dict[str, Any] = {
            k: v for k, v in kwargs.items() if k in scene_keys
        }
        style_kwargs: dict[str, Any] = {
            k: v for k, v in kwargs.items() if k not in scene_keys
        }
        super().__init__(**scene_kwargs)  # type: ignore[no-untyped-call]
        if config is not None:
            if isinstance(config, dict):
                if self.config_cls is None:
                    raise TypeError("a mapping config requires a scene with config_cls")
                config = self.config_cls(**config)
            self.style = config
        elif style_kwargs:
            if self.config_cls is None:
                raise TypeError(
                    "configuration keywords require a scene with config_cls"
                )
            self.style = self.config_cls(**style_kwargs)
        elif self.style is None and self.config_cls is not None:
            self.style = self.config_cls()

    def __init_subclass__(cls, **config_kwargs: Any) -> None:
        """Apply configuration keywords written in the class statement.

        ``class Demo(GaussianSurfaceScene, pace="fast")`` passes ``pace``
        here; the resulting class keeps a normal class base and receives a
        configured ``style``.  A plain subclass without keywords keeps the
        inherited ``style`` or builds ``config_cls`` with its defaults.

        Parameters
        ----------
        **config_kwargs
            Configuration fields for ``config_cls``, such as ``pace``,
            ``duration`` or ``captions``.

        Raises
        ------
        TypeError
            If configuration keywords are given to a scene without a
            ``config_cls``.
        """
        super().__init_subclass__()
        if config_kwargs:
            if cls.config_cls is None:
                raise TypeError(
                    "configuration keywords require a scene with config_cls"
                )
            cls.style = cls.config_cls(**config_kwargs)

    # ---- hooks ----
    def _geometry(self, cfg: SurfaceConfig) -> GeometrySpec:
        """Return the surface geometry description.

        Parameters
        ----------
        cfg
            Surface configuration.

        Returns
        -------
            A tuple containing the normalized height function, formula string,
            normalized minimum height, and low and high axis limits.

        Raises
        ------
        NotImplementedError
            Always, because subclasses must implement this hook.
        """
        raise NotImplementedError

    def _contours(
        self,
        cfg: SurfaceConfig,
        axes: ThreeDAxes,
        f: SurfaceFunction,
        ramp: ColorRamp,
        zmin_n: float,
    ) -> ContourSpec:
        """Build contour lines for the surface.

        Parameters
        ----------
        cfg
            Surface configuration.
        axes
            Axes used for world-space projection.
        f
            Normalized height function.
        ramp
            Colour ramp.
        zmin_n
            Normalized minimum height.

        Returns
        -------
            A contour group and a flag telling whether it rotates with the
            surface.

        Raises
        ------
        NotImplementedError
            Always, because subclasses must implement this hook.
        """
        raise NotImplementedError

    def _feature(self, cfg: SurfaceConfig, f: SurfaceFunction) -> FeatureSpec:
        """Describe the annotated feature point.

        Parameters
        ----------
        cfg
            Surface configuration.
        f
            Normalized height function.

        Returns
        -------
            The ``x``, ``y`` and ``z`` coordinates of the feature, its tag
            formula, the HUD flag, and the dashed-stem starting height.

        Raises
        ------
        NotImplementedError
            Always, because subclasses must implement this hook.
        """
        raise NotImplementedError

    def _caption_slots(self) -> list[str]:
        """List the caption slots used by this scene.

        Returns
        -------
            Slot names in beat order.
        """
        return ["title", "axes", "flat", "rings", "orbit", "flip", "outro"]

    def _annotate_camera(self) -> tuple[float, float, float]:
        """Return the camera angle used for the annotation beat.

        Returns
        -------
            The ``(phi, theta, zoom)`` triple.
        """
        return 66.0, -40.0, 0.95

    def _make_axes(
        self, cfg: GraphSurfaceConfig, ax_z_lo: float, ax_z_hi: float
    ) -> ThreeDAxes:
        """Build the default graph-surface axes.

        Parameters
        ----------
        cfg
            Surface configuration.
        ax_z_lo
            Lower z axis limit.
        ax_z_hi
            Upper z axis limit.

        Returns
        -------
            The configured axes.
        """

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

    def _make_surface(
        self,
        cfg: GraphSurfaceConfig,
        axes: ThreeDAxes,
        f: SurfaceFunction,
        ramp: ColorRamp,
        zmin_n: float,
    ) -> Surface:
        """Build the default graph surface :math:`z=f(x, y)`.

        Parameters
        ----------
        cfg
            Surface configuration.
        axes
            Axes used for world-space projection.
        f
            Normalized height function.
        ramp
            Colour ramp.
        zmin_n
            Normalized minimum height.

        Returns
        -------
            The coloured surface mobject.
        """

        d0, d1 = cfg.domain
        s = Surface(
            cast(
                Callable[[float, float], Point3D], lambda u, v: axes.c2p(u, v, f(u, v))
            ),
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

    # ---- main flow ----
    def construct(self) -> None:
        """Build and play the full surface presentation.

        Returns
        -------
            The scene beats are played.
        """

        cfg = self.style
        assert cfg is not None
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
                f"[manim_extensions.three_d] {duration}s budget cannot fit every beat; dropping: {', '.join(dropped)}"
            )
        swap_t = min(max(0.9 * duration / 45.0, 0.35), 1.0)
        print(
            "[manim_extensions.three_d] beat budget:",
            ", ".join(f"{k}={v:.1f}s" for k, v in t.items()),
            f"(caption swap {swap_t:.2f}s each)",
        )

        slots = self._caption_slots()
        cap_map = dict(zip(slots, list(cfg.captions) if cfg.captions else []))
        self.camera.background_color = ManimColor(cfg.background)
        self.set_camera_orientation(
            phi=cfg.camera_phi * DEGREES,
            theta=cfg.camera_theta * DEGREES,
            zoom=cfg.zoom,
        )

        # ---------- caption HUD (text + formula VGroup, screen-fixed) ----------
        cur_cap = None

        def make_cap(text: str, tex: Optional[str] = None, live: bool = True) -> VGroup:
            """Build one caption line and optionally register it as HUD.

            Parameters
            ----------
            text
                Plain-language caption text.
            tex
                Optional formula appended after a middle dot.
            live
                When true, add the caption as a fixed-in-frame mobject so it
                stays screen-aligned during camera motion.

            Returns
            -------
                The caption group positioned above the bottom edge.
            """
            if tex:
                text = f"{text} ·" if not text.rstrip().endswith("·") else text.rstrip()
            parts: list[VMobject] = [
                Text(text, font=DEFAULT_CJK_FONT, font_size=42, color="#e8d9a0")
            ]
            if tex:
                parts.append(MathTex(tex, font_size=52, color="#e8d9a0"))
            g = VGroup(*parts).arrange(RIGHT, buff=0.2).to_edge(DOWN, buff=0.55)
            g.set_z_index(50)
            if live:
                self.add_fixed_in_frame_mobjects(
                    g
                )  # registered on entry; caller must self.remove to detach
            return g

        def swap_caption(text: str, tex: Optional[str] = None) -> VGroup:
            """Crossfade the caption line without a Transform.

            Parameters
            ----------
            text
                New caption text.
            tex
                Optional formula appended to the caption.

            Returns
            -------
                ``None`` after playing the fade.
            """

            nonlocal cur_cap
            new_cap = make_cap(text, tex)
            self.remove(new_cap)  # detach to avoid early text; FadeIn adds it back
            if cur_cap is not None:
                self.play(FadeOut(cur_cap), run_time=0.44 * swap_t)
            self.play(FadeIn(new_cap), run_time=0.56 * swap_t)
            cur_cap = new_cap
            return new_cap

        # ---------- geometry ----------
        graph_cfg = cast(GraphSurfaceConfig, cfg)
        axes_obj = self._make_axes(graph_cfg, ax_z_lo, ax_z_hi)
        surface = self._make_surface(graph_cfg, axes_obj, f_n, ramp, zmin_n)

        flat = None
        if self.uses_flat:
            d0, d1 = graph_cfg.domain
            flat = Surface(
                cast(
                    Callable[[float, float], Point3D],
                    lambda u, v: axes_obj.c2p(u, v, 0.001),
                ),
                u_range=(d0, d1),
                v_range=(d0, d1),
                resolution=graph_cfg.resolution,
                fill_opacity=0.95,
                stroke_color="#8899bb",
                stroke_width=0.35,
                stroke_opacity=0.25,
            )
            flat.set_fill_by_value(
                axes=axes_obj,
                colorscale=[("#14304f", zmin_n), ("#27507d", graph_cfg.height)],
                axis=2,
            )

        rings_grp, rings_follow = (VGroup(), False)
        if "rings" in t:
            rings_grp, rings_follow = self._contours(cfg, axes_obj, f_n, ramp, zmin_n)

        feat = self._feature(cfg, f_n) if "annotate" in t else None

        # ---------- corner formula ----------
        formula = None
        if func_tex:
            formula = MathTex(func_tex, font_size=112)
            formula.set_color_by_gradient(BLUE, TEAL, GREEN, YELLOW, ORANGE, RED)
            self.add_fixed_in_frame_mobjects(formula)

        # ================= title =================
        if cap_map.get("title"):
            cur_cap = make_cap(
                cap_map["title"], tex=func_tex
            )  # title card appears directly
        if "title" in t:
            fade = max(0.8, 0.53 * t["title"])
            if formula is not None:
                self.play(FadeIn(formula, shift=UP * 0.5), run_time=fade)
            self.wait(t["title"] - fade)

        # ================= axes =================
        if "axes" in t:
            if cap_map.get("axes"):
                swap_caption(cap_map["axes"])
            anims: list[Animation | _AnimationBuilder] = []
            if formula is not None:
                anims.append(
                    cast(
                        _AnimationBuilder,
                        formula.animate.scale(0.55).to_corner(UR, buff=0.45),
                    )
                )
            anims.append(Create(axes_obj))
            self.play(*anims, run_time=t["axes"])

        # ================= shaping (graph surface: lift plane / closed surface: inflate) =================
        if "flat" in t and flat is not None:
            if cap_map.get("flat"):
                swap_caption(cap_map["flat"])
            self.play(Create(flat), run_time=t["flat"])
        if "rise" in t:
            if flat is not None:
                self.play(
                    Transform(flat, surface), run_time=t["rise"], rate_func=smooth
                )
                surface = flat  # after Transform it is already the target shape
            else:
                self.play(
                    GrowFromCenter(surface), run_time=t["rise"]
                )  # inflate the closed surface

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
            self.begin_ambient_camera_rotation(rate=TAU / spin)  # exactly one full turn
            self.wait(spin)
            self.stop_ambient_camera_rotation()  # type: ignore[no-untyped-call]
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
                # stem_z0 == pz -> no dashed line (waist-type feature point; a vertical line would enter the surface)
                stem = DashedLine(
                    axes_obj.c2p(px, py, stem_z0),
                    axes_obj.c2p(px, py, pz),
                    stroke_width=2.5,
                    color=WHITE,
                )
                stem.set_z_index(60)
            if use_hud:
                # feature point is surrounded by the surface: after the camera settles, project to screen coordinates and pin the label above-right,
                # never covered by the surface depth (the red dot/dashed line stay anchored in 3D).
                proj = self.camera.project_point(axes_obj.c2p(px, py, pz))
                tag = MathTex(tag_tex, font_size=44, color=WHITE).move_to(
                    proj + RIGHT * 1.05 + UP * 0.4
                )
                self.add_fixed_in_frame_mobjects(tag)
            else:
                tag = MathTex(tag_tex, font_size=44, color=WHITE).next_to(
                    dot, RIGHT, buff=0.28
                )
            ann_anims: list[Animation | _AnimationBuilder] = [FadeIn(dot, scale=0.3)]
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
            anims.append(
                cast(_AnimationBuilder, formula.animate.move_to(ORIGIN).scale(1.5))
            )
        self.play(*anims, run_time=f1)
        # cleanup: force-remove any missed objects
        self.remove(*[m for m in list(self.mobjects) if m is not formula])
        if cap_map.get("outro") and cfg.captions and len(list(cfg.captions)) >= 2:
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


# ---------------- three surface scenes ----------------
class GaussianSurfaceScene(GraphSurfaceScene):
    """Animated demo of the Gaussian surface :math:`z=e^{-x^2-y^2}`.

    The scene raises the bell-shaped sheet from a flat plane, projects
    contour rings onto the floor, orbits the camera, flips the surface to
    show its underside, and annotates the peak with a HUD label.

    Examples
    --------
    .. manim:: GaussianSurfacePreview

       from manim import *
       from manim_extensions.three_d.core import GaussianSurfaceScene

       class GaussianSurfacePreview(GaussianSurfaceScene, pace="fast"):
           def construct(self):
               super().construct()
    """

    config_cls = GaussianSurface

    def _geometry(self, cfg: SurfaceConfig) -> GeometrySpec:
        """Sample the Gaussian surface and derive its display range.

        Parameters
        ----------
        cfg
            Gaussian surface configuration.

        Returns
        -------
            The normalized height function, formula string, normalized minimum
            height, and low and high z axis limits.
        """
        cfg = cast(GaussianSurface, cfg)

        f_raw, tex = cfg.resolve()
        n = 160
        gx = np.linspace(cfg.domain[0], cfg.domain[1], n)
        zs = np.array([[f_raw(x, y) for x in gx] for y in gx])
        zmax = max(float(zs.max()), 1e-9)
        zmin = min(0.0, float(zs.min()))
        scale = cfg.height / zmax
        self._gx, self._zs = gx, zs  # for the peak label
        self._stem_z0 = zmin * scale
        f = lambda x, y: f_raw(x, y) * scale
        return f, tex, zmin * scale, min(0.0, zmin * scale), cfg.height * 1.5

    def _contours(
        self,
        cfg: SurfaceConfig,
        axes: ThreeDAxes,
        f: SurfaceFunction,
        ramp: ColorRamp,
        zmin_n: float,
    ) -> ContourSpec:
        """Build the floor-projected contour rings.

        Parameters
        ----------
        cfg
            Gaussian surface configuration.
        axes
            Axes used for world-space projection.
        f
            Normalized height function.
        ramp
            Colour ramp.
        zmin_n
            Normalized minimum height.

        Returns
        -------
            The contour group and ``False`` because these rings stay on the
            floor and do not rotate with the surface.
        """
        cfg = cast(GaussianSurface, cfg)
        g = VGroup()
        for c in [0.8, 0.55, 0.33, 0.15, 0.045]:
            r = _radius_for_level(f, cfg.domain[1], c)
            if r is None:
                continue
            g.add(
                ParametricFunction(
                    cast(
                        Callable[[float], Point3D],
                        lambda tt, r=r: axes.c2p(r * np.cos(tt), r * np.sin(tt), 0.002),
                    ),
                    t_range=(0, TAU),
                    color=_ramp_color(ramp, c),
                    stroke_width=2.0,
                    stroke_opacity=0.65,
                )
            )
        return g, False  # floor projection, does not follow the flip

    def _feature(self, cfg: SurfaceConfig, f: SurfaceFunction) -> FeatureSpec:
        """Locate the peak of the sampled Gaussian surface.

        Parameters
        ----------
        cfg
            Gaussian surface configuration.
        f
            Normalized height function.

        Returns
        -------
            The peak coordinates, tag formula, HUD flag, and stem start height.
        """
        cfg = cast(GaussianSurface, cfg)
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

    def _caption_slots(self) -> list[str]:
        """List the caption slots used by the Gaussian scene.

        Returns
        -------
            Slot names in beat order.
        """
        return ["title", "axes", "flat", "orbit", "flip", "outro"]

    def _annotate_camera(self) -> tuple[float, float, float]:
        """Return the camera angle used for the Gaussian annotation.

        Returns
        -------
            The ``(phi, theta, zoom)`` triple.
        """
        return 68.0, -40.0, 0.95


class SaddleSurfaceScene(GraphSurfaceScene):
    """Animated demo of the saddle surface :math:`z=x^2-y^2`.

    The scene forms the hyperbolic paraboloid, draws its floor-projected
    contour family and asymptotes, orbits and flips the surface, and marks
    the saddle point where the two principal curvatures oppose each other.

    Examples
    --------
    .. manim:: SaddleSurfacePreview

       from manim import *
       from manim_extensions.three_d.core import SaddleSurfaceScene

       class SaddleSurfacePreview(SaddleSurfaceScene, pace="fast"):
           def construct(self):
               super().construct()
    """

    config_cls = SaddleSurface

    def _geometry(self, cfg: SurfaceConfig) -> GeometrySpec:
        """Return the fixed saddle geometry and its display range.

        Parameters
        ----------
        cfg
            Saddle surface configuration.

        Returns
        -------
            The height function, formula string, normalized minimum height, and
            low and high z axis limits.
        """
        cfg = cast(SaddleSurface, cfg)
        d1 = cfg.domain[1]
        scale = cfg.height / (d1 * d1)
        f = lambda x, y: (x * x - y * y) * scale
        return f, r"z = x^{2} - y^{2}", -cfg.height, -cfg.height * 1.3, cfg.height * 1.3

    def _contours(
        self,
        cfg: SurfaceConfig,
        axes: ThreeDAxes,
        f: SurfaceFunction,
        ramp: ColorRamp,
        zmin_n: float,
    ) -> ContourSpec:
        """Build the saddle contour family and its asymptotes.

        Parameters
        ----------
        cfg
            Saddle surface configuration.
        axes
            Axes used for world-space projection.
        f
            Normalized height function.
        ramp
            Colour ramp.
        zmin_n
            Normalized minimum height.

        Returns
        -------
            The contour group and ``False`` because the contours stay on the
            floor.
        """
        cfg = cast(SaddleSurface, cfg)

        d1 = cfg.domain[1]
        H = cfg.height
        g = VGroup()
        # asymptote x=±y (k=0 degenerate contour, saddle signature)
        for s in (+1, -1):
            line = ParametricFunction(
                cast(
                    Callable[[float], Point3D], lambda t, s=s: axes.c2p(t, s * t, 0.003)
                ),
                t_range=(-d1, d1),
                color="#9fb3c8",
                stroke_width=2.0,
                stroke_opacity=0.55,
            )
            g.add(DashedVMobject(line, num_dashes=24))
        # hyperbola family x²-y²=k, two branches, coloured by horizontal level
        for z_lv in [1.0, 0.6, 0.25, -0.25, -0.6, -1.0]:
            k = z_lv * d1 * d1 / H  # original level before normalisation
            col = _ramp_color(ramp, (z_lv - zmin_n) / (H - zmin_n))
            if k > 0:  # x = ±√(k+y²)
                ymax = np.sqrt(d1 * d1 - k)
                for s in (+1, -1):
                    g.add(
                        ParametricFunction(
                            cast(
                                Callable[[float], Point3D],
                                lambda t, k=k, s=s: axes.c2p(
                                    s * np.sqrt(k + t * t), t, 0.002
                                ),
                            ),
                            t_range=(-ymax, ymax),
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
                            cast(
                                Callable[[float], Point3D],
                                lambda t, k=k, s=s: axes.c2p(
                                    t, s * np.sqrt(-k + t * t), 0.002
                                ),
                            ),
                            t_range=(-xmax, xmax),
                            color=col,
                            stroke_width=2.4,
                            stroke_opacity=0.75,
                        )
                    )
        return g, False  # floor contours, do not follow the flip

    def _feature(self, cfg: SurfaceConfig, f: SurfaceFunction) -> FeatureSpec:
        """Return the saddle point annotation.

        Parameters
        ----------
        cfg
            Saddle surface configuration.
        f
            Normalized height function.

        Returns
        -------
            The origin coordinates, tag formula, HUD flag, and stem start
            height.
        """
        cfg = cast(SaddleSurface, cfg)
        return (
            0.0,
            0.0,
            0.0,
            r"(0,\,0,\,0)",
            True,
            -cfg.height * 1.3,
        )  # saddle point: HUD label


class ParaboloidSurfaceScene(GraphSurfaceScene):
    """Animated demo of the paraboloid :math:`z=x^2+y^2`.

    The scene raises the bowl, paints concentric level rings on the surface,
    orbits and flips it, and annotates the vertex at the origin. The radii
    of the concentric rings are derived from the configured height so the contour spacing remains
    stable when the presentation is resized.

    Examples
    --------
    .. manim:: ParaboloidSurfacePreview

       from manim import *
       from manim_extensions.three_d.core import ParaboloidSurfaceScene

       class ParaboloidSurfacePreview(ParaboloidSurfaceScene, pace="fast"):
           def construct(self):
               super().construct()
    """

    config_cls = ParaboloidSurface

    def _geometry(self, cfg: SurfaceConfig) -> GeometrySpec:
        """Return the fixed paraboloid geometry and its display range.

        Parameters
        ----------
        cfg
            Paraboloid surface configuration.

        Returns
        -------
            The height function, formula string, normalized minimum height, and
            low and high z axis limits.
        """
        cfg = cast(ParaboloidSurface, cfg)
        d1 = cfg.domain[1]
        scale = cfg.height / (d1 * d1)
        f = lambda x, y: (x * x + y * y) * scale
        return f, r"z = x^{2} + y^{2}", 0.0, -cfg.height * 0.6, cfg.height * 1.3

    def _contours(
        self,
        cfg: SurfaceConfig,
        axes: ThreeDAxes,
        f: SurfaceFunction,
        ramp: ColorRamp,
        zmin_n: float,
    ) -> ContourSpec:
        """Build the concentric rings painted on the paraboloid.

        Parameters
        ----------
        cfg
            Paraboloid surface configuration.
        axes
            Axes used for world-space projection.
        f
            Normalized height function.
        ramp
            Colour ramp.
        zmin_n
            Normalized minimum height.

        Returns
        -------
            The contour group and ``True`` because these rings follow the
            surface when it flips.
        """
        cfg = cast(ParaboloidSurface, cfg)

        d1 = cfg.domain[1]
        H = cfg.height
        g = VGroup()
        # surface-attached concentric rings (altitude rings): rim high; floor projection is blocked by the near bowl wall.
        # radius of the z_lv circle r = D·√(z_lv/H), raised by 0.004 to avoid z-fighting.
        for z_lv in [1.0, 0.7, 0.45, 0.25]:
            r = d1 * np.sqrt(z_lv / H)
            g.add(
                ParametricFunction(
                    cast(
                        Callable[[float], Point3D],
                        lambda t, r=r, z_lv=z_lv: axes.c2p(
                            r * np.cos(t), r * np.sin(t), z_lv + 0.004
                        ),
                    ),
                    t_range=(0, TAU),
                    color=_ramp_color(ramp, z_lv / H),
                    stroke_width=2.6,
                    stroke_opacity=0.85,
                )
            )
        return g, True  # attached to the surface; the flip must rotate with it

    def _feature(self, cfg: SurfaceConfig, f: SurfaceFunction) -> FeatureSpec:
        """Return the paraboloid vertex annotation.

        Parameters
        ----------
        cfg
            Paraboloid surface configuration.
        f
            Normalized height function.

        Returns
        -------
            The origin coordinates, tag formula, HUD flag, and stem start
            height.
        """
        cfg = cast(ParaboloidSurface, cfg)
        return (
            0.0,
            0.0,
            0.0,
            r"(0,\,0,\,0)",
            True,
            -cfg.height * 0.6,
        )  # top vertex: HUD label


class EllipsoidSurfaceScene(GraphSurfaceScene):
    """Ellipsoid scene with an inflated formation and uniformly scaled axes.

    Examples
    --------
    .. manim:: EllipsoidSurfacePreview

       from manim import *
       from manim_extensions.three_d.core import EllipsoidSurfaceScene

       class EllipsoidSurfacePreview(EllipsoidSurfaceScene, pace="fast"):
           def construct(self):
               super().construct()
    """

    #: Whether this surface scene uses a flat parameterisation.
    uses_flat = False

    config_cls = EllipsoidSurface

    def _geometry(self, cfg: SurfaceConfig) -> GeometrySpec:
        """Return the ellipsoid formula and display range.

        Parameters
        ----------
        cfg
            Ellipsoid configuration.

        Returns
        -------
            A placeholder height function, the formula string, normalized
            minimum height, and low and high z axis limits.
        """
        cfg = cast(EllipsoidSurface, cfg)
        a, b, c = cfg.semi_axes
        f = lambda x, y: 0.0  # closed surfaces skip graph construction; placeholder
        tex = (
            rf"\frac{{x^{{2}}}}{{{_fmt(a)}^{{2}}}} + "
            rf"\frac{{y^{{2}}}}{{{_fmt(b)}^{{2}}}} + "
            rf"\frac{{z^{{2}}}}{{{_fmt(c)}^{{2}}}} = 1"
        )
        return f, tex, -c, -c - 0.5, c + 0.9

    def _make_axes(
        self, cfg: SurfaceConfig, ax_z_lo: float, ax_z_hi: float
    ) -> ThreeDAxes:
        """Scale the axes uniformly so the ellipsoid does not distort.

        Parameters
        ----------
        cfg
            Ellipsoid configuration.
        ax_z_lo
            Lower z axis limit.
        ax_z_hi
            Upper z axis limit.

        Returns
        -------
            The uniformly scaled axes.
        """
        cfg = cast(EllipsoidSurface, cfg)
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

    def _make_surface(
        self,
        cfg: SurfaceConfig,
        axes: ThreeDAxes,
        f: SurfaceFunction,
        ramp: ColorRamp,
        zmin_n: float,
    ) -> Surface:
        """Build the parametric ellipsoid surface.

        Parameters
        ----------
        cfg
            Ellipsoid configuration.
        axes
            Axes used for world-space projection.
        f
            Placeholder height function, unused for closed surfaces.
        ramp
            Colour ramp.
        zmin_n
            Normalized minimum height, unused here.

        Returns
        -------
            The coloured ellipsoid surface.
        """
        cfg = cast(EllipsoidSurface, cfg)
        a, b, c = cfg.semi_axes
        s = Surface(
            cast(
                Callable[[float, float], Point3D],
                lambda u, v: axes.c2p(
                    a * np.sin(u) * np.cos(v), b * np.sin(u) * np.sin(v), c * np.cos(u)
                ),
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

    def _contours(
        self,
        cfg: SurfaceConfig,
        axes: ThreeDAxes,
        f: SurfaceFunction,
        ramp: ColorRamp,
        zmin_n: float,
    ) -> ContourSpec:
        """Build the latitude rings painted on the ellipsoid.

        Parameters
        ----------
        cfg
            Ellipsoid configuration.
        axes
            Axes used for world-space projection.
        f
            Placeholder height function, unused here.
        ramp
            Colour ramp.
        zmin_n
            Normalized minimum height, unused here.

        Returns
        -------
            The contour group and ``True`` because the rings rotate with the
            surface.
        """
        cfg = cast(EllipsoidSurface, cfg)
        a, b, c = cfg.semi_axes
        g = VGroup()
        for h in [0.66, 0.33, 0.0, -0.33, -0.66]:  # z/c height ratio
            z0 = c * h
            s = (
                np.sqrt(max(1.0 - h * h, 0.0)) * 1.005
            )  # slight offset to avoid z-fighting
            g.add(
                ParametricFunction(
                    cast(
                        Callable[[float], Point3D],
                        lambda t, s=s, z0=z0: axes.c2p(
                            a * s * np.cos(t), b * s * np.sin(t), z0
                        ),
                    ),
                    t_range=(0, TAU),
                    color=_ramp_color(ramp, (z0 + c) / (2 * c)),
                    stroke_width=2.6,
                    stroke_opacity=0.85,
                )
            )
        return g, True  # surface-attached ring, follows the flip

    def _feature(self, cfg: SurfaceConfig, f: SurfaceFunction) -> FeatureSpec:
        """Return the ellipsoid apex annotation.

        Parameters
        ----------
        cfg
            Ellipsoid configuration.
        f
            Normalized height function, unused here.

        Returns
        -------
            The apex coordinates, tag formula, HUD flag, and stem start height.
        """
        cfg = cast(EllipsoidSurface, cfg)
        a, b, c = cfg.semi_axes
        # top vertex exposed; a 3D label suffices; dashed line from above (below the vertex is inside the surface and occluded)
        return 0.0, 0.0, c, rf"(0,\,0,\,{_fmt(c)})", False, c + 0.75


class TorusSurfaceScene(GraphSurfaceScene):
    """Torus scene with an inflated formation and uniformly scaled axes.

    Examples
    --------
    .. manim:: TorusSurfacePreview

       from manim import *
       from manim_extensions.three_d.core import TorusSurfaceScene

       class TorusSurfacePreview(TorusSurfaceScene, pace="fast"):
           def construct(self):
               super().construct()
    """

    #: Whether this surface scene uses a flat parameterisation.
    uses_flat = False

    config_cls = TorusSurface

    def _geometry(self, cfg: SurfaceConfig) -> GeometrySpec:
        """Return the torus formula and display range.

        Parameters
        ----------
        cfg
            Torus configuration.

        Returns
        -------
            A placeholder height function, the formula string, normalized
            minimum height, and low and high z axis limits.
        """
        cfg = cast(TorusSurface, cfg)
        R, r = cfg.major_radius, cfg.minor_radius
        f = lambda x, y: 0.0  # closed surfaces skip graph construction; placeholder
        tex = rf"(\sqrt{{x^{{2}}+y^{{2}}}} - {_fmt(R)})^{{2}} + z^{{2}} = {_fmt(r * r)}"
        return f, tex, -r, -r - 0.4, r + 0.9

    def _make_axes(
        self, cfg: SurfaceConfig, ax_z_lo: float, ax_z_hi: float
    ) -> ThreeDAxes:
        """Scale the axes uniformly for the torus.

        Parameters
        ----------
        cfg
            Torus configuration.
        ax_z_lo
            Lower z axis limit.
        ax_z_hi
            Upper z axis limit.

        Returns
        -------
            The uniformly scaled axes.
        """
        cfg = cast(TorusSurface, cfg)
        R, r = cfg.major_radius, cfg.minor_radius
        outer = R + r
        k = 7.2 / (
            2 * (outer + 0.4)
        )  # x scale; y/z use the same ratio to avoid distortion
        axes = ThreeDAxes(
            x_range=[-outer - 0.4, outer + 0.4, 1],
            y_range=[-outer - 0.4, outer + 0.4, 1],
            z_range=[ax_z_lo, ax_z_hi, r / 2],
            x_length=7.2,
            y_length=7.2,
            z_length=(ax_z_hi - ax_z_lo) * k,
        )
        return axes.set_stroke(opacity=0.55)

    def _make_surface(
        self,
        cfg: SurfaceConfig,
        axes: ThreeDAxes,
        f: SurfaceFunction,
        ramp: ColorRamp,
        zmin_n: float,
    ) -> Surface:
        """Build the parametric torus surface.

        Parameters
        ----------
        cfg
            Torus configuration.
        axes
            Axes used for world-space projection.
        f
            Placeholder height function, unused for closed surfaces.
        ramp
            Colour ramp.
        zmin_n
            Normalized minimum height, unused here.

        Returns
        -------
            The coloured torus surface.
        """
        cfg = cast(TorusSurface, cfg)
        R, r = cfg.major_radius, cfg.minor_radius
        s = Surface(
            cast(
                Callable[[float, float], Point3D],
                lambda u, v: axes.c2p(
                    (R + r * np.cos(v)) * np.cos(u),
                    (R + r * np.cos(v)) * np.sin(u),
                    r * np.sin(v),
                ),
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

    def _contours(
        self,
        cfg: SurfaceConfig,
        axes: ThreeDAxes,
        f: SurfaceFunction,
        ramp: ColorRamp,
        zmin_n: float,
    ) -> ContourSpec:
        """Build the horizontal rings cut from the torus.

        Parameters
        ----------
        cfg
            Torus configuration.
        axes
            Axes used for world-space projection.
        f
            Placeholder height function, unused here.
        ramp
            Colour ramp.
        zmin_n
            Normalized minimum height, unused here.

        Returns
        -------
            The contour group and ``True`` because the rings rotate with the
            surface.
        """
        cfg = cast(TorusSurface, cfg)
        R, r = cfg.major_radius, cfg.minor_radius
        g = VGroup()
        for z_lv in [0.6, 0.0, -0.6]:  # tube cross-section height ratio (×r)
            z0 = r * z_lv
            half = np.sqrt(max(r * r - z0 * z0, 0.0))
            for sgn in (+1, -1):  # horizontal section cuts outer/inner branches
                rho = (R + sgn * half) * 1.004  # slight offset to avoid z-fighting
                g.add(
                    ParametricFunction(
                        cast(
                            Callable[[float], Point3D],
                            lambda t, rho=rho, z0=z0: axes.c2p(
                                rho * np.cos(t), rho * np.sin(t), z0
                            ),
                        ),
                        t_range=(0, TAU),
                        color=_ramp_color(ramp, (z0 + r) / (2 * r)),
                        stroke_width=2.6,
                        stroke_opacity=0.85,
                    )
                )
        return g, True  # surface-attached ring, follows the flip

    def _feature(self, cfg: SurfaceConfig, f: SurfaceFunction) -> FeatureSpec:
        """Return the torus apex annotation.

        Parameters
        ----------
        cfg
            Torus configuration.
        f
            Normalized height function, unused here.

        Returns
        -------
            The apex coordinates, tag formula, HUD flag, and stem start height.
        """
        cfg = cast(TorusSurface, cfg)
        R, r = cfg.major_radius, cfg.minor_radius
        # highest point exposed; 3D label; antenna line hangs from above (other directions are inside the surface/hole)
        return 0.0, 0.0, r, rf"(0,\,0,\,{_fmt(r)})", False, r + 0.75


class HyperboloidOneSheetScene(GraphSurfaceScene):
    """One-sheet hyperboloid scene with an inflated formation.

    Examples
    --------
    .. manim:: HyperboloidOneSheetPreview

       from manim import *
       from manim_extensions.three_d.core import HyperboloidOneSheetScene

       class HyperboloidOneSheetPreview(HyperboloidOneSheetScene, pace="fast"):
           def construct(self):
               super().construct()
    """

    #: Whether this surface scene uses a flat parameterisation.
    uses_flat = False

    config_cls = HyperboloidOneSheet

    def _geometry(self, cfg: SurfaceConfig) -> GeometrySpec:
        """Return the hyperboloid formula and display range.

        Parameters
        ----------
        cfg
            Hyperboloid configuration.

        Returns
        -------
            A placeholder height function, the formula string, normalized
            minimum height, and low and high z axis limits.
        """
        cfg = cast(HyperboloidOneSheet, cfg)
        a, h = cfg.waist_radius, cfg.z_extent
        f = (
            lambda x, y: 0.0
        )  # closed tube surface skips graph construction; placeholder
        rhs = "1" if abs(a * a - 1.0) < 1e-9 else _fmt(a * a)
        tex = rf"x^{{2}} + y^{{2}} - z^{{2}} = {rhs}"
        return f, tex, -h, -h - 0.4, h + 0.4

    def _make_axes(
        self, cfg: SurfaceConfig, ax_z_lo: float, ax_z_hi: float
    ) -> ThreeDAxes:
        """Scale the axes uniformly for the hyperboloid.

        Parameters
        ----------
        cfg
            Hyperboloid configuration.
        ax_z_lo
            Lower z axis limit.
        ax_z_hi
            Upper z axis limit.

        Returns
        -------
            The uniformly scaled axes.
        """
        cfg = cast(HyperboloidOneSheet, cfg)
        a, h = cfg.waist_radius, cfg.z_extent
        max_r = (a * a + h * h) ** 0.5  # port radius
        k = 7.2 / (
            2 * (max_r + 0.4)
        )  # x scale; y/z use the same ratio to avoid distortion
        axes = ThreeDAxes(
            x_range=[-max_r - 0.4, max_r + 0.4, 1],
            y_range=[-max_r - 0.4, max_r + 0.4, 1],
            z_range=[ax_z_lo, ax_z_hi, h / 2],
            x_length=7.2,
            y_length=7.2,
            z_length=(ax_z_hi - ax_z_lo) * k,
        )
        return axes.set_stroke(opacity=0.55)

    def _make_surface(
        self,
        cfg: SurfaceConfig,
        axes: ThreeDAxes,
        f: SurfaceFunction,
        ramp: ColorRamp,
        zmin_n: float,
    ) -> Surface:
        """Build the parametric one-sheet hyperboloid surface.

        Parameters
        ----------
        cfg
            Hyperboloid configuration.
        axes
            Axes used for world-space projection.
        f
            Placeholder height function, unused for closed surfaces.
        ramp
            Colour ramp.
        zmin_n
            Normalized minimum height, unused here.

        Returns
        -------
            The coloured hyperboloid surface.
        """
        cfg = cast(HyperboloidOneSheet, cfg)
        a, h = cfg.waist_radius, cfg.z_extent
        s = Surface(
            cast(
                Callable[[float, float], Point3D],
                lambda u, v: axes.c2p(
                    (a * a + u * u) ** 0.5 * np.cos(v),
                    (a * a + u * u) ** 0.5 * np.sin(v),
                    u,
                ),
            ),  # u is z
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

    def _contours(
        self,
        cfg: SurfaceConfig,
        axes: ThreeDAxes,
        f: SurfaceFunction,
        ramp: ColorRamp,
        zmin_n: float,
    ) -> ContourSpec:
        """Build the horizontal circle family of the hyperboloid.

        Parameters
        ----------
        cfg
            Hyperboloid configuration.
        axes
            Axes used for world-space projection.
        f
            Placeholder height function, unused here.
        ramp
            Colour ramp.
        zmin_n
            Normalized minimum height, unused here.

        Returns
        -------
            The contour group and ``True`` because the rings rotate with the
            surface.
        """
        cfg = cast(HyperboloidOneSheet, cfg)
        a, h = cfg.waist_radius, cfg.z_extent
        g = VGroup()
        for z_lv in [1.0, 0.5, 0.0, -0.5, -1.0]:  # horizontal circle family (0 = waist)
            if abs(z_lv) > h * 0.95:
                continue
            rho = (
                (a * a + z_lv * z_lv) ** 0.5
            ) * 1.004  # slight offset to avoid z-fighting
            g.add(
                ParametricFunction(
                    cast(
                        Callable[[float], Point3D],
                        lambda t, rho=rho, z_lv=z_lv: axes.c2p(
                            rho * np.cos(t), rho * np.sin(t), z_lv
                        ),
                    ),
                    t_range=(0, TAU),
                    color=_ramp_color(ramp, (z_lv + h) / (2 * h)),
                    stroke_width=2.6,
                    stroke_opacity=0.85,
                )
            )
        return g, True  # surface-attached ring, follows the flip

    def _feature(self, cfg: SurfaceConfig, f: SurfaceFunction) -> FeatureSpec:
        """Return the waist point annotation.

        Parameters
        ----------
        cfg
            Hyperboloid configuration.
        f
            Normalized height function, unused here.

        Returns
        -------
            The waist point coordinates, tag formula, HUD flag, and stem start
            height.
        """
        cfg = cast(HyperboloidOneSheet, cfg)
        a, h = cfg.waist_radius, cfg.z_extent
        # waist front point (a,0,0): both ends of a vertical line enter the surface; no dashed line; point + HUD label
        return a, 0.0, 0.0, rf"({_fmt(a)},\,0,\,0)", True, 0.0

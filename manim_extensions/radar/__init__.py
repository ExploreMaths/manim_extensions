# SPDX-FileCopyrightText: 2026 FTZ-OPUS
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""``manim-radar`` — animated radar (spider) charts for Manim.

Provides radar chart construction, reveal and morph animations, comparison
reels, colour themes, numeric displays, and camera helpers.  The reference
page carries the rendered usage examples.
"""

from __future__ import annotations

__version__ = "0.1.2"

from .animations import (
    TRANSITIONS as _TRANSITIONS,
    GlitchFlash,
    RadarBurstIn,
    RadarFade,
    RadarMorph,
    RadarReveal,
    Shockwave,
)
from .backdrop import DeepSpace, set_scene_background
from .camera import CameraRig
from .chart import RadarChart
from .config import STYLES as _STYLES, RadarConfig, get_style, style_names
from .data import RadarData
from .numbers import RollingNumber
from .overflow import OverflowRadarChart
from .poly import PolyMorph, PolyRadarChart
from .reel import RadarReel
from .theme import THEMES as _THEMES, RadarTheme, get_theme, theme_names
from .utils import ease_in_out_cubic, ease_out_back, ease_out_overshoot, mix, pick_font

#: Named transition presets understood by :meth:`~manim_extensions.radar.chart.RadarChart.morph_to`.
TRANSITIONS = _TRANSITIONS
#: Bundled radar style presets keyed by style name.
STYLES = _STYLES
#: Bundled radar colour themes keyed by theme name.
THEMES = _THEMES

__all__ = [
    "__version__",
    # core
    "RadarChart",
    "OverflowRadarChart",
    "PolyRadarChart",
    "PolyMorph",
    "RadarData",
    "RadarConfig",
    "RadarTheme",
    # animations
    "RadarMorph",
    "RadarReveal",
    "RadarBurstIn",
    "RadarFade",
    "Shockwave",
    "GlitchFlash",
    "TRANSITIONS",
    # helpers
    "RadarReel",
    "CameraRig",
    "DeepSpace",
    "RollingNumber",
    "set_scene_background",
    # presets & utilities
    "STYLES",
    "THEMES",
    "get_style",
    "get_theme",
    "style_names",
    "theme_names",
    "mix",
    "pick_font",
    "ease_in_out_cubic",
    "ease_out_back",
    "ease_out_overshoot",
]

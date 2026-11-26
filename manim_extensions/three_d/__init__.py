# SPDX-FileCopyrightText: 2026 FTZ-OPUS
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Utilities for the package module."""

from __future__ import annotations

# -*- coding: utf-8 -*-
"""Manim 3D geometry and animation utilities with tube surfaces and graph surfaces."""

from .core import (
    GaussianSurface,
    SaddleSurface,
    ParaboloidSurface,
    EllipsoidSurface,
    TorusSurface,
    HyperboloidOneSheet,
    GraphSurfaceScene,
    GaussianSurfaceScene,
    SaddleSurfaceScene,
    ParaboloidSurfaceScene,
    EllipsoidSurfaceScene,
    TorusSurfaceScene,
    HyperboloidOneSheetScene,
    plan_timeline,
    RAMPS as _RAMPS,
    PACE as _PACE,
)

#: Named colour ramps used to colour the timeline.
RAMPS = _RAMPS
#: Per-pace total duration in seconds for the timeline.
PACE = _PACE

__version__ = "0.1.1"
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
    "__version__",
]

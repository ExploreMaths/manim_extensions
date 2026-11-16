# SPDX-FileCopyrightText: 2026 FTZ-OPUS
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Small helpers shared across :mod:`manim_extensions.radar`."""

from __future__ import annotations

import math
from typing import Iterable, Optional, Sequence

import numpy as np
from manim import ManimColor, ParsableManimColor, WHITE, interpolate_color

__all__ = [
    "unit_vector",
    "axis_angles",
    "mix",
    "lighten",
    "ease_in_out_cubic",
    "ease_out_back",
    "ease_out_overshoot",
    "pick_font",
    "closed",
]


def unit_vector(degrees: float) -> np.ndarray:
    """Return a unit vector for an angle in degrees.

    Parameters
    ----------
    degrees
        Angle measured counter-clockwise from the positive x axis.

    Returns
    -------
    Cosine and sine of the angle, with a zero z component.
    """

    r = math.radians(degrees)
    return np.array([math.cos(r), math.sin(r), 0.0])


def axis_angles(
    count: int, start: float = 90.0, clockwise: bool = False
) -> list[float]:
    """Build evenly spaced axis angles in degrees.

    Parameters
    ----------
    count
        Number of axes.
    start
        Angle of the first axis in degrees.
    clockwise
        Whether axes run clockwise instead of counter-clockwise.

    Returns
    -------
    One angle in degrees for each axis.
    """
    step = 360.0 / count
    sign = -1.0 if clockwise else 1.0
    return [start + sign * step * i for i in range(count)]


def mix(a: ParsableManimColor, b: ParsableManimColor, t: float) -> ManimColor:
    """Blend two colours linearly.

    Parameters
    ----------
    a
        Colour at :math:`t=0`.
    b
        Colour at :math:`t=1`.
    t
        Blend factor, clipped to the range 0 to 1.

    Returns
    -------
    The blended colour.
    """

    return interpolate_color(ManimColor(a), ManimColor(b), float(np.clip(t, 0.0, 1.0)))


def lighten(color: ParsableManimColor, amount: float = 0.08) -> ManimColor:
    """Push a colour towards white.

    Parameters
    ----------
    color
        Base colour.
    amount
        Blend amount towards white.

    Returns
    -------
    The lightened colour.
    """

    return mix(color, WHITE, amount)


def ease_in_out_cubic(t: float) -> float:
    """Apply a cubic ease-in-out curve.

    Parameters
    ----------
    t
        Normalized time, clipped to the range 0 to 1.

    Returns
    -------
    Eased progress in the range 0 to 1.
    """

    t = float(np.clip(t, 0.0, 1.0))
    if t < 0.5:
        return 4.0 * t * t * t
    return 1.0 - (-2.0 * t + 2.0) ** 3 / 2.0


def ease_out_back(t: float, overshoot: float = 1.2) -> float:
    """Apply an ease-out curve with a controllable overshoot.

    Parameters
    ----------
    t
        Normalized time, clipped to the range 0 to 1.
    overshoot
        Back constant controlling how far the curve overshoots.

    Returns
    -------
    Eased progress.
    """

    t = float(np.clip(t, 0.0, 1.0))
    c1 = overshoot
    c3 = c1 + 1.0
    return 1.0 + c3 * (t - 1.0) ** 3 + c1 * (t - 1.0) ** 2


def ease_out_overshoot(t: float, fraction: float = 0.16) -> float:
    """Apply an ease-out whose peak overshoots by a fraction of the span.

    Used by the burst transition so overflowing spikes visibly pierce the
    outer ring before settling.

    Parameters
    ----------
    t
        Normalized time, clipped to the range 0 to 1.
    fraction
        Peak overshoot as a fraction of the total span.

    Returns
    -------
    Eased progress, temporarily above 1 near the peak.
    """
    t = float(np.clip(t, 0.0, 1.0))
    p = min(0.9, max(1e-4, float(fraction)))
    # solve 4c^3 = 27 f (c+1)^2 for the back constant c (peak = 1 + f);
    # bisection is immune to the Newton divergence at large f
    lo, hi = 0.0, 30.0
    for _ in range(48):
        mid = 0.5 * (lo + hi)
        if 4.0 * mid**3 - 27.0 * p * (mid + 1.0) ** 2 < 0.0:
            lo = mid
        else:
            hi = mid
    c = 0.5 * (lo + hi)
    return ease_out_back(t, overshoot=c)


_FONT_CACHE: dict[tuple, Optional[str]] = {}


def pick_font(
    candidates: Sequence[str], default: Optional[str] = None
) -> Optional[str]:
    """Return the first installed font from a candidate list.

    This lets the library look right on macOS, Windows and Linux without
    hard-coding a platform-specific family.

    Parameters
    ----------
    candidates
        Font families to test in order.
    default
        Name returned when none of the candidates is installed.

    Returns
    -------
    The selected family name, or ``None`` when nothing matches.
    """
    key = tuple(candidates) + (default,)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]

    available: set[str] = set()
    try:  # pragma: no cover - depends on the host system
        import manimpango

        available = set(manimpango.list_fonts())
    except Exception:
        available = set()

    found = next((name for name in candidates if name in available), None)
    if found is None and default is not None and default not in candidates:
        found = default
    _FONT_CACHE[key] = found
    return found


def closed(points: np.ndarray) -> np.ndarray:
    """Close a polygon path by appending its first point.

    Parameters
    ----------
    points
        Open polygon points.

    Returns
    -------
    The polygon with its first point repeated at the end.
    """

    return np.vstack([points, points[:1]])


def as_points(values: Iterable) -> np.ndarray:
    """Coerce 2D or 3D points into a float array with three columns.

    Parameters
    ----------
    values
        Iterable of points, each with two or three coordinates.

    Returns
    -------
    A float array with one row per point and a zero z where needed.
    """

    return np.array(
        [
            np.pad(np.asarray(v, dtype=float), (0, 3 - np.asarray(v).size))
            for v in values
        ],
        dtype=float,
    )

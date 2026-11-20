# SPDX-FileCopyrightText: 2026 FTZ-OPUS
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""The data model: one radar snapshot."""

from __future__ import annotations
from typing import Any, Optional, Sequence, Union

import math
from dataclasses import dataclass, field, replace

from manim import ManimColor

__all__ = ["RadarData"]

_EMPHASIS = ("zoom", "gap", "rim")


@dataclass(frozen=True)
class RadarData:
    """One radar snapshot: the axis names plus the value on each axis.

    Parameters
    ----------
    axes:
        Axis labels, e.g. ``("Speed", "Power", "Range")``. Length must match
        ``values`` and be at least 3.
    values:
        Value per axis, all ``>= 0``.
    name:
        Optional dataset name, drawn as a nameplate above the chart and morphed
        on every transition.
    color:
        Main colour of the polygon. ``None`` -> cycle through the theme palette.
    max_value:
        Full-scale value of this snapshot. Defaults to ``max(values)`` rounded
        up; values above it are shown with ``config.overflow_suffix`` (``"10+"``).
    rim:
        Draw the orange/cyan double outline (emphasis).
    emphasis:
        ``None`` | ``"zoom"`` (heavy zoom transition into this snapshot) |
        ``"gap"`` (fade to black, then glitch back in) | ``"rim"`` (same as
        ``rim=True``, handy in inline lists).
    hold:
        Seconds to hold after morphing to this snapshot (:class:`~manim_extensions.radar.reel.RadarReel` only).
    transition:
        Per-snapshot transition override, see :meth:`~manim_extensions.radar.chart.RadarChart.morph_to`.
    note:
        Free-form text (ignored by the chart itself, useful for the reel).
    """

    axes: Sequence[str]
    values: Sequence[float]
    name: Optional[str] = None
    color: Optional[str] = None
    max_value: Optional[float] = None
    rim: bool = False
    emphasis: Optional[str] = None
    hold: Optional[float] = None
    transition: Optional[str] = None
    note: Optional[str] = None
    meta: dict[Any, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate the snapshot and freeze its sequences.

        Raises
        ------
        ValueError
            If axes and values differ in length, fewer than three axes are
            supplied, a value is negative, the emphasis name is unknown, or
            the full scale is not positive.
        """

        axes = tuple(self.axes)
        values = tuple(float(v) for v in self.values)
        object.__setattr__(self, "axes", axes)
        object.__setattr__(self, "values", values)

        if len(axes) != len(values):
            raise ValueError(
                f"axes and values must have the same length "
                f"({len(axes)} axes vs {len(values)} values)"
            )
        if len(axes) < 3:
            raise ValueError("a radar chart needs at least 3 axes")
        if any(v < 0 for v in values):
            raise ValueError(f"values must be >= 0, got {values}")
        if self.emphasis is not None and self.emphasis not in _EMPHASIS:
            raise ValueError(
                f"emphasis must be one of {_EMPHASIS} or None, got {self.emphasis!r}"
            )
        if self.max_value is not None and self.max_value <= 0:
            raise ValueError("max_value must be > 0")

    # ------------------------------------------------------------------
    @property
    def n_axes(self) -> int:
        """Return the number of axes in this snapshot.

        Returns
        -------
            Number of axis labels.
        """

        return len(self.axes)

    @property
    def overflow_suffix(self) -> str:
        """Report whether any value exceeds the full scale.

        Returns
        -------
            ``"+"`` when a value overflows, otherwise an empty string.
        """

        return "+" if max(self.values) > self.full_scale else ""

    @property
    def full_scale(self) -> float:
        """Return the full-scale value of this snapshot.

        Returns
        -------
            ``max_value`` when supplied, otherwise the ceiling of the largest
            value with a floor of one.
        """

        if self.max_value is not None:
            return float(self.max_value)
        return float(max(1.0, math.ceil(max(self.values))))

    def scale_for(self, levels: int = 5) -> float:
        """Snap the full scale so grid labels are round numbers.

        Parameters
        ----------
        levels
            Number of grid rings; the scale becomes a multiple of this value.

        Returns
        -------
            A scale that labels every ring with an integer.
        """

        if self.max_value is not None:
            return float(self.max_value)
        levels = max(1, int(levels))
        top = max(self.values)
        if top <= 0:
            return 1.0
        if top >= levels:
            return float(levels * math.ceil(top / levels))
        return float(levels)

    def ratios(self, scale: Optional[float] = None) -> list[float]:
        """Express values as fractions of the full scale.

        Parameters
        ----------
        scale
            Optional explicit scale; defaults to :attr:`~manim_extensions.radar.data.RadarData.full_scale`.

        Returns
        -------
            One fraction per axis, where 1.0 is the outer ring.
        """

        sc = float(scale if scale is not None else self.full_scale) or 1.0
        return [v / sc for v in self.values]

    def radius_values(
        self, radius: float, scale: Optional[float] = None
    ) -> list[float]:
        """Convert values to scene-unit radii.

        Parameters
        ----------
        radius
            Scene-unit radius of the outer ring.
        scale
            Optional explicit scale; defaults to :attr:`~manim_extensions.radar.data.RadarData.full_scale`.

        Returns
        -------
            One radius per axis.
        """

        return [r * radius for r in self.ratios(scale)]

    def color_or(self, fallback: Union[str, ManimColor]) -> ManimColor:
        """Resolve the polygon colour for this snapshot.

        Parameters
        ----------
        fallback
            Colour used when :attr:`~manim_extensions.radar.data.RadarData.color` is unset.

        Returns
        -------
            The snapshot colour or the fallback as a Manim colour.
        """

        return ManimColor(self.color) if self.color else ManimColor(fallback)

    def with_values(self, values: Sequence[float], **changes: Any) -> "RadarData":
        """Copy this snapshot with new values and optional other changes.

        Parameters
        ----------
        values
            Replacement values, one per axis.
        changes
            Additional dataclass fields to replace.

        Returns
        -------
            A new validated snapshot.
        """

        return replace(self, values=tuple(float(v) for v in values), **changes)

    def renamed(self, name: Optional[str]) -> "RadarData":
        """Copy this snapshot with another dataset name.

        Parameters
        ----------
        name
            Replacement name, or ``None`` to clear it.

        Returns
        -------
            A new validated snapshot.
        """

        return replace(self, name=name)

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        """Return a compact debug representation.

        Returns
        -------
            A short string naming the axis count, optional name and values.
        """

        label = f" name={self.name!r}" if self.name else ""
        return f"RadarData(axes={len(self.axes)}d{label}, values={tuple(self.values)})"

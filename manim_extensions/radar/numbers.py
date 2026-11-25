# SPDX-FileCopyrightText: 2026 FTZ-OPUS
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Odometer style value numbers (the "rolling digits" used by style ``neo``)."""

from __future__ import annotations
from typing import Any, Optional, cast

import math

from manim.utils.color import ParsableManimColor

import numpy as np
from manim import DOWN, LEFT, RIGHT, UP, ManimColor, Text, VGroup

__all__ = ["RollingNumber"]


class RollingNumber(VGroup):
    """A value read-out that rolls like a mechanical counter.

    Instead of rebuilding a ``Text`` on every frame, all needed integers are
    rendered **lazily once** and kept in a cache; the current value then only
    moves / fades two of them. That makes it cheap enough to drive from an
    updater at 60 fps.

    Parameters
    ----------
    font
        Font family, or ``None`` for Manim's default.
    size
        Font size in points.
    color
        Default glyph colour.
    decimals
        Number of fractional digits.
    template
        Format string applied to the rounded value.
    max_value
        Full scale above which the suffix is appended.
    suffix
        Overflow suffix.
    roll_height
        Wheel travel as a fraction of the chart unit.
    mode
        ``"roll"``, ``"swap"``, or ``"off"``.
    weight
        Font weight.
    kwargs
        Further keyword arguments forwarded to
        :class:`~manim.mobject.types.vectorized_mobject.VGroup`.

    Examples
    --------
    .. manim:: RollingNumberScene
       :save_last_frame:

       from manim import *
       from manim_extensions.radar.numbers import RollingNumber

       class RollingNumberScene(Scene):
           def construct(self):
               number = RollingNumber()
               self.add(number)
               number.render(6.5, ORIGIN)
    """

    def __init__(
        self,
        *,
        font: Optional[str] = None,
        size: int = 28,
        color: str = "#FFFFFF",
        decimals: int = 0,
        template: str = "{:g}",
        max_value: float = 10.0,
        suffix: str = "+",
        roll_height: float = 0.30,
        mode: str = "roll",
        weight: str = "BOLD",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.font = font
        self.size = size
        self.color = cast(ManimColor, color)
        self.decimals = max(0, int(decimals))
        self.template = template
        self.max_value = float(max_value)
        self.suffix = suffix
        self.roll_height = float(roll_height)
        self.mode = mode
        self.weight = weight
        self._cache: dict[int, Text] = {}

    # ------------------------------------------------------------------
    def label_for(self, value: float) -> str:
        """Format a value, including the overflow suffix.

        Parameters
        ----------
        value
            Value to display.

        Returns
        -------
            The formatted label.
        """

        v = float(value)
        if self.max_value > 0 and v > self.max_value + 1e-9:
            v = self.max_value
            extra = self.suffix
        else:
            extra = ""
        q = round(v, self.decimals) if self.decimals else float(round(v))
        try:
            text = self.template.format(q)
        except (ValueError, IndexError, KeyError):  # pragma: no cover - user template
            text = f"{q:g}"
        return f"{text}{extra}"

    def _key_limit(self) -> int:
        """Return the largest integer glyph key the counter needs.

        Returns
        -------
            The cache key limit derived from the full scale.
        """

        return max(1, int(math.ceil(self.max_value)) + 1)

    def set_max_value(self, value: float) -> None:
        """Update the full scale used by the overflow rule.

        Cached glyphs whose label is no longer correct are dropped and rebuilt
        lazily, so call this when the chart settles, not on every frame.

        Parameters
        ----------
        value
            New full-scale value.
        """

        value = float(value)
        if abs(value - self.max_value) < 1e-9:
            return
        self.max_value = value
        limit = self._key_limit()
        for key in list(self._cache):
            txt = self._cache[key]
            if key > limit or getattr(txt, "text", None) != self.label_for(key):
                self.remove(txt)
                self._cache.pop(key, None)

    def hide(self) -> None:
        """Hide every cached glyph (used while another read-out takes over)."""
        for txt in self._cache.values():
            txt.set_opacity(0)

    def set_live_color(self, color: ParsableManimColor) -> None:
        """Recolour the cached glyphs.

        Parameters
        ----------
        color
            New glyph colour.
        """

        col = str(color)
        if getattr(self, "_live_color", None) == col:
            return
        self._live_color = col
        self.color = cast(ManimColor, col)
        for txt in self._cache.values():
            txt.set_color(col)

    def _text_for(self, key: int) -> Text:
        """Return the cached glyph for an integer key, creating it if needed.

        Parameters
        ----------
        key
            Integer value to display.

        Returns
        -------
            The cached text mobject for that value.
        """

        key = int(np.clip(key, 0, self._key_limit()))
        if key not in self._cache:
            text_kwargs: dict[str, Any] = {
                "weight": self.weight,
                "font_size": self.size,
                "color": self.color,
            }
            if self.font is not None:
                text_kwargs["font"] = self.font
            txt = Text(self.label_for(key), **text_kwargs)
            txt.set_opacity(0)
            self._cache[key] = txt
            self.add(txt)
        return self._cache[key]

    @staticmethod
    def _apply_scale(txt: Text, scale: float) -> None:
        """Hook for subclasses to react to chart scaling.

        The base implementation does nothing because glyphs inherit the chart
        transform; only the wheel travel uses the scale.

        Parameters
        ----------
        txt
            Glyph being positioned.
        scale
            Current chart unit length.
        """

    # ------------------------------------------------------------------
    def render(
        self,
        value: float,
        anchor: np.ndarray,
        *,
        opacity: float = 1.0,
        scale: float = 1.0,
        align: str = "left",
    ) -> None:
        """Point the counter at a new value and world anchor.

        Parameters
        ----------
        value
            Value to display.
        anchor
            World-space anchor for the glyph.
        opacity
            Opacity in the range 0 to 1.
        scale
            Current chart unit length, used for wheel travel.
        align
            Which glyph edge sits on the anchor: ``"left"``, ``"right"``,
            or ``"center"``.
        """
        value = float(value)

        op = float(np.clip(opacity, 0.0, 1.0))
        anchor = np.asarray(anchor, dtype=float)

        if self.mode == "off":
            for txt in self._cache.values():
                txt.set_opacity(0)
            return

        if self.mode == "swap":
            key = int(round(value))
            active = {key: (1.0, np.zeros(3))}
        else:  # "roll"
            lo = int(math.floor(value + 1e-9))
            frac = value - lo
            if frac > 1 - 1e-9:
                lo += 1
                frac = 0.0
            travel = self.roll_height * scale
            active = {
                lo: (1.0 - frac, UP * (frac * travel)),
                lo + 1: (frac, DOWN * ((1.0 - frac) * travel)),
            }

        aligned_edge = {"left": LEFT, "right": RIGHT, "center": None}.get(align, LEFT)
        for key, (weight, offset) in active.items():
            txt = self._text_for(key)
            self._apply_scale(txt, scale)
            if aligned_edge is None:
                txt.move_to(anchor + offset)
            else:
                txt.move_to(anchor + offset, aligned_edge=aligned_edge)
            txt.set_opacity(weight * op)
        for key, txt in self._cache.items():
            if key not in active:
                txt.set_opacity(0)

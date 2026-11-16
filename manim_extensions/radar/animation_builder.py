# SPDX-FileCopyrightText: 2026 FTZ-OPUS
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Structural type for Manim's fluent animation-builder objects."""

from __future__ import annotations

from typing import Protocol

__all__ = ["AnimationBuilder"]


class AnimationBuilder(Protocol):
    """Describe the fluent builder returned by ``mobject.animate``-style APIs.

    Both :class:`~manim_extensions.radar.camera.CameraRig` and
    :class:`~manim_extensions.radar.chart.RadarChart` return objects that accept
    duration and easing calls before they are played. The protocol lets those
    return types stay precise without importing Manim's private builder class.

    Examples
    --------
    ::

        builder = rig.push_in(chart)
        builder.set_run_time(0.8)
    """

    def set_run_time(self, run_time: float) -> "AnimationBuilder":
        """Set the duration of the pending animation.

        Parameters
        ----------
        run_time
            Duration in seconds.

        Returns
        -------
            The same builder, allowing further calls to be chained.
        """


if __name__ == "__main__":
    raise SystemExit("This module only defines a typing protocol.")

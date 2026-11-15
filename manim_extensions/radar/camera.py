# SPDX-FileCopyrightText: 2026 FTZ-OPUS
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""True-camera helpers for radar charts (:class:`~manim.scene.moving_camera_scene.MovingCameraScene`).

:class:`~manim_extensions.radar.camera.CameraRig` wraps the camera frame so a radar scene can be shot like a
video: push in for drama, pull out for the establishing shot, glide to a
point of interest, or micro-push towards an escaping overflow spike.

For plain :class:`~manim.scene.scene.Scene` classes (no camera to move), :meth:`~manim_extensions.radar.chart.RadarChart.push_in`
scales the chart instead — same idea, zero setup.
"""

from __future__ import annotations

from typing import Any, Optional

import numpy as np

__all__ = ["CameraRig"]


class CameraRig:
    """Small fluent wrapper around a :class:`~manim.scene.moving_camera_scene.MovingCameraScene` camera frame.

    Examples
    --------
    ::

        class MyScene(MovingCameraScene):
            def construct(self):
                chart = RadarChart(...)
                rig = CameraRig(self)
                self.play(rig.push_in(chart, factor=1.3))
                self.play(chart.morph_to(...))
                self.play(rig.pull_out())
    """

    def __init__(self, scene: Any) -> None:
        frame = getattr(getattr(scene, "camera", None), "frame", None)
        if frame is None:
            raise TypeError(
                "CameraRig needs a MovingCameraScene (whose camera owns a "
                "frame); for plain scenes use chart.push_in() instead"
            )
        self.frame = frame
        self._zoom = 1.0

    # ------------------------------------------------------------------
    def push_in(
        self, target: Any = None, factor: float = 1.35, run_time: float = 1.0, **kwargs
    ) -> Any:
        """Zoom the camera towards ``target`` (a chart, a point, anything).

        Returns an animation — ``self.play(rig.push_in(chart))``.
        """
        self._zoom *= float(factor)
        anim = self.frame.animate.scale(1.0 / float(factor))
        if target is not None:
            anim = anim.move_to(target)
        return self._timed(anim, run_time)

    def pull_out(
        self,
        factor: Optional[float] = None,
        target: Any = None,
        run_time: float = 1.0,
        **kwargs,
    ) -> Any:
        """Zoom back out. Without ``factor`` the camera returns to the default
        full frame (undoing every previous push/focus) and recentres on
        ``target`` (default: the scene origin — pass your chart if it lives
        elsewhere)."""
        if factor is None:
            k = self._zoom
            self._zoom = 1.0
        else:
            k = float(factor)
            self._zoom /= float(factor)
        anim = self.frame.animate.scale(k)
        if target is not None:
            anim = anim.move_to(target)
        else:
            anim = anim.move_to(np.zeros(3))
        return self._timed(anim, run_time)

    def focus_point(
        self, point: Any, factor: float = 1.5, run_time: float = 0.9, **kwargs
    ) -> Any:
        """Pan to ``point`` and zoom in by ``factor`` in one move."""
        self._zoom *= float(factor)
        return self._timed(
            self.frame.animate.scale(1.0 / float(factor)).move_to(point), run_time
        )

    def micro_push(
        self, direction: Any, amount: float = 0.08, run_time: float = 0.35
    ) -> Any:
        """A quick breath towards ``direction`` and back (burst accent)."""
        direction = np.asarray(direction, dtype=float)
        if direction.ndim == 1 and direction.size >= 2:
            direction = np.array([direction[0], direction[1], 0.0])
        center = self.frame.get_center().copy()
        return self._timed(
            self.frame.animate.scale(1.0 - amount).move_to(
                center + direction * amount * 2.0
            ),
            run_time,
        )

    # ------------------------------------------------------------------
    @staticmethod
    def _timed(anim: Any, run_time: float) -> Any:
        """_timed."""
        if hasattr(anim, "set_run_time"):
            return anim.set_run_time(run_time)
        return anim.run_time(run_time)

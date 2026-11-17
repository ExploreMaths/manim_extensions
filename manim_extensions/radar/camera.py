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

from typing import Optional

import numpy as np
from manim import Mobject, MovingCameraScene
from manim.mobject.mobject import _AnimationBuilder
from manim.typing import Point3D, Vector3D

__all__ = ["CameraRig"]


class CameraRig:
    """Small fluent wrapper around a moving-camera frame.

    Parameters
    ----------
    scene
        A :class:`~manim.scene.moving_camera_scene.MovingCameraScene`
        whose camera owns a frame.

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

    def __init__(self, scene: MovingCameraScene) -> None:
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
        self,
        target: Mobject | Point3D | None = None,
        factor: float = 1.35,
        run_time: float = 1.0,
        **kwargs,
    ) -> _AnimationBuilder:
        """Zoom the camera towards a target.

        Parameters
        ----------
        target
            Chart, point, or mobject to centre on.
        factor
            Zoom factor greater than one.
        run_time
            Duration of the move.
        kwargs
            Reserved for call-site compatibility.

        Returns
        -------
            An animation that performs the push.
        """

        self._zoom *= float(factor)
        anim = self.frame.animate.scale(1.0 / float(factor))
        if target is not None:
            anim = anim.move_to(target)
        return self._timed(anim, run_time)

    def pull_out(
        self,
        factor: Optional[float] = None,
        target: Mobject | Point3D | None = None,
        run_time: float = 1.0,
        **kwargs,
    ) -> _AnimationBuilder:
        """Zoom back out towards the default frame or a target.

        Parameters
        ----------
        factor
            Zoom-out factor; when omitted, the camera returns to the full
            default frame and every previous push is undone.
        target
            Point to recentre on; defaults to the scene origin.
        run_time
            Duration of the move.
        kwargs
            Reserved for call-site compatibility.

        Returns
        -------
            An animation that performs the pull-out.
        """

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
        self, point: Point3D, factor: float = 1.5, run_time: float = 0.9, **kwargs
    ) -> _AnimationBuilder:
        """Pan to a point and zoom in during one move.

        Parameters
        ----------
        point
            World-space point to centre on.
        factor
            Zoom factor greater than one.
        run_time
            Duration of the move.
        kwargs
            Reserved for call-site compatibility.

        Returns
        -------
            An animation that pans and zooms.
        """

        self._zoom *= float(factor)
        return self._timed(
            self.frame.animate.scale(1.0 / float(factor)).move_to(point), run_time
        )

    def micro_push(
        self, direction: Vector3D, amount: float = 0.08, run_time: float = 0.35
    ) -> _AnimationBuilder:
        """Make a quick camera breath towards a direction and back.

        Parameters
        ----------
        direction
            Direction of the push; only the first two components are used.
        amount
            Relative push amount.
        run_time
            Duration of the move.

        Returns
        -------
            An animation that performs the micro-push.
        """

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
    def _timed(anim: _AnimationBuilder, run_time: float) -> _AnimationBuilder:
        """Attach a run time to an animation.

        Parameters
        ----------
        anim
            Animation to adjust.
        run_time
            Desired duration.

        Returns
        -------
            The same animation with the requested run time.
        """

        if hasattr(anim, "set_run_time"):
            return anim.set_run_time(run_time)
        return anim.run_time(run_time)

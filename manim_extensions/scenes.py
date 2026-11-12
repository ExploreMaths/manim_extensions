# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Scene classes for Manim.

The module currently provides
:class:`~manim_extensions.scenes.ConstantStrokeWidthScene`, a
:class:`~manim.scene.moving_camera_scene.MovingCameraScene` subclass that keeps the apparent thickness of
strokes constant while the camera zooms.  Using this scene adds a
``fixed_stroke_width`` parameter to stroke-bearing mobjects so that they can opt
out of that compensation.

"""

import functools
from typing import Any, Self

from manim import VMobject, config
from manim.mobject.opengl.opengl_vectorized_mobject import OpenGLVMobject
from manim.scene.moving_camera_scene import MovingCameraScene

__all__ = ["ConstantStrokeWidthScene"]


class ConstantStrokeWidthScene(MovingCameraScene):
    """A scene whose strokes keep a constant on-screen width while zooming.

    Zooming the camera in multiplies the on-screen thickness of every stroke
    by the zoom factor, whichever renderer is used.  This scene compensates for
    that by scaling the ``stroke_width`` of every mobject inversely to the
    camera's frame height, once per frame.  The on-screen (visual) width
    therefore stays the same, while the underlying ``stroke_width`` value
    changes together with the zoom level.

    .. note::

        The compensation is exact for flat content lying in the plane of the
        camera.  With a perspective camera, strokes at different depths are still
        affected by the perspective projection, because the focal distance scales
        together with the frame height.

        Mobjects fixed in the frame with ``fix_in_frame`` are not adjusted,
        since their apparent size does not depend on the
        camera.  To opt out per mobject, set its ``fixed_stroke_width``
        parameter to ``True`` (``mobject.fixed_stroke_width = True`` or
        ``mobject.set(fixed_stroke_width=True)``); such mobjects keep their
        ``stroke_width`` and therefore change appearance together with the zoom.
        The parameter is installed on the stroke-bearing mobject classes as soon as
        a :class:`~manim_extensions.scenes.ConstantStrokeWidthScene` is used, so it
        does not need to be set before adding the mobject to the scene.

    Parameters
    ----------
    *args
        Positional arguments forwarded to
        :class:`~manim.scene.moving_camera_scene.MovingCameraScene`.
    **kwargs
        Keyword arguments forwarded to
        :class:`~manim.scene.moving_camera_scene.MovingCameraScene`.

    Examples
    --------
    The camera zooms in by a factor of three and back out again.  The upper
    line keeps its on-screen width, the lower one opts out with
    ``fixed_stroke_width=True`` and is drawn three times as thick:

    .. manim:: ConstantStrokeWidthExample

       from manim import *
       from manim_extensions.scenes import ConstantStrokeWidthScene

       class ConstantStrokeWidthExample(ConstantStrokeWidthScene):
           def construct(self):
               line1 = Line(LEFT, RIGHT, stroke_width=4).shift(0.3 * UP)
               line2 = Line(LEFT, RIGHT, stroke_width=4, fixed_stroke_width=True).shift(0.3 * DOWN)
               self.add(line1, line2)
               self.play(self.camera.frame.animate.scale(1 / 3), run_time=2)
               self.wait(0.5)
               self.play(self.camera.frame.animate.scale(3), run_time=2)
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._install_stroke_width_parameter()
        self._stroke_scale = self._camera_stroke_scale()
        self.add_updater(self._update_stroke_scale)

    @staticmethod
    def _install_stroke_width_parameter() -> None:
        def _wrap(original_init: Any) -> Any:
            @functools.wraps(original_init)
            def patched_init(self: Any, *args: Any, **kwargs: Any) -> None:
                """Accept ``fixed_stroke_width`` as a constructor keyword."""
                sentinel = object()
                fixed = kwargs.pop("fixed_stroke_width", sentinel)
                original_init(self, *args, **kwargs)
                if fixed is not sentinel:
                    self.fixed_stroke_width = fixed

            return patched_init

        for mobject_class in (VMobject, OpenGLVMobject):
            if "fixed_stroke_width" not in vars(mobject_class):
                setattr(mobject_class, "fixed_stroke_width", False)
            if mobject_class.__dict__.get("_stroke_width_init_patched", False):
                continue
            setattr(mobject_class, "__init__", _wrap(mobject_class.__init__))
            setattr(mobject_class, "_stroke_width_init_patched", True)

    def _camera_stroke_scale(self) -> float:
        """Return the factor by which strokes must be scaled at the current zoom."""
        height = getattr(self.camera, "frame_height", None)
        if height is None:
            get_height = getattr(self.camera, "get_height", None)
            if get_height is None:
                return 1.0
            height = get_height()
        height = float(height)
        if height <= 0.0:
            return 1.0
        return height / float(config.frame_height)

    @staticmethod
    def _scale_stroke_width(member: Any, factor: float) -> None:
        if getattr(member, "is_fixed_in_frame", 0.0):
            return
        if getattr(member, "fixed_stroke_width", False):
            return
        width = getattr(member, "stroke_width", None)
        if width is None:
            return
        member.stroke_width = width * factor

    def _scale_family_stroke_widths(self, mobject: Any, factor: float) -> None:
        get_family = getattr(mobject, "get_family", None)
        family = get_family() if get_family is not None else [mobject]
        for member in family:
            self._scale_stroke_width(member, factor)

    def _update_stroke_scale(self, dt: float) -> None:
        scale = self._camera_stroke_scale()
        if scale == self._stroke_scale:
            return
        ratio = scale / self._stroke_scale
        self._stroke_scale = scale
        for member in self.get_mobject_family_members():
            self._scale_stroke_width(member, ratio)

    def add(self, *mobjects: Any) -> Self:
        """Add mobjects and scale their strokes to the current zoom level.

        Parameters
        ----------
        *mobjects
            The mobjects to add to the scene.

        Returns
        -------
            The scene itself, to allow chaining.
        """
        super().add(*mobjects)
        self._stroke_scale = self._camera_stroke_scale()
        if self._stroke_scale != 1.0:
            for mobject in mobjects:
                self._scale_family_stroke_widths(mobject, self._stroke_scale)
        return self

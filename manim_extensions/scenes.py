# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Scene classes for Manim.

The module currently provides :class:`ConstantStrokeWidthScene`, a
:class:`~manim.scene.scene.Scene` subclass that keeps the apparent thickness of
strokes constant while the camera zooms.  Using this scene adds a
``fixed_stroke_width`` parameter to stroke-bearing mobjects so that they can opt
out of that compensation.

"""

from typing import Any, Self

from manim import VMobject, config
from manim.constants import RendererType
from manim.mobject.opengl.opengl_vectorized_mobject import OpenGLVMobject
from manim.scene.scene import Scene


__all__ = ["ConstantStrokeWidthScene"]


class ConstantStrokeWidthScene(Scene):
    """A scene whose strokes keep a constant on-screen width while zooming.

    The Cairo renderer already draws strokes with a fixed pixel width, so
    nothing needs to be compensated there.  The OpenGL renderer, however,
    specifies stroke widths in scene units: zooming the camera in makes every
    line look proportionally thicker and zooming out makes it look thinner.
    This scene compensates for that by scaling the ``stroke_width`` of every
    mobject inversely to the camera's frame height, once per frame.  The
    on-screen (visual) width therefore stays the same, while the underlying
    ``stroke_width`` value changes together with the zoom level.

    .. note::

        The compensation is exact for flat content lying in the plane of the
        camera.  With a perspective camera, strokes at different depths are still
        affected by the perspective projection, because the focal distance scales
        together with the frame height.

        Mobjects fixed in the frame with ``Mobject.fix_in_frame()`` are not
        adjusted, since their apparent size does not depend on the camera.  To opt
        out per mobject, set its ``fixed_stroke_width`` parameter to ``True``
        (``mobject.fixed_stroke_width = True`` or
        ``mobject.set(fixed_stroke_width=True)``); such mobjects keep their
        ``stroke_width`` and therefore change appearance together with the zoom.
        The parameter is installed on the stroke-bearing mobject classes as soon as
        a :class:`ConstantStrokeWidthScene` is used, so it does not need to be set
        before adding the mobject to the scene.

    Examples
    --------
    .. code-block:: python

        class ZoomScene(ConstantStrokeWidthScene):
            def construct(self):
                line1 = Line(LEFT, RIGHT, stroke_width=4).shift(UP)
                line2 = Line(LEFT, RIGHT, stroke_width=4, fixed_stroke_width=True).shift(DOWN)
                self.add(line1, line2)
                self.play(self.camera.animate.scale(0.5))
                self.wait()
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._install_stroke_width_parameter()
        self._stroke_scale = self._camera_stroke_scale()
        self.add_updater(self._update_stroke_scale)

    @staticmethod
    def _install_stroke_width_parameter() -> None:
        for mobject_class in (VMobject, OpenGLVMobject):
            if "fixed_stroke_width" not in vars(mobject_class):
                setattr(mobject_class, "fixed_stroke_width", False)

    def _camera_stroke_scale(self) -> float:
        """Return the factor by which strokes must be scaled at the current zoom."""
        if config.renderer != RendererType.OPENGL:
            return 1.0
        get_height = getattr(self.camera, "get_height", None)
        if get_height is None:
            return 1.0
        height = float(get_height())
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
        super().add(*mobjects)
        if self._stroke_scale != 1.0:
            for mobject in mobjects:
                self._scale_family_stroke_widths(mobject, self._stroke_scale)
        return self

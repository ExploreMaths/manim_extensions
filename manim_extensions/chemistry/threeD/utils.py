# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""3D utilities for Manim chemistry.

This module provides OpenGL-based 3D geometry classes for chemistry visualizations.
"""

from typing import Any, cast

from manim import ORIGIN, PI, TAU
from manim.mobject.opengl.opengl_surface import OpenGLSurface
import numpy as np
from manim.typing import Point3D, VectorND, MatrixMN


class OpenGLSphere(OpenGLSurface):
    """A sphere rendered as an OpenGL surface.

    Parameters
    ----------
    center
        Center point of the sphere.
    **kwargs
        Additional keyword arguments passed to OpenGLSurface.

    Examples
    --------
    .. manim:: OpenGLSphereOverview
       :renderer: opengl
       :save_last_frame:

       from manim import *
       from manim_extensions.chemistry.threeD.utils import OpenGLSphere

       OpenGLSphereTarget = OpenGLSphere

       class OpenGLSphereOverview(Scene):
           def construct(self):
               public = [n for n in dir(OpenGLSphereTarget) if not n.startswith("_")]
               card = VGroup(
                   Text('OpenGLSphere', font_size=36),
                   Text('module: manim_extensions.chemistry.threeD.utils', font_size=18, color=GREY),
                   Text('A sphere rendered as an OpenGL surface', font_size=22),
                   Text("API: " + ", ".join(public[:6]), font_size=18, color=BLUE),
               ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
               card.scale_to_fit_width(11.5).move_to(ORIGIN)
               frame = RoundedRectangle(
                   width=12.1, height=card.height + 0.5, corner_radius=0.2, color=BLUE_D
               ).move_to(card)
               self.add(frame, card)

    .. manim:: OpenGLSpherePreview
       :renderer: opengl
       :save_last_frame:

       from manim import *
       from manim_extensions.chemistry.threeD.utils import OpenGLSphere

       class OpenGLSpherePreview(ThreeDScene):
           def construct(self):
               self.set_camera_orientation(phi=70 * DEGREES, theta=30 * DEGREES)
               self.add(OpenGLSphere(radius=1.2, color=BLUE))

    .. code-block:: python

        from manim_extensions.chemistry.threeD.utils import OpenGLSphere

        sphere = OpenGLSphere(center=[0, 0, 0], radius=0.5)
    """

    def __init__(  # explicit-any-ok: **kwargs forwarded through Manim's untyped boundary
        self,
        center: Point3D = ORIGIN,
        **kwargs: Any,  # explicit-any-ok: forwarded unchanged through Manim's untyped **kwargs boundary
    ) -> None:
        super().__init__(
            self.uv_func,
            u_range=(0, TAU),
            v_range=(0, PI),
            **kwargs,
        )

        self.shift(center)

    def uv_func(self, u: VectorND | None, v: VectorND) -> MatrixMN:
        """Compute sphere surface coordinates from azimuthal u and polar v angles.

        Parameters
        ----------
        u
            Azimuthal angle.
        v
            Polar angle.

        Returns
        -------
            The computed array.
        """
        u_arr = cast(VectorND, u)
        return np.array(
            [np.cos(u_arr) * np.sin(v), np.sin(u_arr) * np.sin(v), -np.cos(v)],
        )

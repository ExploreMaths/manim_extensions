# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""3D utilities for Manim chemistry.

This module provides OpenGL-based 3D geometry classes for chemistry visualizations.

"""

from manim import *
from manim.mobject.opengl.opengl_surface import OpenGLSurface
import numpy as np



class OpenGLSphere(OpenGLSurface):
    """A sphere rendered as an OpenGL surface.

    Parameters
    ----------
    center
        Center point of the sphere. Defaults to ``ORIGIN``.
    **kwargs
        Additional keyword arguments passed to :class:`~manim_extensions.chemistry.threeD.utils.OpenGLSphere.OpenGLSurface`.
    """

    def __init__(
        self,
        center=ORIGIN,
        **kwargs,
    ):
        super().__init__(
            self.uv_func,
            u_range=(0, TAU),
            v_range=(0, PI),
            **kwargs,
        )

        self.shift(center)

    def uv_func(self, u, v):
        return np.array(
            [np.cos(u) * np.sin(v), np.sin(u) * np.sin(v), -np.cos(v)],
        )
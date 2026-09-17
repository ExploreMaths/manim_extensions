# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""3D utilities for Manim chemistry.

This module provides OpenGL-based 3D geometry classes for chemistry visualizations.

"""

from manim import ORIGIN, PI, TAU
from manim.mobject.opengl.opengl_surface import OpenGLSurface
import numpy as np



from typing import Any, Optional
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
        center: Any = ORIGIN,
        **kwargs,
    ):
        super().__init__(
            self.uv_func,
            u_range=(0, TAU),
            v_range=(0, PI),
            **kwargs,
        )

        self.shift(center)

    def uv_func(self, u: Optional[np.ndarray], v: Any):
        return np.array(
            [np.cos(u) * np.sin(v), np.sin(u) * np.sin(v), -np.cos(v)],
        )
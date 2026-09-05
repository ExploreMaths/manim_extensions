# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""3D atom representation for Manim chemistry.

This module provides the ThreeDAtom class for rendering atoms in 3D.

"""

import numpy as np

from .utils import OpenGLSphere
from ..element import Element


class ThreeDAtom(OpenGLSphere):
    """
    Used to draw a sphere which represents an atom.
    Uses an Element to get data.

    Parameters
    ----------
    element : :class:`~manim_extensions.chemistry.element.Element`
        The element whose data (color) is used to draw the atom.
    coords : :class:`np.array`, optional
        3D coordinates of the atom center. Defaults to the origin.
    **kwargs
        Additional keyword arguments passed to :class:`~manim_extensions.chemistry.threeD.threedatom.ThreeDAtom.OpenGLSphere`.
    """

    def __init__(self, element: Element, coords=np.array([0, 0, 0]), **kwargs):
        self.center = coords
        self.coords = coords
        self.element = element

        super().__init__(center=self.center, color=element.color, **kwargs)
        self.scale(0.25)
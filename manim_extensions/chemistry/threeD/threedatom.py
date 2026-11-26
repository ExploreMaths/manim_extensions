# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""3D atom representation for Manim chemistry.

This module provides the :class:`~manim_extensions.chemistry.threeD.threedatom.ThreeDAtom` class for rendering atoms in 3D.
"""

from typing import Any, cast

# unlinked-class-ok: Element

import numpy as np

from .utils import OpenGLSphere
from ..element import Element
from manim.typing import Point3D


class ThreeDAtom(OpenGLSphere):
    """Used to draw a sphere which represents an atom.
    Uses an Element to get data.

    Parameters
    ----------
    element
        The element whose data (color) is used to draw the atom.
    coords
        3D coordinates of the atom center.
    **kwargs
        Additional keyword arguments passed to :class:`~manim_extensions.chemistry.threeD.utils.OpenGLSphere`.

    Examples
    --------
    .. manim:: ThreeDAtomOverview
       :save_last_frame:

       from manim import *
       from manim_extensions.chemistry.threeD.threedatom import ThreeDAtom

       ThreeDAtomTarget = ThreeDAtom

       class ThreeDAtomOverview(Scene):
           def construct(self):
               public = [n for n in dir(ThreeDAtomTarget) if not n.startswith("_")]
               card = VGroup(
                   Text('ThreeDAtom', font_size=36),
                   Text('module: manim_extensions.chemistry.threeD.threedatom', font_size=18, color=GREY),
                   Text('Used to draw a sphere which represents an atom. Uses an Element to get data', font_size=22),
                   Text("API: " + ", ".join(public[:6]), font_size=18, color=BLUE),
               ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
               card.scale_to_fit_width(11.5).move_to(ORIGIN)
               frame = RoundedRectangle(
                   width=12.1, height=card.height + 0.5, corner_radius=0.2, color=BLUE_D
               ).move_to(card)
               self.add(frame, card)

    .. code-block:: python

        import numpy as np
        from manim_extensions.chemistry.threeD.threedatom import ThreeDAtom
        from manim_extensions.chemistry.utils.utils import get_element

        atom = ThreeDAtom(get_element("C"), coords=np.array([0.0, 0.0, 0.0]))
    """

    def __init__(
        self, element: Element, coords: Point3D = np.array([0, 0, 0]), **kwargs: Any
    ) -> None:
        cast(Any, self).center = coords
        self.coords = coords
        self.element = element

        super().__init__(center=coords, color=element.color, **kwargs)
        self.scale(0.25)

# SPDX-FileCopyrightText: 2024 sinianluoye
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""NumPy helper utilities for algorithm visualization."""

import numpy as np
from manim.typing import VectorND


class NumpyHelper:
    """Static helper methods for common NumPy vector operations.

    Provides utilities for normalizing vectors and comparing
    vector equality and direction within numerical tolerance.

    Examples
    --------
    .. manim:: NumpyHelperOverview
       :save_last_frame:

       from manim import *
       from manim_extensions.algorithm.utils.numpy_helper import NumpyHelper

       NumpyHelperTarget = NumpyHelper

       class NumpyHelperOverview(Scene):
           def construct(self):
               public = [n for n in dir(NumpyHelperTarget) if not n.startswith("_")]
               card = VGroup(
                   Text('NumpyHelper', font_size=36),
                   Text('module: manim_extensions.algorithm.utils.numpy_helper', font_size=18, color=GREY),
                   Text('Static helper methods for common NumPy vector operations', font_size=22),
                   Text("API: " + ", ".join(public[:6]), font_size=18, color=BLUE),
               ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
               card.scale_to_fit_width(11.5).move_to(ORIGIN)
               frame = RoundedRectangle(
                   width=12.1, height=card.height + 0.5, corner_radius=0.2, color=BLUE_D
               ).move_to(card)
               self.add(frame, card)

    .. code-block:: python

        import numpy as np
        from manim_extensions.algorithm.utils.numpy_helper import NumpyHelper

        unit = NumpyHelper.normalize_vector(np.array([3.0, 4.0, 0.0]))
        same = NumpyHelper.is_equal_vector(unit, unit)
    """

    @staticmethod
    def normalize_vector(v: VectorND) -> VectorND:
        """Normalise a vector to unit length.

        Parameters
        ----------
        v
            Input vector (NumPy array).

        Returns
        -------
            Unit-length vector.  If the norm of ``v`` is zero, the original
            vector is returned unchanged.
        """
        norm = np.linalg.norm(v)
        if norm == 0:
            return v
        return v / norm

    @staticmethod
    def is_equal_vector(
        v1: VectorND,
        v2: VectorND,
        rtol: float = 1e-5,
        atol: float = 1e-8,
    ) -> bool:
        """Check whether two vectors are equal within tolerance.

        Parameters
        ----------
        v1
            First vector.
        v2
            Second vector.
        rtol
            Relative tolerance.
        atol
            Absolute tolerance.

        Returns
        -------
            Whether ``v1`` and ``v2`` are element-wise close.
        """
        return bool(np.isclose(v1, v2, rtol=rtol, atol=atol).all())

    @staticmethod
    def is_same_direction(
        v1: VectorND,
        v2: VectorND,
        rtol: float = 1e-5,
        atol: float = 1e-8,
    ) -> bool:
        """Check whether two vectors point in the same direction.

        Both vectors are normalized before comparison.

        Parameters
        ----------
        v1
            First vector.
        v2
            Second vector.
        rtol
            Relative tolerance.
        atol
            Absolute tolerance.

        Returns
        -------
            Whether the normalized vectors are equal within tolerance.
        """
        return NumpyHelper.is_equal_vector(
            NumpyHelper.normalize_vector(v1),
            NumpyHelper.normalize_vector(v2),
            rtol=rtol,
            atol=atol,
        )

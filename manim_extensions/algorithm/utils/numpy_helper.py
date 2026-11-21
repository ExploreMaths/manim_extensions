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

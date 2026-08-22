# SPDX-FileCopyrightText: 2024 sinianluoye
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


import numpy as np
from numpy.typing import NDArray


class NumpyHelper:
    """Utility functions for common NumPy vector checks."""

    @staticmethod
    def normalize_vector(v: NDArray):
        """Normalise a vector to unit length.

        Parameters
        ----------
        v : NDArray
            Input vector (NumPy array).

        Returns
        -------
        NDArray
            Unit-length vector.  If the norm of *v* is zero, the original
            vector is returned unchanged.
        """
        norm = np.linalg.norm(v)
        if norm == 0:
            return v
        return v / norm

    @staticmethod
    def is_equal_vector(
        v1: NDArray, v2: NDArray, rtol: float = 1e-5, atol: float = 1e-8
    ):
        """Check whether two vectors are equal within tolerance.

        Parameters
        ----------
        v1 : NDArray
            First vector.
        v2 : NDArray
            Second vector.
        rtol : float
            Relative tolerance.
        atol : float
            Absolute tolerance.

        Returns
        -------
        bool
            ``True`` if ``v1`` and ``v2`` are element-wise close.
        """
        return np.isclose(v1, v2, rtol=rtol, atol=atol).all()

    @staticmethod
    def is_same_direction(
        v1: NDArray, v2: NDArray, rtol: float = 1e-5, atol: float = 1e-8
    ):
        """Check whether two vectors point in the same direction.

        Both vectors are normalized before comparison.

        Parameters
        ----------
        v1 : NDArray
            First vector.
        v2 : NDArray
            Second vector.
        rtol : float
            Relative tolerance.
        atol : float
            Absolute tolerance.

        Returns
        -------
        bool
            ``True`` if the normalized vectors are equal within tolerance.
        """
        return NumpyHelper.is_equal_vector(
            NumpyHelper.normalize_vector(v1),
            NumpyHelper.normalize_vector(v2),
            rtol=rtol,
            atol=atol,
        )

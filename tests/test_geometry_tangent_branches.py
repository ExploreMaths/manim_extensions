# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Exercise the degenerate cases of the tangent-point solver."""

import numpy as np
import pytest

from manim_extensions.geometry import tangent_point

CASES = [
    ((0, 1), (1, 1), (0, 0), (1, 0)),
    ((0, 0), (0, 0, 1), (-3, 0, 0), (3, 0, 0)),
    ((0, 0), (3, 0), (1, 1), (1, 1)),
    ((0, 1), (0, 3), (0, 0), (1, 0)),
    ((0, 2), (1, 2), (0, 0), (1, 0)),
    ((0, 0.01), (1, 0.01), (0, 0), (1, 0)),
    ((-2, 1), (2, 1), (-3, 0), (3, 0)),
    ((0, 0), (2, 0), (3, 0), (3, 0)),
    ((0, 1), (1, 2), (0, 0), (1, 0)),
    ((0, 2), (1, 2), (0, 0), (0, 1)),
    (
        (-2.1938145353, 2.0846024216),
        (1.5826477139, -1.4695858456),
        (-0.0273894774, -0.3030536113),
        (0.9095578363, 1.7323401068),
    ),
]


@pytest.mark.parametrize("p1,p2,start,end", CASES)
def test_tangent_point_degenerate_cases(p1, p2, start, end):
    result = tangent_point(p1, p2, start, end)

    assert result is None or np.asarray(result).shape == (3,)

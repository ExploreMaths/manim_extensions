# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Smoke tests for the vendored ``manim-CAD_Drawing_utils`` package."""

import numpy as np
import pytest
from manim import LEFT, RIGHT

from manim_extensions.cad_drawing_utils import (
    LinearDimension,
    round_corners,
    angle_between_vectors_signed,
    utils,
)


def test_signed_angle():
    angle = angle_between_vectors_signed(
        np.array([1.0, 0.0, 0.0]), np.array([0.0, 1.0, 0.0])
    )
    assert angle == pytest.approx(np.pi / 2)


def test_utils_submodule_is_rebound():
    assert utils.angle_between_vectors_signed is angle_between_vectors_signed


def test_round_corners_is_exposed():
    assert callable(round_corners)


def test_linear_dimension_keeps_endpoints():
    dimension = LinearDimension(LEFT, RIGHT)
    assert np.allclose(dimension.start, LEFT)
    assert np.allclose(dimension.end, RIGHT)

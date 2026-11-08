# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the Gaussian distribution mobject."""

import numpy as np
import pytest
from manim import Axes

from manim_extensions.machine_learning.utils.mobjects.probability import GaussianDistribution


@pytest.fixture()
def axes():
    return Axes(x_range=[-3, 3], y_range=[-3, 3])


@pytest.mark.parametrize("dist_theme", ["gaussian", "ellipse"])
def test_distribution_construction(axes, dist_theme):
    dist = GaussianDistribution(
        axes,
        mean=np.array([0.0, 0.0]),
        cov=np.array([[1.0, 0.0], [0.0, 1.0]]),
        dist_theme=dist_theme,
    )

    assert dist.axes is axes
    assert len(dist.submobjects) >= 1


def test_simple_gaussian_ellipse(axes):
    ellipse = GaussianDistribution(axes).construct_simple_gaussian_ellipse(
        np.array([0.0, 0.0]), np.array([[1.0, 0.0], [0.0, 2.0]])
    )

    assert ellipse is not None

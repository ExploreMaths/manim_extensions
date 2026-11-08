# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for MCMC visualisation helpers that build animations eagerly."""

import numpy as np

from manim_extensions.machine_learning.diffusion.mcmc import (
    MCMCAxes,
    MultidimensionalGaussianPosterior,
)


def test_distribution_evaluates_log_probability():
    distribution = MultidimensionalGaussianPosterior(ndim=2)

    assert np.isfinite(distribution(np.array([0.0, 0.0])))


def test_gaussian_proposal_animation():
    axes = MCMCAxes()

    animation = axes.visualize_gaussian_proposal_about_point(np.array([0.0, 0.0]))

    assert animation is not None


def test_gaussian_proposal_with_explicit_covariance():
    axes = MCMCAxes()

    animation = axes.visualize_gaussian_proposal_about_point(
        np.array([0.0, 0.0]), np.array([[1.0, 0.0], [0.0, 1.0]])
    )

    assert animation is not None


def test_ground_truth_gaussian_animation():
    axes = MCMCAxes()
    distribution = MultidimensionalGaussianPosterior(ndim=2)

    animation = axes.show_ground_truth_gaussian(distribution)

    assert animation is not None

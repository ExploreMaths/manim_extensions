# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the MCMC chain sampling visualization."""

import numpy as np

from manim_extensions.machine_learning.diffusion.mcmc import (
    MCMCAxes,
    MultidimensionalGaussianPosterior,
)


def _true_samples(count: int = 200, seed: int = 3):
    rng = np.random.default_rng(seed)
    return rng.normal(size=(count, 2))


def test_chain_sampling_animation_is_built():
    axes = MCMCAxes()

    animation = axes.visualize_metropolis_hastings_chain_sampling(
        MultidimensionalGaussianPosterior(ndim=2),
        true_samples=_true_samples(),
        sampling_kwargs={"initial_location": np.array([0.0, 0.0]), "iterations": 5},
    )

    assert animation is not None


def test_chain_sampling_with_dots():
    axes = MCMCAxes()

    animation = axes.visualize_metropolis_hastings_chain_sampling(
        MultidimensionalGaussianPosterior(ndim=2),
        show_dots=True,
        true_samples=_true_samples(seed=11),
        sampling_kwargs={"initial_location": np.array([0.4, -0.4]), "iterations": 3},
    )

    assert animation is not None

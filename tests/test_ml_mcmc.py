# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the Metropolis-Hastings sampler shipped with the diffusion module."""

import numpy as np
import pytest

from manim_extensions.machine_learning.diffusion.mcmc import (
    MultidimensionalGaussianPosterior,
    gaussian_proposal,
    make_dist_image_mobject_from_samples,
    metropolis_hastings_sampler,
)


def test_gaussian_proposal_returns_step_and_factor():
    x = np.array([0.0, 0.0])

    proposal, factor = gaussian_proposal(x)

    assert isinstance(proposal, np.ndarray)
    assert proposal.shape == (2,)
    assert np.isfinite(factor)


def test_gaussian_proposal_respects_sigma():
    x = np.array([0.0, 0.0])

    small, _ = gaussian_proposal(x, sigma=0.01)
    large, _ = gaussian_proposal(x, sigma=10.0)

    assert np.linalg.norm(small - x) < np.linalg.norm(large - x) or np.allclose(
        large, x
    )


@pytest.mark.parametrize("ndim", [2, 3])
def test_posterior_defaults(ndim):
    posterior = MultidimensionalGaussianPosterior(ndim=ndim)

    assert posterior.mu.shape == (ndim,)
    assert posterior.var.shape == (ndim,)


def test_posterior_call_inside_bounds():
    posterior = MultidimensionalGaussianPosterior()
    point = np.zeros(2)

    value = posterior(point)

    assert np.isfinite(value)


def test_posterior_call_outside_bounds_is_penalised():
    posterior = MultidimensionalGaussianPosterior()

    assert posterior(np.array([1000.0, 1000.0])) == -1e6
    assert posterior(np.array([-1000.0, 0.0])) == -1e6


@pytest.mark.parametrize("warm_up", [0, 5])
def test_sampler_shapes(warm_up):
    chain, warm, proposals = metropolis_hastings_sampler(
        iterations=20, warm_up=warm_up, sampling_seed=7
    )

    assert chain.shape == (20, 2)
    assert proposals.shape == (20, 2)
    assert warm.size == 0


def test_sampler_stays_near_the_mode():
    chain, _, _ = metropolis_hastings_sampler(iterations=200, sampling_seed=3)

    assert np.abs(chain[-1]).max() < 12


def test_dist_image_mobject_from_samples():
    rng = np.random.default_rng(0)
    samples = rng.normal(size=(50, 2))

    image = make_dist_image_mobject_from_samples(samples, ylim=[-3, 3], xlim=[-3, 3])

    assert image is not None

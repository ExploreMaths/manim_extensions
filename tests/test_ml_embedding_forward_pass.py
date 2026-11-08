# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for embedding-layer forward-pass animation branches."""

import numpy as np
import pytest
from manim import AnimationGroup, tempconfig

from manim_extensions.machine_learning.neural_network.layers.embedding import EmbeddingLayer

DIST_ARGS = {"mean": np.array([0.0, 0.0]), "cov": np.array([[1.0, 0.0], [0.0, 1.0]])}


@pytest.fixture(autouse=True)
def _config():
    with tempconfig({"dry_run": True, "disable_caching": True, "renderer": "cairo"}):
        yield


def test_forward_pass_with_explicit_dist_args():
    layer = EmbeddingLayer()
    layer.construct_layer(None, None)

    animation = layer.make_forward_pass_animation(
        layer_args={"dist_args": DIST_ARGS, "scale_factor": 2.0}
    )

    assert isinstance(animation, AnimationGroup)


def test_forward_pass_with_triplet_args():
    layer = EmbeddingLayer()
    layer.construct_layer(None, None)

    animation = layer.make_forward_pass_animation(
        layer_args={
            "triplet_args": {
                "anchor_dist": DIST_ARGS,
                "positive_dist": DIST_ARGS,
                "negative_dist": DIST_ARGS,
            }
        }
    )

    assert len(animation.animations) >= 5


def test_forward_pass_in_paired_query_mode():
    layer = EmbeddingLayer(paired_query_mode=True)
    layer.construct_layer(None, None)

    animation = layer.make_forward_pass_animation(
        layer_args={"positive_dist_args": DIST_ARGS, "negative_dist_args": DIST_ARGS}
    )

    assert isinstance(animation, AnimationGroup)

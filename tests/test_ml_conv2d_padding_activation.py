# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for 2D convolutional layer padding, activation and scaling."""

import pytest
from manim import tempconfig

from manim_extensions.machine_learning.neural_network.layers.convolutional_2d import (
    Convolutional2DLayer,
)


@pytest.fixture(autouse=True)
def _config():
    with tempconfig({"dry_run": True, "disable_caching": True, "renderer": "cairo"}):
        yield


def test_padding_tuple_and_int_forms():
    layer = Convolutional2DLayer(num_feature_maps=2, feature_map_size=4, padding=(1, 2))
    other = Convolutional2DLayer(num_feature_maps=2, feature_map_size=4, padding=1)

    assert layer.padding == (1, 2)
    assert other.padding == (1, 1)


def test_padding_invalid_type_raises():
    with pytest.raises(Exception):
        Convolutional2DLayer(num_feature_maps=1, feature_map_size=4, padding="bad")


def test_activation_function_from_string():
    layer = Convolutional2DLayer(
        num_feature_maps=2, feature_map_size=4, activation_function="ReLU"
    )

    layer.construct_activation_function()

    assert layer.activation_function is not None


def test_scale_updates_cell_width():
    layer = Convolutional2DLayer(num_feature_maps=2, feature_map_size=4)
    cell_width = layer.cell_width

    layer.scale(2)

    assert layer.cell_width == pytest.approx(cell_width * 2)

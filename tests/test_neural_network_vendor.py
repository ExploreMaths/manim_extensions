# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


from manim_extensions.neural_network import NeuralNetworkMobject


def test_neural_network_visuals():
    nn = NeuralNetworkMobject([2, 3, 2])
    assert len(nn.layers) == 3
    assert len(nn.edge_groups) == 2

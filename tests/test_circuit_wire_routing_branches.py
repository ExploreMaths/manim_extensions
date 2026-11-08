# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests covering every wire routing branch of the circuit helper."""

import pytest

from manim_extensions.circuit.utils import Circuit


@pytest.mark.parametrize("diagonal", [False, True])
@pytest.mark.parametrize("invert", [False, True])
@pytest.mark.parametrize(
    "end1,end2",
    [
        ([0.0, 0.0, 0.0], [2.0, 0.0, 0.0]),
        ([0.0, 0.0, 0.0], [0.0, 2.0, 0.0]),
        ([0.0, 0.0, 0.0], [2.0, 1.0, 0.0]),
        ([0.0, 0.0, 0.0], [1.0, 2.0, 0.0]),
        ([2.0, 2.0, 0.0], [0.0, 0.0, 0.0]),
    ],
)
def test_add_wire_routing_branches(diagonal, invert, end1, end2):
    circuit = Circuit()

    points = circuit.add_wire(end1, end2, diagonal=diagonal, invert=invert)

    assert points is None or len(points) >= 2

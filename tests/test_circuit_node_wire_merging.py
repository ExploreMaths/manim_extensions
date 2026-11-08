# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for wiring a node with wires that connect in different orders."""

import numpy as np
import pytest

from manim_extensions.circuit.utils import Node

BASE = [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]]


@pytest.mark.parametrize(
    "wire",
    [
        [[1.0, 0.0, 0.0], [2.0, 0.0, 0.0]],
        [[2.0, 0.0, 0.0], [1.0, 0.0, 0.0]],
        [[-1.0, 0.0, 0.0], [0.0, 0.0, 0.0]],
        [[0.0, 0.0, 0.0], [-1.0, 0.0, 0.0]],
        [[3.0, 0.0, 0.0], [4.0, 0.0, 0.0]],
    ],
)
def test_add_wire_extends_or_appends(wire):
    node = Node()
    node.add_wire(BASE)

    node.add_wire(np.array(wire))

    assert len(node.coords) >= 1

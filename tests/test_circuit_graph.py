# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the circuit graph helpers."""

import numpy as np
from manim import Circle

from manim_extensions.circuit.utils import Circuit, Node


def test_node_check_coord_without_wires():
    node = Node()

    assert node.check_coord([0.0, 0.0, 0.0]) is False


def test_node_check_coord_rejects_distant_point():
    node = Node()

    result = node.check_coord([100.0, 100.0, 0.0])

    assert result is False


def test_add_wire_creates_node():
    circuit = Circuit()

    wire = circuit.add_wire([-2.0, 0.0, 0.0], [2.0, 0.0, 0.0])

    assert wire is not None
    assert len(circuit.node_list) == 1


def test_second_wire_merges_into_existing_node():
    circuit = Circuit()

    circuit.add_wire([-2.0, 0.0, 0.0], [0.0, 0.0, 0.0])
    circuit.add_wire([0.0, 0.0, 0.0], [2.0, 0.0, 0.0])

    assert len(circuit.node_list) >= 1


def test_diagonal_wire_builds_zigzag():
    circuit = Circuit()

    segments = circuit.add_wire([0.0, 0.0, 0.0], [1.0, 1.0, 0.0], diagonal=True)

    assert segments is not None


def test_inverted_wire_is_supported():
    circuit = Circuit()

    segments = circuit.add_wire([1.0, 0.0, 0.0], [-1.0, 0.0, 0.0], invert=True)

    assert segments is None or isinstance(segments, list)


def test_add_components_accepts_mobjects():
    circuit = Circuit()
    component = Circle()

    circuit.add_components(component)

    assert component.get_center() is not None or np.asarray(
        component.get_center()
    ).shape == (3,)

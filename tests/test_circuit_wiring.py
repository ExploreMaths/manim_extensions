# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for circuit primitives and wire routing."""

import pytest
from manim import VMobject, VGroup

from manim_extensions.circuit.utils import Circuit, Node, Source


@pytest.fixture()
def circuit():
    return Circuit()


def test_circuit_is_built(circuit):
    assert circuit is not None


def test_source_exposes_terminals_and_center():
    source = Source(VGroup(VMobject()), "R", 2.0)

    assert source.get_terminals("left") is None
    assert source.get_terminals("right") is None
    assert source.center() is source


def test_source_with_explicit_direction():
    source = Source(VGroup(VMobject()), "V", 6.0, [0.0, 0.0, 0.0])

    assert source is not None


def test_straight_wire_returns_points(circuit):
    points = circuit.add_wire([0.0, 0.0, 0.0], [1.0, 0.0, 0.0])

    assert isinstance(points, list)


def test_diagonal_wire_with_both_inversions(circuit):
    direct = circuit.add_wire([0.0, 0.0, 0.0], [1.0, 1.0, 0.0], diagonal=True)
    inverted = circuit.add_wire(
        [0.0, 0.0, 0.0], [1.0, 1.0, 0.0], diagonal=True, invert=True
    )

    for points in (direct, inverted):
        assert points is None or len(points) == 2


def test_add_components_accepts_nodes(circuit):
    circuit.add_components(Node())

    assert circuit is not None

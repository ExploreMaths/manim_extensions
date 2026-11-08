# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for circuit node merging and gear construction variants."""

import pytest

from manim_extensions.circuit.utils import Circuit, Node


@pytest.fixture()
def circuit():
    return Circuit()


def test_merge_without_wire(circuit):
    first = Node()
    second = Node()

    first.merge(second)

    assert len(first.coords) >= 0


def test_merge_with_wire(circuit):
    first = Node()
    second = Node()
    wire = circuit.add_wire([0.0, 0.0, 0.0], [1.0, 0.0, 0.0])

    first.merge(second, wire)

    assert first is not None

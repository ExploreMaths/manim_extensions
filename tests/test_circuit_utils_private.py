import numpy as np
import pytest
from manim import DOWN, UP, Line, VGroup

from manim_extensions.circuit.utils import Circuit, Node, Source


def test_source_without_label_sets_none_and_rotates():
    markings = VGroup(Line(DOWN * 0.3, UP * 0.3))
    source = Source(markings, letter="V", value=5, label=False)

    assert source.label is None
    source.rotate(0.2)
    assert source is not None


def test_source_negative_terminal_on_circle():
    source = Source(VGroup(Line(DOWN, UP)), letter="I", value=5)
    assert source.get_terminals("negative") is not None


def test_wire_creates_second_disconnected_node():
    circuit = Circuit()
    circuit.add_wire([0, 0, 0], [1, 0, 0])
    circuit.add_wire([5, 0, 0], [6, 0, 0])

    assert len(circuit.node_list) == 2


def test_wire_attaches_to_single_node_endpoint():
    circuit = Circuit()
    circuit.add_wire([0, 0, 0], [1, 0, 0])
    circuit.add_wire([1, 0, 0], [1, 1, 0])

    assert len(circuit.node_list) == 1


def test_wire_merges_two_nodes():
    circuit = Circuit()
    circuit.add_wire([0, 0, 0], [0, 1, 0])
    circuit.add_wire([1, 0, 0], [1, 1, 0])
    circuit.add_wire([0, 0, 0], [1, 0, 0])

    assert len(circuit.node_list) == 1


def test_wire_merges_three_nodes_and_adds_dots():
    circuit = Circuit()
    nodes = [Node() for _ in range(3)]
    for node in nodes:
        node.check_coord = lambda coord: True
        circuit.node_list.add(node)
    circuit.add_wire([-1, 0, 0], [3, 0, 0])

    assert len(circuit.node_list) == 1


def test_check_coord_returns_interior_coordinate():
    node = Node()
    node.add_wire([[-1, 0, 0], [1, 0, 0]])
    result = node.check_coord(np.array([0, 0, 0]))
    assert result is not False


def test_add_dot_uses_submobject():
    node = Node()
    node.add_dot([0, 0, 0])
    assert len(node.junction_dots) == 1


def test_merge_copies_junction_dots():
    first = Node()
    second = Node()
    second.add_dot([0, 0, 0])
    first.merge(second)
    assert len(first.junction_dots) == 1


def test_source_with_label_rotates_label():
    markings = VGroup(Line(DOWN * 0.3, UP * 0.3))
    source = Source(markings, letter="V", value=5)
    source.rotate(0.2)
    assert source.label is not None


def test_wire_intersects_node_interior_adds_dot():
    circuit = Circuit()
    circuit.add_wire([0, -1, 0], [0, 1, 0])
    circuit.add_wire([0, 0, 0], [1, 0, 0])

    assert len(circuit.node_list[0].junction_dots) == 1

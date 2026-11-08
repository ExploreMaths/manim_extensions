# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Construction tests for a set of small mobjects spread across packages."""

import pytest
from manim import Axes, Circle, Text, Write

from manim_extensions.chemistry.element.element import Element
from manim_extensions.economics.base import EconDiagram
from manim_extensions.machine_learning.utils.mobjects.list_group import ListGroup
from manim_extensions.machine_learning.utils.mobjects.probability import (
    GaussianDistribution,
)
from manim_extensions.physics.electromagnetism.magnetostatics import (
    MagneticField,
    Wire,
)
from manim_extensions.physics.optics.lenses import Lens
from manim_extensions.sequence_diagram.seq_action import SeqAction
from manim_extensions.table.cell import Cell


def test_cell_keeps_its_value():
    cell = Cell("value")

    assert cell.value == "value"


def test_seq_action_wraps_animations():
    action = SeqAction(Write(Text("a")))

    assert action is not None


def test_lens_is_constructible():
    lens = Lens(2.0, 0.5)

    assert lens is not None


def test_wire_and_magnetic_field():
    field = MagneticField(Wire(Circle(), 1.0))

    assert field is not None


def test_list_group_stacks_layers():
    group = ListGroup(Circle(), Circle())

    assert len(group) >= 2


def test_element_defaults_to_hydrogen():
    element = Element()

    assert element.symbol == "H"
    assert element.atomic_number == 1


@pytest.mark.parametrize("symbol,name,number", [("O", "Oxygen", 8), ("C", "Carbon", 6)])
def test_element_accepts_custom_values(symbol, name, number):
    element = Element(symbol=symbol, name=name, atomic_number=number)

    assert element.symbol == symbol
    assert element.atomic_number == number


def test_econ_diagram_builds_axes():
    diagram = EconDiagram(x_label="Q", y_label="P")

    assert diagram is not None


def test_gaussian_distribution_has_axes():
    axes = Axes(x_range=[-3, 3], y_range=[-1, 1])
    distribution = GaussianDistribution(axes)

    assert distribution.axes is axes

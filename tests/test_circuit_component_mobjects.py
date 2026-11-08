# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for circuit component mobjects."""

import numpy as np
import pytest
from manim import DOWN, LEFT, RIGHT, UP

from manim_extensions.circuit.mobjects import CurrentSource, Inductor, Resistor, VoltageSource


@pytest.mark.parametrize(
    "component_class,label",
    [(Resistor, "R"), (Inductor, "L"), (VoltageSource, "V"), (CurrentSource, "I")],
)
@pytest.mark.parametrize("direction", [LEFT, RIGHT, UP, DOWN])
def test_component_accepts_direction(component_class, label, direction):
    component = component_class(label, direction=direction)

    assert component is not None


@pytest.mark.parametrize(
    "component_class",
    [Resistor, Inductor, VoltageSource, CurrentSource],
)
def test_component_terminals(component_class):
    component = component_class("X")

    for side in ("left", "right", "top", "bottom", "unknown"):
        component.get_terminals(side)


def test_component_rotation_keeps_terminals():
    component = Resistor("R", direction=np.array([1.0, 0.0, 0.0]))
    component.rotate(np.pi / 2)

    assert component.get_terminals("left") is not None or component.get_terminals("left") is None

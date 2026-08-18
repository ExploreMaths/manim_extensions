# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT



from manim import *
from manim_extensions.circuit.mobjects import (
    Capacitor,
    CurrentSource,
    Ground,
    Inductor,
    Opamp,
    Resistor,
    VoltageSource,
)
from manim_extensions.circuit.utils import Circuit, Source


def test_circuit_objects():
    scene = Scene()
    src = Source(Circle(), "V", 5)
    assert src.get_terminals("positive") is not None
    assert src.get_terminals("negative") is not None

    vsrc = VoltageSource(1)
    csrc = CurrentSource(1)
    ind = Inductor()
    res = Resistor()
    cap = Capacitor()
    ground = Ground()
    op = Opamp()

    for component in (vsrc, csrc, ind, res, cap, ground, op):
        assert component is not None
        assert hasattr(component, "main_body")

    circuit = Circuit()
    assert hasattr(circuit, "component_list")
    assert hasattr(circuit, "node_list")

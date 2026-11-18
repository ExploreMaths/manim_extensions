# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

from manim_extensions.circuit.mobjects import Capacitor, Inductor, Opamp, Resistor


def test_inductor_anchors_center_and_rotation():
    inductor = Inductor("L")
    assert len(inductor.get_anchors()) == 2
    inductor.center()
    inductor.rotate(0.1)
    assert inductor.label is not None


def test_resistor_anchors_and_center():
    resistor = Resistor("R")
    assert len(resistor.get_anchors()) == 2
    resistor.center()
    assert resistor is not None


def test_capacitor_center():
    capacitor = Capacitor("C")
    capacitor.center()
    assert capacitor is not None


def test_opamp_both_bias_supplies_and_terminals():
    opamp = Opamp(bias_supply="both", label=True)

    assert opamp.get_terminals("positive_bias") is not None
    assert opamp.get_terminals("negative_bias") is not None

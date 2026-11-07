# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the chemistry ``future_classes`` electronic-component mobjects."""

import numpy as np
import pytest
from manim import DOWN, LEFT, RIGHT, UP, VGroup, Square

from manim_extensions.chemistry.future_classes.future_classes import (
    BatterySchema,
    BatterySide,
    Electron,
    Element,
    ElementFrame,
    Hole,
    MOSFETTransistor,
    NPNTransistor,
    arrange_in_1D_boundary,
)


@pytest.mark.parametrize("radius", [0.2, 0.25, 0.5])
def test_hole_and_electron_are_circles(radius):
    hole = Hole(radius=radius)
    electron = Electron(radius=radius)

    assert hole.width > 0
    assert electron.width > 0
    assert hole.get_center().shape == (3,)
    assert electron.get_center().shape == (3,)


@pytest.mark.parametrize("add_electrons", [True, False])
@pytest.mark.parametrize("add_holes", [True, False])
@pytest.mark.parametrize("subelectron_holes", [True, False])
def test_element_particle_switches(add_electrons, add_holes, subelectron_holes):
    element = Element(
        element="Si",
        n_electrons=2,
        n_holes=2,
        add_electrons=add_electrons,
        add_holes=add_holes,
        subelectron_holes=subelectron_holes,
    )

    assert element.element_label == "Si"
    assert element.atom is not None
    assert isinstance(element.get_particles(), VGroup)
    assert element.get_electrons() is None or isinstance(element.get_electrons(), VGroup)
    assert element.get_holes() is None or isinstance(element.get_holes(), VGroup)


@pytest.mark.parametrize("n_particles", [1, 3, 5])
def test_element_particle_counts(n_particles):
    element = Element(
        element="P",
        n_electrons=n_particles,
        n_holes=n_particles,
    )

    assert len(element.electrons) == n_particles
    assert len(element.holes) == n_particles
    assert len(element.particles) >= 2 * n_particles
    assert element.particles[0].get_center().shape == (3,)


@pytest.mark.parametrize("element", ["H", "C", "Si"])
def test_element_label_and_central_atom(element):
    mob = Element(element=element, radius=0.8)

    assert mob.central_atom() is not None
    assert mob.get_center().shape == (3,)


def test_element_frame_renders_symbol_and_name():
    frame = ElementFrame(element_symbol="Fe", element_name="Hierro")

    assert frame.frame is not None
    assert len(frame.submobjects) == 3


@pytest.mark.parametrize("regions_opacity", [0.5, 0.8, 1.0])
def test_npn_transistor_regions(regions_opacity):
    transistor = NPNTransistor(regions_opacity=regions_opacity)

    assert transistor.regions_opacity == regions_opacity
    assert len(transistor.left_electrons) >= 1
    assert len(transistor.right_electrons) >= 1
    assert len(transistor.holes) >= 1
    assert transistor.p_region.get_center().shape == (3,)


def test_npn_transistor_particle_factory():
    transistor = NPNTransistor()
    particles = transistor.make_particles(Electron)

    assert len(particles) >= 1
    assert particles[0].get_center().shape == (3,)


@pytest.mark.parametrize("schema_type", ["horizontal", "corner"])
@pytest.mark.parametrize("inverted", [True, False])
def test_battery_schema_layouts(schema_type, inverted):
    schema = BatterySchema(mob=Square(), schema_type=schema_type, inverted_terminals=inverted)

    assert schema.schema_type == schema_type
    assert schema.schema is not None
    start, finish = schema.get_start_finish_positions()
    assert start.shape == (3,)
    assert finish.shape == (3,)
    assert schema.invert_terminals() is schema


@pytest.mark.parametrize("show_holes", [True, False])
@pytest.mark.parametrize("show_battery", [True, False])
def test_mosfet_transistor_switches(show_holes, show_battery):
    mosfet = MOSFETTransistor(show_holes=show_holes, show_battery=show_battery)

    assert mosfet.main_board is not None
    assert mosfet.left_n_side is not None
    assert mosfet.right_n_side is not None
    assert mosfet.negative_terminal is not None
    assert mosfet.positive_terminal is not None
    assert mosfet.battery is not None


def test_mosfet_battery_parts():
    mosfet = MOSFETTransistor(show_battery=True)

    holes = mosfet.add_holes()
    assert holes is None or isinstance(holes, VGroup)
    assert len(mosfet.add_battery_terminals()) == 2
    assert len(mosfet.add_battery_sides()) == 2
    assert len(mosfet.battery) >= 1


def test_battery_side_connects_terminal_to_anchor():
    anchor = VGroup(Square(), Square().shift(UP))
    side = BatterySide(terminal=Square(), anchor=anchor)

    assert side.terminal is not None
    assert side.anchor is anchor
    assert side.get_num_points() >= 3


@pytest.mark.parametrize("boundary", [[LEFT, RIGHT], [DOWN, UP]])
def test_arrange_in_1d_boundary(boundary):
    mobs = VGroup(Electron(), Electron(), Electron())
    arrange_in_1D_boundary(mobs, boundary=boundary)

    assert len(mobs) == 3
    assert not np.allclose(mobs[0].get_center(), mobs[-1].get_center())

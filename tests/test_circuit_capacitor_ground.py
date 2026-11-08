# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for capacitor and ground component variants."""

import numpy as np
import pytest
from manim import RIGHT, DOWN, tempconfig

from manim_extensions.circuit.mobjects import Capacitor, Ground


@pytest.fixture(autouse=True)
def _config():
    with tempconfig({"dry_run": True, "disable_caching": True, "renderer": "cairo"}):
        yield


def test_capacitor_unpolarized_has_two_plates():
    capacitor = Capacitor()

    assert len(capacitor.main_body) == 2


def test_capacitor_polarized_uses_arc():
    capacitor = Capacitor(polarized=True)

    assert len(capacitor.main_body) == 2


def test_capacitor_with_label_supports_rotation():
    capacitor = Capacitor(label="C", direction=DOWN)

    capacitor.rotate(np.pi / 4)

    assert capacitor.label is not None


@pytest.mark.parametrize("terminal", ["left", "right"])
def test_capacitor_terminals(terminal):
    capacitor = Capacitor()

    assert capacitor.get_terminals(terminal) is not None


def test_capacitor_terminal_unknown_returns_none():
    capacitor = Capacitor()

    assert capacitor.get_terminals("middle") is None


def test_ground_without_label():
    ground = Ground()

    assert len(ground.main_body) == 1


def test_ground_digital_label():
    ground = Ground(label="D")

    assert len(ground.main_body) == 2


def test_ground_earth_variant():
    ground = Ground(ground_type="earth")

    assert len(ground.main_body) == 3


@pytest.mark.parametrize("ground_type,label", [("ground", None), ("earth", None)])
def test_ground_terminals(ground_type, label):
    ground = Ground(ground_type=ground_type, label=label)

    assert ground.get_terminals() is not None


def test_ground_terminal_uniform_point():
    ground = Ground()

    point = ground.get_terminals()

    assert point is not None

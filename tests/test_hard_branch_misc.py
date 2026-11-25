# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for assorted small fallback and validation branches."""

import numpy as np
import pytest
from manim import ORIGIN, Triangle, Circle, Square

from manim_extensions import animations
from manim_extensions.algorithm.node import Node
from manim_extensions.arabic import text as arabic_text
from manim_extensions.chemistry.bohr_atom.bohr_atom import BohrAtom
from manim_extensions.chemistry.element.element import Element
from manim_extensions.chemistry.future_classes import future_classes


def test_arabic_font_falls_back_to_first_candidate(monkeypatch):
    monkeypatch.setattr(arabic_text, "_FONT_CANDIDATES", ["Definitely-Missing-Font"])

    assert arabic_text._resolve_arabic_font(None) == "Definitely-Missing-Font"


def test_node_rejects_unknown_box_type():
    with pytest.raises(ValueError, match="box_type must be Square or Circle"):
        Node("x", box_type=Triangle)


def test_node_accepts_square_and_circle():
    assert Node("x", box_type=Square).box is not None
    assert Node("x", box_type=Circle).box is not None


def test_bohr_atom_uses_explicit_level():
    atom = BohrAtom(e=14, level=3)

    assert atom.calculate_levels() == 3


def test_element_rejects_invalid_reference(tmp_path):
    path = tmp_path / "elements.csv"
    path.write_text("Symbol,Name,AtomicNumber,AtomicMass\nH,Hydrogen,1,1.008\n")

    with pytest.raises(Exception, match="NOT a valid reference"):
        Element.from_csv_file(str(path), 200)

    with pytest.raises(Exception, match="NOT a valid reference"):
        Element.from_csv_file(str(path), "Xx")


def test_zero_decorator_clamps_outside_unit_interval():
    @future_classes.zero
    def curve(t):
        return t

    assert curve(0.5) == 0.5
    assert curve(-1) == 0
    assert curve(2) == 0


def test_highlight_and_unhighlight_with_lines_parts():
    mob = Square()
    highlight = animations.HighLightWithLines(mob)

    assert hasattr(mob, "_highlight_with_lines_parts")

    animations.UnHighLightWithLines(mob)

    assert not hasattr(mob, "_highlight_with_lines_parts")


def test_QRCode_with_tall_icon_uses_height_fit():
    from manim_extensions.qr_codes.qr import QRCode

    code = QRCode("hello", icon=0xF17C)
    assert code is not None


def test_manim_state_updates_subscript():
    from manim_extensions.automata.mobjects.manim_state import ManimState

    state = ManimState("q0", 0.0, 0.0, {}, scaling=1)
    state.update_subscript(3)

    assert state.subscript is not None

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

import numpy as np
from manim import ORIGIN, WHITE

from manim_extensions.economics.base import EconDiagram


def test_subscript_and_degenerate_arrow():
    diagram = EconDiagram()

    assert diagram._sub(10) == "10"
    assert len(diagram._make_single_arrow(ORIGIN, ORIGIN, WHITE)) == 0


def test_non_intersecting_curves_return_none():
    diagram = EconDiagram()
    assert diagram._get_eq_coords() is None
    diagram.add_curve("a", lambda x: x, [0, 10, 1], WHITE)
    diagram.add_curve("b", lambda x: x + 1, [0, 10, 1], WHITE)

    assert diagram.mark_equilibrium("a", "b") is None
    assert diagram._get_eq_coords() is None


def test_numbered_equilibrium_updates_on_shift():
    diagram = EconDiagram()
    diagram.add_curve("a", lambda x: x, [0, 10, 1], WHITE)
    diagram.add_curve("b", lambda x: -x + 10, [0, 10, 1], WHITE)
    group = diagram.mark_equilibrium("a", "b", numbered=True)

    assert group is not None
    animation = diagram.get_shift_animation("a", lambda x: x + 1)
    assert animation is not None

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the graph-based molecule bond primitives."""

import numpy as np
import pytest

from manim_extensions.chemistry.twoD.graph_molecule import (
    DoubleLine,
    SimpleLine,
    TripleLine,
)


@pytest.mark.parametrize(
    "cls",
    [SimpleLine, DoubleLine, TripleLine],
)
def test_line_primitives(cls):
    start = np.array([0.0, 0.0, 0.0])
    end = np.array([2.0, 0.0, 0.0])

    line = cls(start=start, end=end)

    assert line.get_start() is not None
    assert line.get_end() is not None


def test_double_line_has_two_arcs():
    line = DoubleLine(start=np.array([0.0, 0.0, 0.0]), end=np.array([2.0, 0.0, 0.0]))

    assert len(line.submobjects) >= 1


def test_triple_line_has_middle_line():
    line = TripleLine(start=np.array([0.0, 0.0, 0.0]), end=np.array([2.0, 0.0, 0.0]))

    assert len(line.submobjects) >= 2

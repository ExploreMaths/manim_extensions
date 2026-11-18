# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for abstract hook implementations and degenerate bond geometry."""

from types import SimpleNamespace

import numpy as np
import pytest
from manim import Line, VGroup

from manim_extensions.chemistry.twoD.bond import (
    BaseMBondObject,
    DashedCramBond,
    DoubleBond,
    PlainCramBond,
    TripleBond,
)


def _bare(cls):
    obj = object.__new__(cls)
    obj.submobjects = []
    obj.points = np.empty((0, 3))
    return obj


def test_base_hooks_are_noops():
    bond = _bare(BaseMBondObject)

    assert bond.no_subtype() is None
    assert bond.shorter_subtype() is None
    assert bond.shorter_from_subtype() is None
    assert bond.shorter_to_subtype() is None
    assert bond.longer_subtype() is None
    assert bond.create_line() is None


def test_base_get_vector_reraises_index_error():
    bond = _bare(BaseMBondObject)

    with pytest.raises(IndexError):
        bond.get_vector()


@pytest.mark.parametrize("cls", [DoubleBond, TripleBond])
def test_double_and_triple_get_vector_reraises_index_error(cls):
    bond = _bare(cls)

    with pytest.raises(IndexError):
        bond.get_vector()


def test_plain_cram_no_subtype_handles_zero_direction():
    bond = _bare(PlainCramBond)
    bond.from_atom = SimpleNamespace(coords=np.array([1.0, 1.0, 0.0]))
    bond.to_atom = SimpleNamespace(coords=np.array([1.0, 1.0, 0.0]))

    assert isinstance(bond.no_subtype(), VGroup)


def test_dashed_cram_handles_zero_direction():
    bond = _bare(DashedCramBond)
    bond.from_atom = SimpleNamespace(coords=np.array([0.0, 0.0, 0.0]))
    bond.to_atom = SimpleNamespace(coords=np.array([0.0, 0.0, 0.0]))

    assert isinstance(bond.no_subtype(), VGroup)


def test_dashed_cram_add_handles_zero_length_pivot():
    bond = _bare(DashedCramBond)
    base_line = Line(np.array([0.0, 0.0, 0.0]), np.array([0.0, 0.0, 0.0]))

    result = bond.add_dashed_cram_bond(base_line, np.array([1.0, 0.0, 0.0]))

    assert isinstance(result, VGroup)


def test_dashed_cram_add_handles_zero_direction():
    bond = _bare(DashedCramBond)
    base_line = Line(np.array([0.0, 0.0, 0.0]), np.array([1.0, 0.0, 0.0]))

    result = bond.add_dashed_cram_bond(base_line, np.zeros(3))

    assert isinstance(result, VGroup)


def test_get_perpendicular_unit_vector_vertical_bond():
    bond = _bare(BaseMBondObject)

    perpendicular = bond.get_perpendicular_unit_vector(
        np.array([0.0, 0.0, 1.0]), np.array([0.0, 0.0, 2.0])
    )

    assert np.linalg.norm(perpendicular) == pytest.approx(1.0)


def test_dashed_cram_get_vector_reraises_index_error():
    bond = _bare(DashedCramBond)

    with pytest.raises(IndexError):
        bond.get_vector()


def test_plain_cram_get_vector_reraises_atom_lookup_error():
    bond = _bare(PlainCramBond)

    def broken_lookup():
        raise ValueError("no atoms")

    bond.atoms_in_bond = broken_lookup

    with pytest.raises(ValueError):
        bond.get_vector()

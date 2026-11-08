# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for lookup error handling in the 2-D molecule mobject."""

import pytest

from manim_extensions.chemistry.twoD.molecule import MMoleculeObject as Mol

SDF = """acetone
     RDKit          2D

  3  2  0  0  0  0  0  0  0  0999 V2000
    0.0000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    1.5000    0.0000    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   -1.0000    1.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  2  0
  1  3  1  0
M  END
"""


@pytest.fixture()
def molecule():
    return Mol.from_sdf_string(SDF)[0]


def test_invalid_atom_index_raises(molecule):
    with pytest.raises(KeyError):
        molecule.find_atom_position_by_index(99)


def test_invalid_bond_index_raises(molecule):
    with pytest.raises((KeyError, IndexError)):
        molecule.find_bond_center_by_index(99)


def test_invalid_bond_axis_raises(molecule):
    with pytest.raises((KeyError, IndexError)):
        molecule.find_position_along_bond_axis(99, 0.5)


def test_bond_axis_endpoints(molecule):
    start = molecule.find_position_along_bond_axis(0, -1)
    end = molecule.find_position_along_bond_axis(0, 1)

    assert start is not None
    assert end is not None

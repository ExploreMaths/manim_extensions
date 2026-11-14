# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for drawing double, triple and aromatic bonds from SDF data."""

import pytest

from manim_extensions.chemistry.twoD.molecule import MMoleculeObject as Mol

ETHENE = """ethene
     RDKit          2D

  2  1  0  0  0  0  0  0  0  0999 V2000
    0.0000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    1.5000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  2  0
M  END
"""

ETHYNE = """ethyne
     RDKit          2D

  2  1  0  0  0  0  0  0  0  0999 V2000
    0.0000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    1.5000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  3  0
M  END
"""

BENZENE = """benzene
     RDKit          2D

  6  6  0  0  0  0  0  0  0  0999 V2000
    1.0000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    0.5000    0.8660    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   -0.5000    0.8660    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   -1.0000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   -0.5000   -0.8660    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    0.5000   -0.8660    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  4  0
  2  3  4  0
  3  4  4  0
  4  5  4  0
  5  6  4  0
  6  1  4  0
M  END
"""


@pytest.mark.parametrize("sdf", [ETHENE, ETHYNE, BENZENE])
def test_bond_group_built_for_bond_orders(sdf):
    molecule = Mol.from_sdf_string(sdf)[0]

    bonds = molecule.bonds

    assert len(bonds) == len(molecule.bonds)


@pytest.mark.parametrize("sdf", [ETHENE, ETHYNE])
def test_bond_axis_positions_for_multiple_bonds(sdf):
    molecule = Mol.from_sdf_string(sdf)[0]

    center = molecule.find_bond_center_by_index(0)
    along_axis = molecule.find_position_along_bond_axis(0, 0.25)

    assert center is not None
    assert along_axis is not None

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for molecule lookups on missing atoms and bonds."""

import pytest
from manim import tempconfig

from manim_extensions.chemistry.twoD.molecule import MMoleculeObject

MOL = """acetone
     RDKit          2D

  6  5  0  0  0  0  0  0  0  0999 V2000
    0.0000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    1.2990    0.7500    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   -1.2990    0.7500    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    0.0000    1.5000    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
   -2.0000    0.0000    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
    1.5000    1.5000    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  2  0
  1  3  1  0
  3  4  1  0
  3  5  1  0
  1  6  1  0
M  END
"""


@pytest.fixture(autouse=True)
def _config():
    with tempconfig({"dry_run": True, "disable_caching": True, "renderer": "cairo"}):
        yield


@pytest.fixture()
def molecule():
    return MMoleculeObject.molecule_from_string(MOL, format="mol")


def test_missing_atom_position_raises(molecule):
    with pytest.raises(Exception):
        molecule.find_atom_position_by_index("missing")


def test_missing_bond_center_raises(molecule):
    with pytest.raises(Exception):
        molecule.find_bond_center_by_index("missing")


def test_missing_position_along_bond_axis_raises(molecule):
    with pytest.raises(Exception):
        molecule.find_position_along_bond_axis("missing", 0.5)


def test_missing_atoms_positions_raises(molecule):
    with pytest.raises(Exception):
        molecule.find_atoms_position_by_index(["missing"])


def test_missing_bonds_center_raises(molecule):
    with pytest.raises(Exception):
        molecule.find_bonds_center_by_index(["missing"])

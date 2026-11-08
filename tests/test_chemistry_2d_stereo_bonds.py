# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for MOL stereo bond parsing into Cram bond objects."""

import pytest
from manim import tempconfig

from manim_extensions.chemistry.twoD.bond import DashedCramBond, PlainCramBond, SimpleBond
from manim_extensions.chemistry.twoD.molecule import MMoleculeObject

WEDGE_MOL = """wedge
     RDKit          2D

  4  3  0  0  0  0  0  0  0  0999 V2000
    0.0000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    1.2990    0.7500    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   -1.2990    0.7500    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
    0.0000    1.5000    0.0000 Cl  0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  1
  1  3  1  6
  1  4  1  0
M  END
"""


@pytest.fixture(autouse=True)
def _config():
    with tempconfig({"dry_run": True, "disable_caching": True, "renderer": "cairo"}):
        yield


def test_stereo_bonds_map_to_cram_bond_classes():
    molecule = MMoleculeObject.molecule_from_string(WEDGE_MOL, format="mol")

    bond_types = [type(bond) for bond in molecule.bonds]

    assert PlainCramBond in bond_types
    assert DashedCramBond in bond_types
    assert SimpleBond in bond_types


def test_wedge_and_hash_bonds_have_lines():
    molecule = MMoleculeObject.molecule_from_string(WEDGE_MOL, format="mol")

    cram_bonds = [
        bond
        for bond in molecule.bonds
        if isinstance(bond, (PlainCramBond, DashedCramBond))
    ]

    assert cram_bonds
    assert all(len(bond.submobjects) >= 1 for bond in cram_bonds)

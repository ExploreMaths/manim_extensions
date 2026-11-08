# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for converting MC molecules into 3-D atom and bond dictionaries."""

import pytest
from manim import tempconfig

from manim_extensions.chemistry.manim_chemistry_molecule.mc_molecule import MCMolecule
from manim_extensions.chemistry.threeD.threedmolecule import ThreeDMolecule

MOL = """acetone
     RDKit          3D

  6  5  0  0  0  0  0  0  0  0999 V2000
    0.0000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    1.2000    0.0000    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   -1.0000    0.9000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
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
    with tempconfig({"renderer": "opengl", "window": False, "dry_run": True}):
        yield


def test_conversion_produces_atoms_and_bonds():
    mc_molecule = MCMolecule.construct_from_string(MOL, format="mol")

    atoms, bonds = ThreeDMolecule.mc_molecule_to_atoms_and_bonds(mc_molecule)

    assert len(atoms) == 3
    assert len(bonds) == 1


def test_converted_data_builds_molecule():
    mc_molecule = MCMolecule.construct_from_string(MOL, format="mol")
    atoms, bonds = ThreeDMolecule.mc_molecule_to_atoms_and_bonds(mc_molecule)

    molecule = ThreeDMolecule(atoms_dict=atoms, bonds_dict=bonds, source_csv=None)

    assert len(molecule.submobjects) >= 1

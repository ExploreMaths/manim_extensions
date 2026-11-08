# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the OpenGL 3-D molecule mobject."""

import pytest
from manim import tempconfig

from manim_extensions.chemistry.element.element import Element
from manim_extensions.chemistry.threeD.threedmolecule import ThreeDMolecule
from manim_extensions.chemistry.utils.utils import mol_parser_string

MOL = """acetone
     RDKit          3D

  3  2  0  0  0  0  0  0  0  0999 V2000
    0.0000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    1.2000    0.0000    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   -1.0000    0.9000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  2  0
  1  3  1  0
M  END
"""

ELEMENTS = {
    "C": Element("C", "Carbon", 6, 12.011, "#909090"),
    "O": Element("O", "Oxygen", 8, 15.999, "#FF0D0D"),
}


@pytest.fixture()
def mol_data():
    atoms, bonds = mol_parser_string(MOL.splitlines())
    for atom in atoms.values():
        atom["element"] = ELEMENTS[atom["element"]]
    return atoms, bonds


def test_molecule_is_constructed(mol_data):
    atoms, bonds = mol_data
    with tempconfig({"renderer": "opengl", "window": False}):
        molecule = ThreeDMolecule(atoms_dict=atoms, bonds_dict=bonds, source_csv=None)

        assert len(molecule.submobjects) >= 1


def test_atom_and_bond_groups_are_built(mol_data):
    atoms, bonds = mol_data
    with tempconfig({"renderer": "opengl", "window": False}):
        molecule = ThreeDMolecule(atoms_dict=atoms, bonds_dict=bonds, source_csv=None)

        assert molecule.get_atoms_from_csv() is not None
        assert molecule.get_bonds() is not None


def test_molecule_without_atoms_or_bonds_flag(mol_data):
    atoms, bonds = mol_data
    with tempconfig({"renderer": "opengl", "window": False}):
        molecule = ThreeDMolecule(
            atoms_dict=atoms,
            bonds_dict=bonds,
            source_csv=None,
            add_bonds=False,
            add_atoms=False,
        )

        assert molecule is not None

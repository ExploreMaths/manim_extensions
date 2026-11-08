# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for MC atom and bond assignment validation."""

import pytest

from manim_extensions.chemistry.manim_chemistry_molecule.mc_atom import MCAtom
from manim_extensions.chemistry.manim_chemistry_molecule.mc_bond import MCBond
from manim_extensions.chemistry.manim_chemistry_molecule.mc_element import MCElement


@pytest.fixture()
def carbon():
    return MCElement("C", "Carbon", 6, 12.011, "#909090")


def test_add_atoms_accepts_single_atom_and_list(carbon):
    atom = MCAtom(carbon)
    other = MCAtom(carbon)
    other.add_atoms(atom)

    atom.add_atoms([other])

    assert len(atom.atoms) >= 1


def test_add_atoms_rejects_other_type(carbon):
    atom = MCAtom(carbon)

    with pytest.raises(Exception):
        atom.add_atoms("not an atom")


def test_add_bonds_rejects_other_type(carbon):
    atom = MCAtom(carbon)

    with pytest.raises(Exception):
        atom.add_bonds("not a bond")


def test_add_bonds_accepts_bond_and_list(carbon):
    atom = MCAtom(carbon)
    other = MCAtom(carbon)
    bond = MCBond(1, from_atom=atom, to_atom=other)

    atom.add_bonds(bond)
    atom.add_bonds([bond])

    assert len(atom.bonds) >= 1


def test_assign_molecule_rejects_other_type(carbon):
    atom = MCAtom(carbon)

    with pytest.raises(Exception):
        atom.assign_molecule("not a molecule")


def test_assign_molecule_index_rejects_non_int(carbon):
    atom = MCAtom(carbon)

    with pytest.raises(Exception):
        atom.assign_molecule_index("1")

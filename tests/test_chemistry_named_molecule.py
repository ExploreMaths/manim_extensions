# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the named-molecule wrapper and its geometry helpers."""

import numpy as np
import pytest

from manim_extensions.chemistry.twoD.molecule import MMoleculeObject, NamedMolecule

MOL = (
    "acetone\n"
    "  Mrv2014 03011512422D\n"
    "\n"
    "  6  5  0  0  0  0            999 V2000\n"
    "    0.0000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0\n"
    "    1.2990   -0.7500    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0\n"
    "    2.5981    0.0000    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0\n"
    "   -0.6495   -1.1250    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0\n"
    "   -0.6495    1.1250    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0\n"
    "    1.2990   -2.2500    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0\n"
    "  1  2  1\n"
    "  2  3  2\n"
    "  1  4  1\n"
    "  1  5  1\n"
    "  2  6  1\n"
    "M  END\n"
)


@pytest.fixture()
def named_molecule():
    molecule = MMoleculeObject.molecule_from_string(MOL, format="mol")
    return NamedMolecule("Acetone", molecule)


def test_named_molecule_collects_label(named_molecule):
    assert len(named_molecule.atoms) == 3
    assert len(named_molecule.bonds) == 2
    assert len(named_molecule.submobjects) == 2


def test_single_index_lookups(named_molecule):
    atom_position = named_molecule.find_atom_position_by_index(1)
    bond_center = named_molecule.find_bond_center_by_index(0)
    along_axis = named_molecule.find_position_along_bond_axis(0, 0.5)

    for value in (atom_position, bond_center, along_axis):
        assert isinstance(value, np.ndarray)
        assert value.shape[-1] == 3


def test_list_index_lookups(named_molecule):
    assert len(named_molecule.find_atoms_position_by_index([1, 2])) == 2
    assert len(named_molecule.find_bonds_center_by_index([0, 1])) == 2


def test_all_positions_are_mapped(named_molecule):
    assert len(named_molecule.find_all_atoms_positions()) == len(named_molecule.atoms)
    assert len(named_molecule.find_all_bonds_centers()) == len(named_molecule.bonds)


def test_numbering_and_rotation_return_self(named_molecule):
    assert named_molecule.add_atom_numbering() is named_molecule
    assert named_molecule.add_bond_numbering() is named_molecule
    assert named_molecule.rotate_bond(0) is named_molecule


def test_from_mol_file(tmp_path, named_molecule):
    path = tmp_path / "acetone.mol"
    path.write_text(MOL)

    loaded = NamedMolecule.from_mol_file("Acetone", str(path))

    assert len(loaded.atoms) >= len(named_molecule.atoms)
    assert len(loaded.bonds) >= len(named_molecule.bonds)

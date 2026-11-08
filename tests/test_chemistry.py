# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Behaviour tests for the vendored chemistry toolkit.

These exercise the molecule builders that ship with the package: parsing
MOL/SDF data, the representation switches, the numbering and position
helpers, and the bond subtypes reached through those builders.
"""

import numpy as np
import pytest
from manim import DOWN, LEFT, RIGHT, UP

from manim_extensions.chemistry.twoD.atom import MAtomObject
from manim_extensions.chemistry.twoD.bond import (
    DoubleBond,
    PlainCramBond,
    SimpleBond,
    TripleBond,
)
from manim_extensions.chemistry.twoD.molecule import MMoleculeObject, NamedMolecule
from manim_extensions.chemistry.utils.parsers.mol_parser import MolParser
from manim_extensions.chemistry.utils.parsers.sdf_parser import SDFParser


def build_mol(atoms, bonds):
    """Assemble a MOL V2000 block from atom and bond rows."""
    lines = ["molecule", "  manim", ""]
    lines.append("%3d%3d  0  0  0  0  0  0  0  0999 V2000" % (len(atoms), len(bonds)))
    for row in atoms:
        lines.append(
            "  ".join(str(value) for value in row) + "  0  0  0  0  0  0  0  0  0  0"
        )
    for row in bonds:
        lines.append("  ".join(str(value) for value in row) + "  0  0  0  0")
    lines.append("M  END")
    return "\n".join(lines) + "\n"


WATER_ATOMS = [
    (0.0, 0.0, 0.0, "O"),
    (1.05, 0.0, 0.0, "H"),
    (-1.05, 0.0, 0.0, "H"),
]
WATER_BONDS = [
    (1, 2, 1),
    (1, 3, 1),
]

ETHENE_ATOMS = [
    (0.0, 0.0, 0.0, "C"),
    (1.33, 0.0, 0.0, "C"),
    (-0.7, 1.0, 0.0, "H"),
    (2.03, 1.0, 0.0, "H"),
    (-0.9, 0.9, 0.0, "H"),
    (1.9, -1.0, 0.0, "H"),
]
ETHENE_BONDS = [
    (1, 2, 2),
    (1, 3, 1),
    (1, 5, 1),
    (2, 4, 1),
    (2, 6, 1),
]

ACETYLENE_ATOMS = [
    (0.0, 0.0, 0.0, "C"),
    (1.2, 0.0, 0.0, "C"),
    (-0.6, 0.0, 0.0, "H"),
    (1.8, 0.0, 0.0, "H"),
]
ACETYLENE_BONDS = [
    (1, 2, 3),
    (1, 3, 1),
    (2, 4, 1),
]

WEDGED_ATOMS = [
    (0.0, 0.0, 0.0, "C"),
    (1.0, 1.0, 0.0, "O"),
    (-1.0, 1.0, 0.0, "C"),
]
WEDGED_BONDS = [
    (1, 2, 1),
    (1, 3, 4),
]


def water():
    """Return a parsed water molecule."""
    return MMoleculeObject.from_mol_string(build_mol(WATER_ATOMS, WATER_BONDS))


def test_from_mol_string_builds_atoms_and_bonds():
    molecule = water()

    assert len(molecule.atoms_dict) == 3
    # ``bonds_dict`` is keyed by the first atom of each bond.
    assert len(molecule.bonds_dict) == 1
    assert len(molecule.atoms) == 3
    assert molecule.atoms[1].element == "O"
    assert len(molecule.atoms_by_index) == 3
    assert isinstance(molecule.bonds, type(molecule.bonds))


def test_get_atoms_returns_attr_objects():
    molecule = water()
    atoms, index_map = molecule.get_atoms()

    assert len(atoms) == 3
    for atom in atoms:
        assert isinstance(atom, MAtomObject)
    assert index_map[1] is atoms[1]


@pytest.mark.parametrize("representation", ["complete", "skeleton", "over_bond"])
def test_representation_type_accepts_each_mode(representation):
    molecule = MMoleculeObject.from_mol_string(
        build_mol(WATER_ATOMS, WATER_BONDS), representation_type=representation
    )

    assert molecule.representation_type == representation
    assert len(molecule.atoms) == 3


@pytest.mark.parametrize("explicit_carbons", [True, False])
@pytest.mark.parametrize("explicit_hydrogens", [True, False])
def test_explicit_switch_flags(explicit_carbons, explicit_hydrogens):
    molecule = MMoleculeObject.from_mol_string(
        build_mol(ETHENE_ATOMS, ETHENE_BONDS),
        explicit_carbons=explicit_carbons,
        explicit_hydrogens=explicit_hydrogens,
    )

    assert molecule.explicit_carbons is explicit_carbons
    assert molecule.explicit_hydrogens is explicit_hydrogens


def test_numbering_helpers_add_labels():
    molecule = MMoleculeObject.from_mol_string(
        build_mol(WATER_ATOMS, WATER_BONDS),
        add_atoms_numbering=True,
        add_bonds_numbering=True,
    )

    assert molecule.find_atom_position_by_index(1) is not None
    assert molecule.find_bond_center_by_index(1) is not None
    assert len(molecule.find_all_atoms_positions()) == 3
    assert len(molecule.find_all_bonds_centers()) == 2


def test_rotate_bond_accepts_single_index_and_list():
    single = MMoleculeObject.from_mol_string(
        build_mol(WATER_ATOMS, WATER_BONDS), rotate_bonds=1
    )
    many = MMoleculeObject.from_mol_string(
        build_mol(ETHENE_ATOMS, ETHENE_BONDS), rotate_bonds=[1, 2]
    )

    assert len(single.atoms) == 3
    assert len(many.atoms) == 6


def test_position_helpers_return_points_and_groups():
    molecule = water()

    assert molecule.find_atom_position_by_index(1).shape == (3,)
    positions = molecule.find_atoms_position_by_index([1, 2])
    assert len(positions) == 2
    center = molecule.find_bond_center_by_index(1)
    assert center.shape == (3,)
    centers = molecule.find_bonds_center_by_index([0, 1])
    assert len(centers) == 2
    along = molecule.find_position_along_bond_axis(1, 0.5)
    assert along.shape == (3,)
    assert len(molecule.find_all_atoms_positions()) == 3
    assert len(molecule.find_all_bonds_centers()) == 2


@pytest.mark.parametrize("bond_type", [1, 2, 3, 4])
def test_bond_types_construct_subclasses(bond_type):
    atoms = list(WATER_ATOMS)
    bonds = [(1, 2, bond_type)]
    molecule = MMoleculeObject.from_mol_string(build_mol(atoms, bonds))

    assert len(molecule.bonds) == 1
    bond = molecule.bonds[0]
    assert bond.atoms_in_bond() is not None


def test_named_molecule_places_a_label():
    named = NamedMolecule.from_mol_string("Water", build_mol(WATER_ATOMS, WATER_BONDS))

    assert len(named.submobjects) == 2
    assert named.molecule is not None
    assert len(named.molecule.atoms) == 3


@pytest.mark.parametrize("tex", [True, False])
@pytest.mark.parametrize("direction", [DOWN, UP, LEFT, RIGHT])
def test_named_molecule_direction_and_tex(tex, direction):
    named = NamedMolecule.from_mol_string(
        "H2O",
        build_mol(WATER_ATOMS, WATER_BONDS),
        direction=direction,
        tex=tex,
        font="",
    )

    assert named.molecule is not None
    assert len(named.submobjects) == 2


def test_mol_parser_from_string_returns_raw_data():
    atoms, bonds = MolParser.parse_from_string(build_mol(WATER_ATOMS, WATER_BONDS))

    assert atoms[1]["element"] == "O"
    assert np.allclose(atoms[1]["coords"], [0.0, 0.0, 0.0])
    assert bonds[1]["to_atom_index"] == 1
    assert bonds[1]["from_atom_index"] == 2


def test_sdf_parser_reads_multiple_molecules(tmp_path):
    block = build_mol(WATER_ATOMS, WATER_BONDS)
    path = tmp_path / "two.sdf"
    path.write_text(block.rstrip("\n") + "$$$$" + block + "$$$$", encoding="utf-8")

    molecules = SDFParser(filename=str(path)).molecular_data

    assert len(molecules) == 2
    assert len(molecules[0][0]) == 3


def test_sdf_string_builds_molecule_list():
    block = build_mol(WATER_ATOMS, WATER_BONDS)
    molecules = MMoleculeObject.from_sdf_string(block + "$$$$\n")

    assert len(molecules) == 1
    assert len(molecules[0].atoms) == 3


def test_mol_file_round_trip(tmp_path):
    path = tmp_path / "water.mol"
    path.write_text(build_mol(WATER_ATOMS, WATER_BONDS), encoding="utf-8")

    molecule = MMoleculeObject.from_mol_file(str(path))

    assert len(molecule.atoms) == 3


def test_bond_subtypes_build_lines_and_groups():
    atom_a = MAtomObject(coords=np.array([0.0, 0.0, 0.0]), element="C", index=1)
    atom_b = MAtomObject(coords=np.array([1.0, 0.0, 0.0]), element="C", index=2)

    simple = SimpleBond(atom_a, atom_b)
    double = DoubleBond(atom_a, atom_b)
    triple = TripleBond(atom_a, atom_b)
    cram = PlainCramBond(atom_a, atom_b)

    assert simple.atoms_in_bond() == (atom_a, atom_b)
    assert simple.atom_is_in_bond(atom_a) is True
    assert simple.get_bond_index_by_atom(atom_a) is not None
    assert simple.get_vector() is not None
    assert len(double) >= 1
    assert len(triple) >= 1
    assert len(cram) >= 1
    assert str(simple) is not None
    assert repr(simple) is not None

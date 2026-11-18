import numpy as np
import pytest

from manim_extensions.chemistry.manim_chemistry_molecule.mc_atom import MCAtom


def _atom():
    return MCAtom.construct_from_atom_dict(0, {"element": "C", "coords": [0, 0, 0]}, {})


def test_assign_atoms_and_bonds_reject_wrong_types():
    atom = _atom()
    atom.add_atoms([])
    atom.add_bonds([])

    with pytest.raises(Exception):
        atom.add_atoms("bad")
    with pytest.raises(Exception):
        atom.add_bonds("bad")
    with pytest.raises(Exception):
        atom.add_bonds(["bad"])


def test_assign_atoms_rejects_bad_list():
    atom = _atom()
    with pytest.raises(Exception):
        atom.add_atoms(["bad"])


def test_assign_molecule_and_index():
    from manim_extensions.chemistry.manim_chemistry_molecule.mc_molecule import (
        MCMolecule,
    )

    class FalsyMolecule(MCMolecule):
        def __bool__(self):
            return False

    atom = _atom()
    atom.assign_molecule(FalsyMolecule())
    atom.assign_molecule_index(0)
    with pytest.raises(Exception):
        atom.assign_molecule_index(None)

    with pytest.raises(Exception):
        atom.assign_molecule("bad")
    with pytest.raises(Exception):
        atom.assign_molecule_index("bad")


def test_construct_from_atom_dict_rejects_bad_inputs():
    with pytest.raises(Exception):
        MCAtom.construct_from_atom_dict(0, ["not", "a", "dict"], {})
    with pytest.raises(Exception):
        MCAtom.construct_from_atom_dict(0, {"coords": [0, 0, 0]}, {})
    with pytest.raises(Exception):
        MCAtom.construct_from_atom_dict(0, {"element": "Xx", "coords": [0, 0, 0]}, {})
    with pytest.raises(Exception):
        MCAtom.construct_from_atom_dict(0, {"element": "C", "coords": "bad"}, {})


def test_construct_from_atom_dict_merges_extra_elements():
    atom = MCAtom.construct_from_atom_dict(
        1,
        {"element": "C", "coords": np.array([0.0, 0.0, 0.0])},
        {"C": _atom().element},
    )

    assert atom.molecule_index == 1

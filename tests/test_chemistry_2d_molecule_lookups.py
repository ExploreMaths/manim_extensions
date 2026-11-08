# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for missing hydrogen completion, numbering and atom lookups."""

import pytest
from manim import tempconfig

from manim_extensions.chemistry.twoD.molecule import MMoleculeObject

# Amine with the nitrogen on the left of the carbon: hydrogens go to the left.
AMINE_LEFT = """amine
     RDKit          2D

  2  1  0  0  0  0  0  0  0  0999 V2000
    0.0000    0.0000    0.0000 N   0  0  0  0  0  0  0  0  0  0  0  0
   -1.0000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  0
M  END
"""

# Amine with the nitrogen on the right of the carbon: hydrogens go to the right.
AMINE_RIGHT = """amine
     RDKit          2D

  2  1  0  0  0  0  0  0  0  0999 V2000
    0.0000    0.0000    0.0000 N   0  0  0  0  0  0  0  0  0  0  0  0
    1.0000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  0
M  END
"""

# An oxygen bound once: exactly one hydrogen has to be added.
METHANOL = """methanol
     RDKit          2D

  2  1  0  0  0  0  0  0  0  0999 V2000
    1.0000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   -0.2000    0.0000    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  0
M  END
"""


@pytest.fixture(autouse=True)
def _config():
    with tempconfig({"dry_run": True, "disable_caching": True, "renderer": "cairo"}):
        yield


def test_complete_missing_hydrogens_prefixes_hydrogen():
    molecule = MMoleculeObject.from_mol_string(AMINE_LEFT)

    molecule.complete_missing_hydrogens()

    assert "H<sub>2</sub>N" in [atom.element for atom in molecule.atoms]


def test_complete_missing_hydrogens_suffixes_hydrogen():
    molecule = MMoleculeObject.from_mol_string(AMINE_RIGHT)

    molecule.complete_missing_hydrogens()

    assert "NH<sub>2</sub>" in [atom.element for atom in molecule.atoms]


def test_complete_missing_hydrogens_single_hydrogen():
    molecule = MMoleculeObject.from_mol_string(METHANOL)

    molecule.complete_missing_hydrogens()

    elements = [atom.element for atom in molecule.atoms]

    assert "HO" in elements or "OH" in elements


def test_atom_numbering_with_explicit_hydrogens():
    molecule = MMoleculeObject.from_mol_string(METHANOL, explicit_hydrogens=True)
    before = len(molecule.submobjects)

    molecule.add_atom_numbering()

    assert len(molecule.submobjects) > before


def test_find_atom_position_unknown_key():
    molecule = MMoleculeObject.from_mol_string(METHANOL)

    with pytest.raises(KeyError):
        molecule.find_atom_position_by_index("unknown")

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the 2-D molecule helper methods."""

from pathlib import Path

import numpy as np
import pytest
from manim import VGroup

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


@pytest.fixture()
def molecule():
    return MMoleculeObject.molecule_from_string(MOL, format="mol")


def test_get_bonds_returns_vgroup(molecule):
    bonds = molecule.bonds

    assert isinstance(bonds, VGroup)
    assert len(bonds) == len(molecule.bonds)


def test_add_atom_numbering(molecule):
    molecule.add_atom_numbering()

    assert len(molecule.submobjects) > 0


def test_complete_missing_hydrogens(molecule):
    molecule.complete_missing_hydrogens()

    assert len(molecule.atoms) >= 3


def test_find_atom_position_by_index(molecule):
    position = molecule.find_atom_position_by_index(1)

    assert np.shape(position) in {(3,), (1, 3)}


def test_from_sdf_file(tmp_path: Path):
    path = tmp_path / "acetone.sdf"
    path.write_text(MOL, encoding="utf-8")

    molecules = MMoleculeObject.from_sdf_file(str(path))

    assert isinstance(molecules, list)
    assert len(molecules[0].atoms) > 0

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for GraphMolecule construction from a MOL file."""

import pytest
from manim import tempconfig

from manim_extensions.chemistry.twoD.graph_molecule import GraphMolecule

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
def mol_path(tmp_path):
    path = tmp_path / "acetone.mol"
    path.write_text(MOL)
    return str(path)


def test_molecule_from_file(mol_path):
    molecule = GraphMolecule.molecule_from_file(mol_path)

    assert len(molecule.vertices) == 3


def test_molecule_from_file_with_hydrogens(mol_path):
    molecule = GraphMolecule.molecule_from_file(mol_path, ignore_hydrogens=False)

    assert len(molecule.vertices) >= 3

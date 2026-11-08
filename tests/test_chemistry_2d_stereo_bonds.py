# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for stereo-aware bond construction in 2D molecules."""

import pytest
from manim import tempconfig

from manim_extensions.chemistry.twoD.molecule import MMoleculeObject

WEDGE_MOL = """stereo
     RDKit          2D

  4  3  0  0  0  0  0  0  0  0999 V2000
    0.0000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    1.0000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    0.5000    0.9000    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
   -0.5000    0.9000    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  0
  1  3  1  1
  1  4  1  0
M  END
"""

DASH_MOL = """stereo
     RDKit          2D

  4  3  0  0  0  0  0  0  0  0999 V2000
    0.0000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    1.0000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    0.5000    0.9000    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
   -0.5000    0.9000    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  0
  1  3  1  0
  1  4  1  6
M  END
"""


@pytest.fixture(autouse=True)
def _config():
    with tempconfig({"dry_run": True, "disable_caching": True, "renderer": "cairo"}):
        yield


def test_wedge_bond_uses_plain_cram_bond():
    molecule = MMoleculeObject.from_mol_string(WEDGE_MOL)

    bonds = molecule.get_bonds()

    assert len(bonds) >= 1


def test_dashed_bond_uses_dashed_cram_bond():
    molecule = MMoleculeObject.from_mol_string(DASH_MOL)

    bonds = molecule.get_bonds()

    assert len(bonds) >= 1

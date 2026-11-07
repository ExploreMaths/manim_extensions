# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the chemistry file parsers and element lookup."""

import pytest

from manim_extensions.chemistry.utils.utils import (
    get_element,
    mol_parser_string,
    sdf_parser_string,
)

MOL_BLOCK = """acetone
     RDKit          2D

  3  2  0  0  0  0  0  0  0  0999 V2000
    0.0000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    1.2990    0.7500    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   -1.2990    0.7500    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  2  0
  1  3  1  0
M  END
"""


def test_mol_parser_string_reads_atoms_and_bonds():
    atoms, bonds = mol_parser_string(MOL_BLOCK.splitlines())

    assert len(atoms) == 3
    assert len(bonds) >= 1
    assert isinstance(atoms, dict)


def test_sdf_parser_string_returns_records():
    records = sdf_parser_string(MOL_BLOCK + "$$$$\n")

    assert isinstance(records, list)
    assert records


@pytest.mark.parametrize("symbol", ["O", "C", "H"])
def test_get_element_returns_element(symbol):
    element = get_element(symbol)

    assert element is not None

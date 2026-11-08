# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the chemistry CLI download command."""

import pytest

from manim_extensions.chemistry import cli as chemistry_cli

PUBMEDCALLBACK = chemistry_cli.pubchem_molecule.callback


class StubManager:
    """Minimal stand-in for the PubChem API manager."""

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def get_molecule(self):
        return "stub-molecule-data"


@pytest.fixture()
def stub_api(monkeypatch):
    monkeypatch.setattr(chemistry_cli, "PubchemAPIManager", StubManager)


def test_cid_branch_writes_a_file(stub_api, tmp_path):
    PUBMEDCALLBACK(
        "sdf", ("123",), None, (), (), False, str(tmp_path)
    )

    assert (tmp_path / "123.sdf").read_text() == "stub-molecule-data"


def test_name_branch(stub_api, tmp_path):
    PUBMEDCALLBACK("json", (), ("acetone",), (), (), False, str(tmp_path))

    assert (tmp_path / "acetone.json").exists()


def test_smiles_branch(stub_api, tmp_path):
    PUBMEDCALLBACK("xml", (), None, ("CCO",), (), False, str(tmp_path))

    assert (tmp_path / "CCO.xml").exists()


def test_inchi_branch_sanitises_the_file_name(stub_api, tmp_path):
    PUBMEDCALLBACK(
        "asnt", (), None, (), ("InChI=1S/C3H6O",), False, str(tmp_path)
    )

    files = list(tmp_path.iterdir())
    assert len(files) == 1
    assert files[0].name.endswith(".asnt")


def test_missing_identifier_raises(stub_api, tmp_path):
    with pytest.raises(Exception, match="No identifier provided"):
        PUBMEDCALLBACK("sdf", (), None, (), (), False, str(tmp_path))

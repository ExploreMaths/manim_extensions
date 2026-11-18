# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for chemistry file handlers, parser accessors and PubChem fallbacks."""

import importlib
import json

import pytest

from manim_extensions.chemistry.utils.file_handler import FileHandler, IncorrectFormat
from manim_extensions.chemistry.utils.parsers.json_parser import JSONParser
from manim_extensions.chemistry.utils.parsers.xml_parser import XMLParser


def test_file_handler_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError, match="does not exist"):
        FileHandler(tmp_path / "missing.mol")


def test_file_handler_unsupported_extension(tmp_path):
    path = tmp_path / "molecule.xyz"
    path.write_text("not a molecule")

    with pytest.raises(IncorrectFormat, match="is not supported"):
        FileHandler(path)


def test_file_handler_parse_from_string_rejects_format():
    with pytest.raises(IncorrectFormat, match="is not supported"):
        FileHandler.parse_from_string("data", "xyz")


def test_file_handler_parse_from_string_data_parser_fallback():
    with pytest.raises(Exception):
        FileHandler.parse_from_string("not asnt data", "asnt")


def test_json_parser_read_file_and_invalid_bonds(tmp_path):
    path = tmp_path / "molecule.json"
    payload = {"mol": [{"atoms": {}, "bonds": []}]}
    path.write_text(json.dumps(payload))

    assert JSONParser.read_file(str(path)) == json.dumps(payload)

    with pytest.raises(Exception, match="Bonds data is not defined correctly"):
        JSONParser.extract_bonds_data(payload["mol"][0])


def test_xml_parser_read_file(tmp_path):
    path = tmp_path / "molecule.xml"
    path.write_text("<PC-Compounds></PC-Compounds>")

    assert XMLParser.read_file(str(path)) == "<PC-Compounds></PC-Compounds>"


def test_base_parser_atoms_and_bonds_accessors():
    from manim_extensions.chemistry.utils.utils import mol_parser_string

    from manim_extensions.chemistry.utils.parsers.mol_parser import MolParser

    from tests.test_chemistry_parsers import MOL_BLOCK

    parser = MolParser.parse_from_string(MOL_BLOCK)
    atoms, bonds = parser

    class Dummy:
        atoms_data = atoms
        bonds_data = bonds

    from manim_extensions.chemistry.utils.parsers.base_parser import BaseParser

    dummy = Dummy()
    assert BaseParser.atoms.fget(dummy) == atoms
    assert BaseParser.bonds.fget(dummy) == bonds


class _FakeResponse:
    def __init__(self, payload, status_code=200, decode=False):
        self._payload = payload
        self.status_code = status_code
        self.content = b"raw-payload"
        self._decode = decode

    def json(self):
        if self._decode:
            import requests

            raise requests.exceptions.JSONDecodeError("bad", "doc", 0)
        return self._payload


def test_pubchem_json_decode_falls_back_to_content(monkeypatch):
    import requests
    from manim_extensions.chemistry.utils.pubchem_api import PubchemAPIManager

    response = _FakeResponse({}, decode=True)
    manager = PubchemAPIManager(cid=2244)
    monkeypatch.setattr(importlib.import_module("manim_extensions.chemistry.utils.pubchem_api").time, "sleep", lambda _: None)

    body = manager.handle_request(response, 2244)

    assert body == "raw-payload"


def test_pubchem_three_d_urls_for_every_identifier(monkeypatch):
    import requests
    from manim_extensions.chemistry.utils.pubchem_api import PubchemAPIManager

    calls = []

    def fake_get(url, *args, **kwargs):
        calls.append(url)
        return _FakeResponse({"ok": True})

    monkeypatch.setattr(requests, "get", fake_get)
    monkeypatch.setattr(importlib.import_module("manim_extensions.chemistry.utils.pubchem_api").time, "sleep", lambda _: None)

    PubchemAPIManager(cid=1, three_d=True).from_cid()
    PubchemAPIManager(name="water", three_d=True).from_name()
    PubchemAPIManager(smiles="O", three_d=True).from_smiles()

    assert "cid/1/json?record_type=3d" in calls[0]
    assert "name/water/json?record_type=3d" in calls[1]
    assert "smiles/O/json?record_type=3d" in calls[2]


def test_pubchem_404_and_500_errors(monkeypatch):
    import requests
    from manim_extensions.chemistry.utils.pubchem_api import PubchemAPIManager

    def fake_get(url, *args, **kwargs):
        if "missing" in url:
            return _FakeResponse({}, status_code=404)
        return _FakeResponse({}, status_code=500)

    monkeypatch.setattr(requests, "get", fake_get)
    monkeypatch.setattr(importlib.import_module("manim_extensions.chemistry.utils.pubchem_api").time, "sleep", lambda _: None)

    with pytest.raises(Exception, match="Compound missing not found"):
        PubchemAPIManager(cid="missing").from_cid()
    with pytest.raises(Exception, match="Status code: 500"):
        PubchemAPIManager(cid="broken").from_cid()


def test_mcbond_constructor_and_assignments():
    from types import SimpleNamespace
    from manim_extensions.chemistry.manim_chemistry_molecule.mc_bond import MCBond

    atom = SampleAtom()
    bond = MCBond(1, from_atom=atom, to_atom=atom, stereo=2)
    bond.assign_from_atom(atom)
    bond.assign_to_atom(atom)
    bond.assign_stereo(None)

    assert bond.from_atom is atom
    assert bond.to_atom is atom
    assert bond.stereo is None


def test_mcbond_construct_validation():
    from types import SimpleNamespace
    from manim_extensions.chemistry.manim_chemistry_molecule.mc_bond import MCBond

    molecule = SimpleNamespace(atoms_by_index={0: SampleAtom(), 1: SampleAtom()})

    with pytest.raises(Exception, match="Expected"):
        MCBond.construct_from_bond_dict(0, "bad", molecule)

    with pytest.raises(Exception, match="does not contain bond type"):
        MCBond.construct_from_bond_dict(0, {}, molecule)

    with pytest.raises(Exception, match="does not contain the expected data"):
        MCBond.construct_from_bond_dict(0, {"bond_type": 1}, molecule)

    bond = MCBond.construct_from_bond_dict(
        0,
        {"bond_type": 2, "from_atom_index": 0, "to_atom_index": 1, "stereo": 1},
        molecule,
    )
    assert bond.bond_type == 2
    assert bond.stereo == 1


class SampleAtom:
    """Minimal atom stand-in for bond construction."""

    pass

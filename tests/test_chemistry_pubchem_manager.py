# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the PubChem API manager using a stub HTTP layer."""

import json

import pytest

from manim_extensions.chemistry.utils.pubchem_api import PubchemAPIManager


class FakeResponse:
    def __init__(self, payload, status_code=200, decode_text=False):
        self._payload = payload
        self.status_code = status_code
        self.content = json.dumps(payload).encode()
        self._decode_text = decode_text

    def json(self):
        if self._decode_text:
            raise ValueError("not json")
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"status {self.status_code}")


@pytest.fixture()
def stub_requests(monkeypatch):
    import requests

    calls = []

    def fake_get(url, *args, **kwargs):
        calls.append(url)
        if "missing" in url:
            return FakeResponse({}, status_code=404)
        if "broken" in url:
            return FakeResponse({}, status_code=500)
        return FakeResponse({"PropertyTable": {"Properties": [{"CID": 1}]}})

    def fake_post(url, *args, **kwargs):
        calls.append(url)
        return FakeResponse({"IdentifierList": {"CID": [2244]}})

    monkeypatch.setattr(requests, "get", fake_get)
    monkeypatch.setattr(requests, "post", fake_post)
    return calls


def test_requires_an_identifier():
    with pytest.raises(Exception):
        PubchemAPIManager()


@pytest.mark.usefixtures("stub_requests")
def test_lookup_by_each_identifier():
    assert PubchemAPIManager(cid=2244).get_molecule()
    assert PubchemAPIManager(cid=2244, three_d=True).get_molecule()
    assert PubchemAPIManager(name="acetone").get_molecule()
    assert PubchemAPIManager(smiles="CC=O").get_molecule()
    assert PubchemAPIManager(inchi="inchikey/literal").get_molecule()


@pytest.mark.usefixtures("stub_requests")
def test_lookup_by_inchi_uses_post_to_resolve_cid():
    manager = PubchemAPIManager(inchi="InChI=1S/C3H6O/c1-3(2)4/h3H,1-2H3")

    assert manager.get_molecule()
    assert manager.three_d is False


@pytest.mark.usefixtures("stub_requests")
def test_handle_request_error_paths():
    manager = PubchemAPIManager(cid="missing")

    with pytest.raises(Exception, match="not found"):
        manager.from_cid()

    manager = PubchemAPIManager(cid="broken")
    with pytest.raises(Exception, match="Status code: 500"):
        manager.from_cid()

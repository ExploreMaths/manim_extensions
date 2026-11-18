# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Path tests for the abstract molecule construction helpers."""

import pytest

from manim_extensions.chemistry.manim_chemistry_molecule.mc_molecule import MCMolecule
from manim_extensions.chemistry.twoD.graph_molecule import GraphMolecule


@pytest.fixture()
def empty_builder(monkeypatch):
    def build(*args, **kwargs):
        return ({}, {})

    monkeypatch.setattr(
        GraphMolecule, "mc_molecule_to_atoms_and_bonds", classmethod(build)
    )


def test_molecule_from_file_accepts_single_item_list(monkeypatch, empty_builder):
    monkeypatch.setattr(MCMolecule, "construct_from_file", lambda **kwargs: [object()])

    molecule = GraphMolecule.molecule_from_file("fake.mol")

    assert isinstance(molecule, GraphMolecule)


def test_molecule_from_string_accepts_single_item_list(monkeypatch, empty_builder):
    monkeypatch.setattr(
        MCMolecule, "construct_from_string", lambda **kwargs: [object()]
    )

    molecule = GraphMolecule.molecule_from_string("fake")

    assert isinstance(molecule, GraphMolecule)


def test_multiple_molecules_from_file_rejects_non_list(monkeypatch):
    monkeypatch.setattr(
        MCMolecule, "construct_multiples_from_file", lambda **kwargs: object()
    )

    with pytest.raises(Exception, match="Expected a list"):
        GraphMolecule.multiple_molecules_from_file("fake.mol")


def test_multiple_molecules_from_string_rejects_non_list(monkeypatch):
    monkeypatch.setattr(
        MCMolecule, "construct_multiples_from_string", lambda **kwargs: object()
    )

    with pytest.raises(Exception, match="Expected a list"):
        GraphMolecule.multiple_molecules_from_string("fake")


def test_multiple_molecules_from_file_builds_group(monkeypatch, empty_builder):
    monkeypatch.setattr(
        MCMolecule, "construct_multiples_from_file", lambda **kwargs: [object()]
    )

    group = GraphMolecule.multiple_molecules_from_file("fake.mol")

    assert len(group) == 1


def test_molecule_from_pubchem_delegates_to_api(monkeypatch, empty_builder):
    import importlib

    abstract = importlib.import_module(
        "manim_extensions.chemistry.molecule.abstract_molecule"
    )

    class FakeManager:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def get_molecule(self):
            return "{}"

    monkeypatch.setattr(abstract, "PubchemAPIManager", FakeManager)
    monkeypatch.setattr(
        GraphMolecule,
        "molecule_from_string",
        classmethod(lambda cls, **kw: cls({}, {})),
    )

    molecule = GraphMolecule.molecule_from_pubchem(cid="123")

    assert isinstance(molecule, GraphMolecule)

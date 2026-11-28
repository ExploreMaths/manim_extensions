# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Manim chemistry molecule representation.

This module provides the :class:`~manim_extensions.chemistry.manim_chemistry_molecule.mc_molecule.MCMolecule` class for representing molecules.
"""

from typing import Literal, cast

from ..utils.parsers.base_parser import BondsDict
from .mc_atom import MCAtom
from .mc_bond import MCBond
from .mc_element import MCElement
from ..utils import FileHandler


class MCMolecule:
    r"""Abstraction of a molecule.

    Parameters
    ----------
    atoms
        List of :class:`~manim_extensions.chemistry.manim_chemistry_molecule.mc_atom.MCAtom` objects of the molecule.
    bonds
        List of :class:`~manim_extensions.chemistry.manim_chemistry_molecule.mc_bond.MCBond` objects of the molecule.
    name
        Name of the molecule.
    elements
        :class:`~manim_extensions.chemistry.element.element.Element`\ s data of the molecule.

    Examples
    --------
    .. manim:: MCMoleculeOverview
       :save_last_frame:

       from manim import *
       from manim_extensions.chemistry.manim_chemistry_molecule.mc_molecule import MCMolecule

       MCMoleculeTarget = MCMolecule

       class MCMoleculeOverview(Scene):
           def construct(self):
               public = [n for n in dir(MCMoleculeTarget) if not n.startswith("_")]
               card = VGroup(
                   Text('MCMolecule', font_size=36),
                   Text('module: manim_extensions.chemistry.manim_chemistry_molecule.mc_molecule', font_size=18, color=GREY),
                   Text('Abstraction of a molecule', font_size=22),
                   Text("API: " + ", ".join(public[:6]), font_size=18, color=BLUE),
               ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
               card.scale_to_fit_width(11.5).move_to(ORIGIN)
               frame = RoundedRectangle(
                   width=12.1, height=card.height + 0.5, corner_radius=0.2, color=BLUE_D
               ).move_to(card)
               self.add(frame, card)

    .. code-block:: python

        import numpy as np
        from manim_extensions.chemistry.manim_chemistry_molecule.mc_atom import MCAtom
        from manim_extensions.chemistry.manim_chemistry_molecule.mc_bond import MCBond
        from manim_extensions.chemistry.manim_chemistry_molecule.mc_molecule import MCMolecule
        from manim_extensions.chemistry.manim_chemistry_molecule.mc_element import MC_ELEMENT_DICT

        atom_a = MCAtom(MC_ELEMENT_DICT["C"], coords=np.array([0.0, 0.0, 0.0]))
        atom_b = MCAtom(MC_ELEMENT_DICT["O"], coords=np.array([1.0, 0.0, 0.0]))
        bond = MCBond(bond_type=1, from_atom=atom_a, to_atom=atom_b)
        molecule = MCMolecule(atoms=[atom_a, atom_b], bonds=[bond], name="ethene")
    """

    def __init__(
        self,
        atoms: list[MCAtom] | None = None,
        bonds: list[MCBond] | None = None,
        name: str | None = None,
        elements: MCElement | dict[str, MCElement] | None = None,
    ) -> None:
        self.atoms = atoms or []
        self.bonds = bonds or []
        self.elements: MCElement | dict[str, MCElement] = elements or {}
        self.atoms_by_index: dict[int, MCAtom] = {}
        self.name = name

    def add_atoms_from_atoms_dict(
        self,
        atoms_dict: dict[int, dict[str, object]],
        elements_data_dict: dict[str, MCElement] | None,
    ) -> None:
        """Uses the atoms dict returned by a parser to add the atoms to the molecule.

        Parameters
        ----------
        atoms_dict
            Atoms dict from a parser. See :class:`~manim_extensions.chemistry.utils.parsers.base_parser.BaseParser`.
        elements_data_dict
            Dictionary of custom element data to merge over the
            default elements data.

        Raises
        ------
        Exception
            Raised when ``atoms_dict`` is not a dict of atom data dicts.
        """

        if self.atoms and not isinstance(self.atoms, list):
            raise Exception(f"Atoms list {self.atoms} is not an atoms list.")

        else:
            self.atoms = []

        for atom_index, atom_data_dict in atoms_dict.items():
            mc_atom = MCAtom.construct_from_atom_dict(
                atom_index=atom_index,
                atom_data_dict=atom_data_dict,
                elements_data_dict=elements_data_dict,
            )
            mc_atom.assign_molecule(self)
            self.atoms.append(mc_atom)
            self.atoms_by_index[atom_index] = mc_atom

    def add_bonds_from_bonds_dict(self, bonds_dict: BondsDict) -> None:
        """Uses the bonds dict returned by a parser to add the bonds to the molecule.

        Parameters
        ----------
        bonds_dict
            Bonds dict from a parser. See Base Parser.

        Raises
        ------
        Exception
            Raised when ``bonds_dict`` is not a dict of bond data dicts.
        """

        if self.bonds and not isinstance(self.bonds, list):
            raise Exception("Bonds list is not a bonds list.")

        else:
            self.bonds = []

        for bond_index, bond_data_dict in bonds_dict.items():
            self.bonds.append(
                MCBond.construct_from_bond_dict(
                    bond_index=bond_index,
                    bond_data_dict=bond_data_dict,
                    molecule=self,
                )
            )

    def add_connections_between_atoms(self) -> None:
        r"""Uses the :class:`~manim_extensions.chemistry.manim_chemistry_molecule.mc_bond.MCBond`\ s to add connections between :class:`~manim_extensions.chemistry.manim_chemistry_molecule.mc_atom.MCAtom`\ s.

        Raises
        ------
        Exception
            Raised when the bonds list is not a list of :class:`~manim_extensions.chemistry.manim_chemistry_molecule.mc_bond.MCBond`\ s.
        """

        if self.bonds and not isinstance(self.bonds, list):
            raise Exception("Bonds list is not a bonds list.")

        for mc_bond in self.bonds:
            from_atom = mc_bond.from_atom
            to_atom = mc_bond.to_atom
            assert from_atom is not None
            assert to_atom is not None
            from_atom.add_atoms(to_atom)
            from_atom.add_bonds(mc_bond)
            to_atom.add_atoms(from_atom)
            to_atom.add_bonds(mc_bond)

    @staticmethod
    def construct_from_data_dict(
        atoms_data_dict: dict[int, dict[str, object]],
        bonds_data_dict: BondsDict,
        ignore_hydrogens: bool = True,
        ignore_all_hydrogens: bool = False,
        elements_data_dict: dict[str, MCElement] | None = None,
    ) -> "MCMolecule":
        r"""Given data with the format provided by a parser, constructs a :class:`~manim_extensions.chemistry.manim_chemistry_molecule.mc_molecule.MCMolecule`,
        the corresponding :class:`~manim_extensions.chemistry.manim_chemistry_molecule.mc_atom.MCAtom`\ s and :class:`~manim_extensions.chemistry.manim_chemistry_molecule.mc_bond.MCBond`\ s and stablishes the connections between
        :class:`~manim_extensions.chemistry.manim_chemistry_molecule.mc_atom.MCAtom`\ s and bonds.

        Parameters
        ----------
        atoms_data_dict
            Atoms data.
        bonds_data_dict
            Bonds data.
        ignore_hydrogens
            Whether to remove hydrogens bonded to carbon atoms.

        ignore_all_hydrogens
            Whether to remove every hydrogen atom.
        elements_data_dict
            Dictionary of custom element data to merge over the
            default elements data.

        Returns
        -------
            A :class:`~manim_extensions.chemistry.manim_chemistry_molecule.mc_molecule.MCMolecule` instance representing the result.
        """

        mc_molecule = MCMolecule()
        mc_molecule.add_atoms_from_atoms_dict(
            atoms_dict=atoms_data_dict, elements_data_dict=elements_data_dict
        )
        mc_molecule.add_bonds_from_bonds_dict(bonds_dict=bonds_data_dict)
        mc_molecule.add_connections_between_atoms()

        if ignore_all_hydrogens:
            mc_molecule.remove_all_hydrogens()

        elif ignore_hydrogens:
            mc_molecule.remove_carbon_hydrogens()

        return mc_molecule

    @staticmethod
    def construct_from_file(
        filepath: str,
        ignore_hydrogens: bool = True,
        ignore_all_hydrogens: bool = False,
        elements_data_dict: dict[str, MCElement] | None = None,
    ) -> "MCMolecule":
        """Returns an :class:`~manim_extensions.chemistry.manim_chemistry_molecule.mc_molecule.MCMolecule` given a file path.

        Parameters
        ----------
        filepath
            File path.
        ignore_hydrogens
            Whether to remove hydrogens bonded to carbon atoms.

        ignore_all_hydrogens
            Whether to remove every hydrogen atom.
        elements_data_dict
            Dictionary of custom element data to merge over the
            default elements data.

        Returns
        -------
            The molecule constructed from the file.
        """
        parsed_data = FileHandler(file_path=filepath).parsed_atoms_bonds_data()

        if isinstance(parsed_data, list):
            parsed_data = parsed_data[0]

        atoms_dict, bonds_dict = parsed_data
        return MCMolecule.construct_from_data_dict(
            atoms_dict,
            bonds_dict,
            ignore_hydrogens=ignore_hydrogens,
            ignore_all_hydrogens=ignore_all_hydrogens,
            elements_data_dict=elements_data_dict,
        )

    @staticmethod
    def construct_multiples_from_file(
        filepath: str,
        ignore_hydrogens: bool = True,
        ignore_all_hydrogens: bool = False,
        elements_data_dict: dict[str, MCElement] | None = None,
    ) -> list["MCMolecule"]:
        r"""Similar to ``construct_from_file`` but returning a list of :class:`~manim_extensions.chemistry.manim_chemistry_molecule.mc_molecule.MCMolecule`\ s.

        Parameters
        ----------
        filepath
            Path to the molecule file.
        ignore_hydrogens
            Whether to remove hydrogens bonded to carbon atoms.

        ignore_all_hydrogens
            Whether to remove every hydrogen atom.
        elements_data_dict
            Dictionary of custom element data to merge over the
            default elements data.

        Returns
        -------
            A list of the results.
        """

        list_of_data_dicts = cast(
            list[tuple[dict[int, dict[str, object]], BondsDict]],
            FileHandler(file_path=filepath).parsed_atoms_bonds_data(),
        )
        mc_molecules = []
        for atoms_dict, bonds_dict in list_of_data_dicts:
            mc_molecules.append(
                MCMolecule.construct_from_data_dict(
                    atoms_data_dict=atoms_dict,
                    bonds_data_dict=bonds_dict,
                    ignore_hydrogens=ignore_hydrogens,
                    ignore_all_hydrogens=ignore_all_hydrogens,
                    elements_data_dict=elements_data_dict,
                )
            )

        return mc_molecules

    @staticmethod
    def construct_from_string(
        string: str,
        format: Literal["mol", "sdf", "asnt", "json", "xml"] = "json",
        ignore_hydrogens: bool = True,
        ignore_all_hydrogens: bool = False,
        elements_data_dict: dict[str, MCElement] | None = None,
    ) -> "MCMolecule":
        """Reads a string and returns a molecule.

        Supported formats are:

        .. list-table::
           :header-rows: 0

           * - ``mol``
             - MDL molfile.
           * - ``sdf``
             - Structure-Data File.
           * - ``asnt``
             - ASN.1 format.
           * - ``json``
             - JSON format.
           * - ``xml``
             - XML format.

        Parameters
        ----------
        string
            String with the molecule data.
        format
            Format of the data.
        ignore_hydrogens
            Whether to remove hydrogens bonded to carbon atoms.

        ignore_all_hydrogens
            Whether to remove every hydrogen atom.
        elements_data_dict
            Dictionary of custom element data to merge over the
            default elements data.

        Returns
        -------
            The molecule parsed from the string.
        """
        parsed_data = FileHandler.parse_from_string(string=string, format=format)

        if isinstance(parsed_data, list):
            parsed_data = parsed_data[0]

        atoms_dict, bonds_dict = parsed_data
        return MCMolecule.construct_from_data_dict(
            atoms_dict,
            bonds_dict,
            ignore_hydrogens=ignore_hydrogens,
            ignore_all_hydrogens=ignore_all_hydrogens,
            elements_data_dict=elements_data_dict,
        )

    @staticmethod
    def construct_multiples_from_string(
        string: str,
        format: Literal["mol", "sdf", "asnt", "json", "xml"] = "json",
        ignore_hydrogens: bool = True,
        ignore_all_hydrogens: bool = False,
        elements_data_dict: dict[str, MCElement] | None = None,
    ) -> list["MCMolecule"]:
        r"""Similar to ``construct_from_string`` but returning a list of :class:`~manim_extensions.chemistry.manim_chemistry_molecule.mc_molecule.MCMolecule`\ s.

        Parameters
        ----------
        string
            String with the molecule data.
        format
            Format of the data.
        ignore_hydrogens
            Whether to remove hydrogens bonded to carbon atoms.

        ignore_all_hydrogens
            Whether to remove every hydrogen atom.
        elements_data_dict
            Dictionary of custom element data to merge over the
            default elements data.

        Returns
        -------
            A list of the results.
        """
        parsed_data = FileHandler.parse_from_string(string=string, format=format)
        if isinstance(parsed_data, tuple):
            parsed_data = [parsed_data]
        mc_molecules = []
        for atoms_dict, bonds_dict in parsed_data:
            mc_molecules.append(
                MCMolecule.construct_from_data_dict(
                    atoms_data_dict=atoms_dict,
                    bonds_data_dict=bonds_dict,
                    ignore_hydrogens=ignore_hydrogens,
                    ignore_all_hydrogens=ignore_all_hydrogens,
                    elements_data_dict=elements_data_dict,
                )
            )

        return mc_molecules

    def remove_carbon_hydrogens(self) -> None:
        """Remove all hydrogen atoms that are bonded only to carbon atoms."""
        atoms_to_be_removed = []
        for index, atom in self.atoms_by_index.items():
            if atom.element.atomic_number != 1 or atom.element.symbol != "H":
                continue

            bond = atom.bonds[0]
            to_atom = cast(MCAtom, bond.to_atom)
            from_atom = cast(MCAtom, bond.from_atom)
            if (
                to_atom.element.atomic_number == 6
                or from_atom.element.atomic_number == 6
                or to_atom.element.symbol == "C"
                or from_atom.element.symbol == "C"
            ):
                atoms_to_be_removed.append(index)

        self.remove_hydrogens(atoms_to_be_removed)
        return None

    def remove_all_hydrogens(self) -> None:
        """Remove every hydrogen atom from the molecule."""
        atoms_to_be_removed = []
        for index, atom in self.atoms_by_index.items():
            if atom.element.atomic_number != 1:
                continue

            atoms_to_be_removed.append(index)

        self.remove_hydrogens(atoms_to_be_removed)
        return None

    def remove_hydrogens(self, atoms_to_be_removed: list[int]) -> None:
        """Remove specified atoms and their associated bonds, then reindex.

        Parameters
        ----------
        atoms_to_be_removed
            Indices of the atoms to remove.
        """
        if not atoms_to_be_removed:
            return
        for atom in atoms_to_be_removed:
            self.atoms_by_index.pop(atom)

        self.atoms = list(self.atoms_by_index.values())

        bonds_to_be_removed = []
        for index, bond in enumerate(self.bonds):
            from_atom = bond.from_atom
            to_atom = bond.to_atom
            assert from_atom is not None
            assert to_atom is not None
            if from_atom.molecule_index in atoms_to_be_removed:
                bonds_to_be_removed.append(index)

            if to_atom.molecule_index in atoms_to_be_removed:
                bonds_to_be_removed.append(index)

        if not bonds_to_be_removed:
            return

        bonds_to_be_removed.reverse()

        for bond_index in bonds_to_be_removed:
            self.bonds.pop(bond_index)

        self.reindex_molecule_atoms()

    def reindex_molecule_atoms(self) -> None:
        """Reassign consecutive indices to all atoms and update bond references."""
        self.atoms_by_index = {}
        atoms_old_index_mapping = {}
        for index, atom in enumerate(self.atoms, start=1):
            atoms_old_index_mapping[atom.molecule_index] = index
            atom.molecule_index = index
            self.atoms_by_index[index] = atom

        for bond in self.bonds:
            from_atom = bond.from_atom
            to_atom = bond.to_atom
            assert from_atom is not None
            assert to_atom is not None
            if from_atom.molecule_index in atoms_old_index_mapping:
                from_atom.molecule_index = atoms_old_index_mapping[
                    from_atom.molecule_index
                ]

            if to_atom.molecule_index in atoms_old_index_mapping:
                to_atom.molecule_index = atoms_old_index_mapping[to_atom.molecule_index]

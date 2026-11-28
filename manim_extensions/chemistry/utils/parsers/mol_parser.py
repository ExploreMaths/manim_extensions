# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""MOL format parser for chemical files.

This module provides the :class:`~manim_extensions.chemistry.utils.parsers.mol_parser.MolParser` class for parsing MOL format chemical files.
"""

from typing import cast

import numpy as np

from .base_parser import (
    AtomsDict,
    BaseParser,
    BondsDict,
    FilePath,
    ParsedData,
)


class MolParser(BaseParser):
    """Parses mol files.

    Examples
    --------
    .. manim:: MolParserOverview
       :save_last_frame:

       from manim import *
       from manim_extensions.chemistry.utils.parsers.mol_parser import MolParser

       MolParserTarget = MolParser

       class MolParserOverview(Scene):
           def construct(self):
               public = [n for n in dir(MolParserTarget) if not n.startswith("_")]
               card = VGroup(
                   Text('MolParser', font_size=36),
                   Text('module: manim_extensions.chemistry.utils.parsers.mol_parser', font_size=18, color=GREY),
                   Text('Parses mol files', font_size=22),
                   Text("API: " + ", ".join(public[:6]), font_size=18, color=BLUE),
               ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
               card.scale_to_fit_width(11.5).move_to(ORIGIN)
               frame = RoundedRectangle(
                   width=12.1, height=card.height + 0.5, corner_radius=0.2, color=BLUE_D
               ).move_to(card)
               self.add(frame, card)

    .. nbcell::
       :files: acetone_2d.mol

       from pprint import pprint

       parsed_mol = MolParser(
           filename="acetone_2d.mol"
       )
       pprint(parsed_mol.atoms_data)

    .. nbcell::

       pprint(parsed_mol.bonds_data)
    """

    @staticmethod
    def read_file(
        filename: FilePath,
    ) -> str | list[str] | list[list[str]]:
        """Read a MOL file and return its lines.

        Parameters
        ----------
        filename
            Path to the MOL file to parse.

        Returns
        -------
            Lines of the MOL file.
        """
        with open(filename) as file:
            mol_file = file.readlines()

        return mol_file

    @staticmethod
    def parse_from_string(string: str) -> tuple[AtomsDict, BondsDict]:
        """Parse MOL data passed directly as a string.

        Parameters
        ----------
        string
            Raw MOL data (the contents of a ``.mol`` file).

        Returns
        -------
            ``(atoms_data, bonds_data)`` tuple of dictionaries.
        """
        return cast(
            tuple[AtomsDict, BondsDict], MolParser.data_parser(string.splitlines())
        )

    @staticmethod
    def data_parser(data: list[str] | list[list[str]]) -> ParsedData:
        # Get general data
        """Parse the lines of a MOL file into atoms and bonds dicts.

        Parameters
        ----------
        data
            Lines of the MOL file as returned by :meth:`~manim_extensions.chemistry.utils.parsers.mol_parser.MolParser.read_file`.

        Returns
        -------
            ``(atoms_data, bonds_data)`` tuple of dictionaries.
        """
        lines = cast(list[str], data)
        mol_name = lines[0].strip()  # This info is not always available  # noqa F841
        mol_source = lines[1].strip()  # This info is not always available  # noqa F841
        mol_comments = lines[
            2
        ].rstrip()  # This info is not always available # noqa F841
        mol_general_line = lines[3]  # This info is not always available
        lines.remove(mol_general_line)  # This info is not always available
        mol_general_info = mol_general_line.rstrip().split()
        number_of_atoms = int(mol_general_info[0])
        number_of_bonds = int(mol_general_info[1])

        atoms: dict[int, dict[str, object]] = {}
        bonds: dict[int, list[dict[str, object]]] = {}
        for index, line in enumerate(lines[3 : 3 + number_of_atoms]):
            line_data = line.split()
            x_position = float(line_data[0])
            y_position = float(line_data[1])
            z_position = float(line_data[2])
            element = line_data[3]
            atoms[index + 1] = {
                "coords": np.array([x_position, y_position, z_position]),
                "element": element,
            }
        bond_index = 1
        for line in lines[3 + number_of_atoms : 3 + number_of_atoms + number_of_bonds]:
            line_data = line.split()
            first_atom_index = int(float(line_data[0]))
            second_atom_index = int(float(line_data[1]))
            bond_type = line_data[2]
            bond_data: dict[str, object] = {
                "to_atom_index": first_atom_index,
                "from_atom_index": second_atom_index,
                "bond_type": bond_type,
                "bond_index": bond_index,
                "stereo": None,
                "topology": None,
                "reacting_center_status": None,
            }
            bond_index += 1

            try:
                bond_stereo = line_data[3]
            except Exception as _:
                bond_stereo = ""
            else:
                bond_data["stereo"] = int(bond_stereo)

            try:
                bond_topology = line_data[5]
            except Exception as _:
                bond_topology = ""
            else:
                bond_data["topology"] = int(bond_topology)

            try:
                reacting_center_status = line_data[6]
            except Exception as _:
                reacting_center_status = ""
            else:
                bond_data["reacting_center_status"] = int(reacting_center_status)

            if first_atom_index not in bonds:
                bonds[first_atom_index] = [bond_data]
                target_bonds = atoms[first_atom_index].get("bond_to")
                if not isinstance(target_bonds, dict):
                    target_bonds = {}
                    atoms[first_atom_index]["bond_to"] = target_bonds
                target_bonds[second_atom_index] = atoms[second_atom_index].get(
                    "element"
                )

            else:
                bonds[first_atom_index].append(bond_data)
                target_bonds = atoms[first_atom_index].get("bond_to")
                if not isinstance(target_bonds, dict):
                    target_bonds = {}
                    atoms[first_atom_index]["bond_to"] = target_bonds
                target_bonds[second_atom_index] = atoms[second_atom_index].get(
                    "element"
                )

            target_bonds = atoms[second_atom_index].get("bond_to")
            if not isinstance(target_bonds, dict):
                target_bonds = {}
                atoms[second_atom_index]["bond_to"] = target_bonds
            target_bonds[first_atom_index] = atoms[first_atom_index].get("element")

        new_bonds: BondsDict = {}

        for bonds_data in bonds.values():
            for bond in bonds_data:
                bond_index = cast(int, bond.pop("bond_index"))
                new_bonds[bond_index] = bond

        return atoms, new_bonds

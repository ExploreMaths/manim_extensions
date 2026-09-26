# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
# patched: lazy-import xmltodict (chemistry extra)
"""XML format parser for chemical files.

This module provides the XMLParser class for parsing XML format chemical files.

"""

from typing import Any

import numpy as np

from ....utils.deps import require

from .base_parser import AtomsDict, BaseParser, BondsDict, FilePath, MoleculeData


class XMLParser(BaseParser):
    """Parses mol files.

    Examples
    --------
    .. code-block:: python

        parsed_xml = XMLParser(filename="acetone_2d.json")
        print(parsed_xml.atoms_data)
        print(parsed_xml.bonds_data)
        >>> {
            1: {"element": "O", "coords": array([3.732, 0.75, 0.0])},
            2: {"element": "C", "coords": array([2.866, 0.25, 0.0])},
            3: {"element": "C", "coords": array([2.0, 0.75, 0.0])},
            4: {"element": "C", "coords": array([2.866, -0.75, 0.0])},
            5: {"element": "H", "coords": array([2.31, 1.2869, 0.0])},
            6: {"element": "H", "coords": array([1.4631, 1.06, 0.0])},
            7: {"element": "H", "coords": array([1.69, 0.2131, 0.0])},
            8: {"element": "H", "coords": array([2.246, -0.75, 0.0])},
            9: {"element": "H", "coords": array([2.866, -1.37, 0.0])},
            10: {"element": "H", "coords": array([3.486, -0.75, 0.0])},
        }
        >>> {
            0: {"from_atom_index": 1, "to_atom_index": 2, "bond_type": 2},
            1: {"from_atom_index": 2, "to_atom_index": 3, "bond_type": 1},
            2: {"from_atom_index": 2, "to_atom_index": 4, "bond_type": 1},
            3: {"from_atom_index": 3, "to_atom_index": 5, "bond_type": 1},
            4: {"from_atom_index": 3, "to_atom_index": 6, "bond_type": 1},
            5: {"from_atom_index": 3, "to_atom_index": 7, "bond_type": 1},
            6: {"from_atom_index": 4, "to_atom_index": 8, "bond_type": 1},
            7: {"from_atom_index": 4, "to_atom_index": 9, "bond_type": 1},
            8: {"from_atom_index": 4, "to_atom_index": 10, "bond_type": 1},
        }
    """

    @staticmethod
    def read_file(filename: FilePath) -> str:
        """Read an XML file and return its content as a string.

        Parameters
        ----------
        filename : :data:`~manim_extensions.chemistry.utils.parsers.base_parser.FilePath`
            Path to the XML file to parse.

        Returns
        -------
        :class:`str`
            String with the file data.
        """
        with open(filename) as file:
            xml_file = file.read()

        return xml_file

    @staticmethod
    def data_parser(data: str) -> MoleculeData:
        """
        Parses the atoms and bonds data and returns a tuple of dictionaries with each data.
        Currently only PubChem xml files are supported.

        The atom data follows the structure:
            {<atom_index>: {"element": <atom_element>, "position": [<x_pos>, <y_pos>, <z_pos>]}}

        The bond data follows the structure:
            {<bond_index>: {"from_atom_index": <from_atom_index>, "to_atom_index": <to_atom_index>, "bond_type": <bond_type>}}

        Parameters
        ----------
        data : :class:`str`
            String with the XML file data as returned by :meth:`~manim_extensions.chemistry.utils.parsers.xml_parser.XMLParser.read_file`.

        Returns
        -------
        :data:`~manim_extensions.chemistry.utils.parsers.base_parser.MoleculeData`
            ``(atoms_data, bonds_data)`` tuple of dictionaries.
        """
        xmltodict: Any = require("chemistry", "xmltodict")
        parsed_xml: Any = xmltodict.parse(data)
        molecule_data = parsed_xml.get("PC-Compounds").get("PC-Compound")
        molecule_parsed_data = XMLParser.parse_molecule_data(
            molecule_data=molecule_data
        )

        return molecule_parsed_data

    @staticmethod
    def parse_molecule_data(molecule_data: dict[str, Any]) -> MoleculeData:
        """Parse a single molecule entry into atoms and bonds dicts.

        Parameters
        ----------
        molecule_data : :class:`dict`
            Dictionary with the data of a single molecule.

        Returns
        -------
        :data:`~manim_extensions.chemistry.utils.parsers.base_parser.MoleculeData`
            ``(atoms_data, bonds_data)`` tuple of dictionaries.
        """
        atoms_data = XMLParser.extract_atoms_data(molecule_data=molecule_data)
        bonds_data = XMLParser.extract_bonds_data(molecule_data=molecule_data)

        return atoms_data, bonds_data

    @staticmethod
    def extract_atoms_data(molecule_data: dict[str, Any]) -> AtomsDict:
        """Extract the atoms data from a single molecule entry.

        Parameters
        ----------
        molecule_data : :class:`dict`
            Dictionary with the data of a single molecule.

        Returns
        -------
        :data:`~manim_extensions.chemistry.utils.parsers.base_parser.AtomsDict`
            Atoms data of the molecule.

        Raises
        ------
        Exception
            Raised when the atoms data has no dictionary structure.
        """
        compound_atoms: Any = molecule_data.get("PC-Compound_atoms")
        atoms_data_dict = compound_atoms.get("PC-Atoms")
        if not isinstance(atoms_data_dict, dict):
            raise Exception(f"Atoms data has no dictionary structure {atoms_data_dict}")

        atoms_aid: Any = atoms_data_dict.get("PC-Atoms_aid")
        atoms_indices_raw = atoms_aid.get("PC-Atoms_aid_E")
        atoms_indices = [int(atom_index) for atom_index in atoms_indices_raw]

        atoms_element: Any = atoms_data_dict.get("PC-Atoms_element")
        atoms_elements_raw = atoms_element.get("PC-Element")
        atoms_elements: list[Any] = []
        for atom_element_dict in atoms_elements_raw:
            atoms_elements.append(atom_element_dict.get("@value"))

        compound_coords: Any = molecule_data.get("PC-Compound_coords")
        coords_data_dict = compound_coords.get("PC-Coordinates")
        conformers_section: Any = coords_data_dict.get("PC-Coordinates_conformers")
        atoms_coords_raw = conformers_section.get("PC-Conformer")

        conformer_x: Any = atoms_coords_raw.get("PC-Conformer_x")
        coords_x = [
            float(coord)
            for coord in conformer_x.get("PC-Conformer_x_E")
        ]
        conformer_y: Any = atoms_coords_raw.get("PC-Conformer_y")
        coords_y = [
            float(coord)
            for coord in conformer_y.get("PC-Conformer_y_E")
        ]
        conformer_z: Any = atoms_coords_raw.get("PC-Conformer_z")
        if conformer_z:
            coords_z = [
                float(coord)
                for coord in conformer_z.get("PC-Conformer_z_E")
            ]

        else:
            coords_z = [0 for _ in coords_x]

        atoms_coords = [
            np.array([coord_x, coord_y, coord_z])
            for coord_x, coord_y, coord_z in zip(coords_x, coords_y, coords_z)
        ]

        atoms_data = {
            atom_index: {"element": element.capitalize(), "coords": coord}
            for atom_index, element, coord in zip(
                atoms_indices, atoms_elements, atoms_coords
            )
        }

        return atoms_data

    @staticmethod
    def extract_bonds_data(molecule_data: dict[str, Any]) -> BondsDict:
        """Extract the bonds data from a single molecule entry.

        Parameters
        ----------
        molecule_data : :class:`dict`
            Dictionary with the data of a single molecule.

        Returns
        -------
        :data:`~manim_extensions.chemistry.utils.parsers.base_parser.BondsDict`
            Bonds data of the molecule.
        """
        compound_bonds: Any = molecule_data.get("PC-Compound_bonds")
        bonds_data_dict = compound_bonds.get("PC-Bonds")

        aid1_section: Any = bonds_data_dict.get("PC-Bonds_aid1")
        from_atoms_raw_data = aid1_section.get("PC-Bonds_aid1_E")
        from_atoms_data = [
            int(from_atom_index) for from_atom_index in from_atoms_raw_data
        ]

        aid2_section: Any = bonds_data_dict.get("PC-Bonds_aid2")
        to_atoms_raw_data = aid2_section.get("PC-Bonds_aid2_E")
        to_atoms_data = [int(to_atom_index) for to_atom_index in to_atoms_raw_data]

        order_section: Any = bonds_data_dict.get("PC-Bonds_order")
        bonds_type_raw_data = order_section.get("PC-BondType")
        bonds_type_data = [
            int(bond_type_data.get("#text")) for bond_type_data in bonds_type_raw_data
        ]

        bonds_data: BondsDict = {}
        for index, bond_data in enumerate(
            zip(from_atoms_data, to_atoms_data, bonds_type_data)
        ):
            from_atom_index, to_atom_index, bond_type = bond_data
            bonds_data[index] = {
                "from_atom_index": from_atom_index,
                "to_atom_index": to_atom_index,
                "bond_type": bond_type,
            }

        return bonds_data
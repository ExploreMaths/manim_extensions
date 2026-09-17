# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""File handling for chemistry module.

This module provides file parsing utilities for chemistry file formats.

"""

import os
from typing import Any, Dict, Tuple, Union

from .parsers import MolParser, SDFParser, ASNTParser, JSONParser, XMLParser

SUPPORTED_FORMATS = {
    "mol": MolParser,
    "sdf": SDFParser,
    "asnt": ASNTParser,
    "json": JSONParser,
    "xml": XMLParser,
}


class IncorrectFormat(Exception):
    """Raised when a file has an unsupported or unrecognized format."""


class FileHandler:
    """Handles the parsing of chemistry files selecting the right parser.

    Parameters
    ----------
    file_path : :class:`str`, :class:`~manim_extensions.chemistry.utils.file_handler.FileHandler.bytes` or Path-like
        Path to the chemistry file to parse.
    """

    def __init__(self, file_path: Union[str, bytes, os.PathLike]):
        """Open a chemistry file and instantiate the appropriate parser.

        Parameters
        ----------
        file_path : str, bytes, or os.PathLike
            Path to the chemistry file to parse. The format is inferred
            from the file extension.

        Raises
        ------
        FileNotFoundError
            If the file does not exist.
        IncorrectFormat
            If the file extension is not in ``SUPPORTED_FORMATS``.
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File {file_path} does not exist.")

        file_extension = FileHandler.get_file_extension(file_path)

        if file_extension not in SUPPORTED_FORMATS:
            raise IncorrectFormat(
                f"File {file_path} of format {file_extension} is not supported. Supported extensions are {SUPPORTED_FORMATS.keys()}"
            )

        self.parser = SUPPORTED_FORMATS.get(file_extension)(filename=file_path)

    @staticmethod
    def get_file_extension(file_path: Any):
        """Return the lowercase file extension without the leading dot."""
        return os.path.splitext(file_path)[1][1:]

    def parsed_atoms_bonds_data(self) -> Tuple[Dict, Dict]:
        """Return the parsed ``(atoms_dict, bonds_dict)`` from the parser."""
        return self.parser.molecule_data

    def parse_from_string(string: str, format: str):
        """Parse molecule data directly from a string using the given format.

        Parameters
        ----------
        string : str
            Raw molecule data as a string (e.g. the contents of a .mol file).
        format : str
            Format identifier matching a key in ``SUPPORTED_FORMATS``.

        Returns
        -------
        tuple or list
            Parsed ``(atoms, bonds)`` tuple (or list of tuples for multi-molecule formats).

        Raises
        ------
        IncorrectFormat
            If ``format`` is not a supported format.
        """
        if format not in SUPPORTED_FORMATS:
            raise IncorrectFormat(
                f"Format {format} is not supported. Supported extensions are {SUPPORTED_FORMATS.keys()}"
            )

        parser = SUPPORTED_FORMATS.get(format)

        return parser.data_parser(string)
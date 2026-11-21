# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
# patched: document module-level constants

"""File handling for chemistry module.

This module provides file parsing utilities for chemistry file formats.

"""

from typing import Any, Literal, cast

import os

from .parsers import MolParser, SDFParser, ASNTParser, JSONParser, XMLParser
from .parsers.base_parser import ParsedData

#: Mapping from file extension to the parser class that handles it.
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
    file_path
        Path to the chemistry file to parse.
    """

    def __init__(self, file_path: str | bytes | os.PathLike[str]) -> None:
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File {file_path!r} does not exist.")

        file_extension = FileHandler.get_file_extension(file_path)

        if file_extension not in SUPPORTED_FORMATS:
            raise IncorrectFormat(
                f"File {file_path!r} of format {file_extension} is not supported. Supported extensions are {SUPPORTED_FORMATS.keys()}"
            )

        parser_class = cast(Any, SUPPORTED_FORMATS[file_extension])
        self.parser = parser_class(filename=file_path)

    @staticmethod
    def get_file_extension(file_path: str | bytes | os.PathLike[str]) -> str:
        """Return the lowercase file extension without the leading dot.

        Parameters
        ----------
        file_path
            Path to the file.

        Returns
        -------
            The lowercase file extension without the leading dot.
        """
        return cast(str, os.path.splitext(file_path)[1][1:])

    def parsed_atoms_bonds_data(self) -> ParsedData:
        """
        Return the parsed atom and bond dictionaries.

        Returns
        -------
            ``(atoms_dict, bonds_dict)`` parsed by the selected parser.
        """
        return cast(ParsedData, self.parser.molecule_data)

    @staticmethod
    def parse_from_string(
        string: str, format: Literal["mol", "sdf", "asnt", "json", "xml"]
    ) -> ParsedData:
        """Parse molecule data directly from a string using the given format.

        Parameters
        ----------
        string
            Raw molecule data as a string (e.g. the contents of a .mol file).
        format
            Format identifier matching a key in :data:`~manim_extensions.chemistry.utils.file_handler.SUPPORTED_FORMATS`.

        Returns
        -------
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

        parser = SUPPORTED_FORMATS[format]

        parse_from_string = getattr(parser, "parse_from_string", None)
        if parse_from_string is not None:
            return cast(ParsedData, parse_from_string(string))

        return parser.data_parser(string)

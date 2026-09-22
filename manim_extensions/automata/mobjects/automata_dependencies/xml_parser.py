# SPDX-FileCopyrightText: 2022 Sean Nelson
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
# patched: lazy-import xmltodict (automata extra)

"""XML parser for automata definition files.

This module provides functions for parsing XML format automaton definition files.

"""

from ....utils.deps import require


def parse_xml_file(file_name: str) -> dict[str, object]:
    """Converts parses the xml from given file,
    then jsonify into a dictionary.

    Parameters
    ----------
    file_name
        The path to the target file.

    Returns
    -------
    dict
        The parsed XML content as a dictionary.
    """
    xmltodict = require("automata", "xmltodict")
    with open(file_name, "rb") as f:
        return xmltodict.parse(f)
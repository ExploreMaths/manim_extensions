.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

parsers
=======

.. automodule:: manim_extensions.chemistry.utils.parsers

Usage
-----

Pick the parser for the file format, or use it directly to read atom and bond data.

.. code-block:: python

   from manim_extensions.chemistry.utils.parsers import MolParser, SDFParser

   atoms, bonds = MolParser.read_file("acetone_2d.mol")
   records = SDFParser.read_file("molecules.sdf")

Modules
-------

.. autosummary::
   :nosignatures:

   ~asnt_parser
   ~base_parser
   ~json_parser
   ~mol_parser
   ~sdf_parser
   ~xml_parser

.. toctree::
   :hidden:
   :maxdepth: 1

   asnt_parser
   base_parser
   json_parser
   mol_parser
   sdf_parser
   xml_parser

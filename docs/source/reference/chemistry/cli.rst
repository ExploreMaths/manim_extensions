.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

cli
===

.. automodule:: manim_extensions.chemistry.cli

The chemistry subpackage ships a small `Click
<https://click.palletsprojects.com/>`_-based command-line client for
downloading molecule data from `PubChem <https://pubchem.ncbi.nlm.nih.gov/>`_
without writing any Python. Installing the package registers a
``manim-chemistry`` command; the examples below use it:

.. nbcell::
   :language: console
   :prompt-in: "$"

   manim-chemistry --help

The command group currently exposes one subcommand,
``pubchem-molecule``. It accepts a molecule identifier in four forms —
``--cid`` (PubChem compound ID), ``--name``, ``--smiles`` or ``--inchi`` —
and writes one file per molecule to a local folder.

Command overview
----------------

.. list-table::
   :header-rows: 1
   :widths: 32 68

   * - Command
     - What it does
   * - ``manim-chemistry --help``
     - List the command group and its subcommands.
   * - ``manim-chemistry pubchem-molecule --help``
     - Show every option, alias, and default.
   * - ``manim-chemistry pubchem-molecule --name acetone``
     - Download acetone and write ``acetone.sdf``.
   * - ``manim-chemistry pubchem-molecule --name acetone --format json``
     - Download the same molecule as ``acetone.json``.
   * - ``manim-chemistry pubchem-molecule --name acetone --output_folder molecules``
     - Write into an existing or newly created ``molecules`` folder.

Options
-------

.. list-table::
   :header-rows: 1
   :widths: 26 14 60

   * - Option
     - Default
     - Purpose
   * - ``-f`` / ``--format``
     - ``sdf``
     - Output format: ``sdf``, ``asnt``, ``json`` or ``xml``.
   * - ``-c`` / ``--cid``
     - none
     - PubChem compound ID. Repeatable.
   * - ``-n`` / ``--name``
     - none
     - Compound name. Repeatable.
   * - ``-s`` / ``--smiles``
     - none
     - SMILES string. Repeatable; quote strings containing spaces.
   * - ``-i`` / ``--inchi``
     - none
     - Full InChI or InChIKey. Repeatable; quote the full InChI.
   * - ``-td`` / ``--three_d``
     - ``False``
     - Request 3-D coordinates. This option takes a boolean value.
   * - ``-o`` / ``--output_folder``
     - current directory
     - Destination folder; created if it does not exist.

Download by name
----------------

The simplest invocation passes a compound name:

.. nbcell::
   :language: console
   :prompt-in: "$"

   manim-chemistry pubchem-molecule --name acetone

The command prints the identifier it is about to fetch, asks PubChem for
the record, then reports each file as it is written. With the defaults,
the result is ``./acetone.sdf``.

Several molecules of the same kind
----------------------------------

Every identifier option is repeatable. Repeating the same option downloads
several molecules in one invocation and writes one file per value:

.. nbcell::
   :language: console
   :prompt-in: "$"

   manim-chemistry pubchem-molecule --name acetone --name morphine

.. note::

   Use one identifier family per invocation. The command does not merge
   different families: if both ``--cid`` and ``--name`` are supplied,
   ``--cid`` wins; after that the precedence is ``--name``, then
   ``--smiles``, then ``--inchi``. To download a mix of CIDs and names,
   either run the command once per family or resolve the names to CIDs
   first.

Choosing the identifier type
----------------------------

A PubChem CID is the most stable identifier:

.. nbcell::
   :language: console
   :prompt-in: "$"

   manim-chemistry pubchem-molecule --cid 180

SMILES is convenient when the structure is already known:

.. nbcell::
   :language: console
   :prompt-in: "$"

   manim-chemistry pubchem-molecule --smiles "CC(=O)C"

A full InChI contains slashes, so quote it in the shell:

.. nbcell::
   :language: console
   :prompt-in: "$"

   manim-chemistry pubchem-molecule --inchi "InChI=1S/C3H6O/c1-3(2)4/h1-2H3"

An InChIKey is accepted through the same ``--inchi`` option:

.. nbcell::
   :language: console
   :prompt-in: "$"

   manim-chemistry pubchem-molecule --inchi CSCPPACGZOOCGX-UHFFFAOYSA-N

Output formats
--------------

``--format`` changes the file type written for every downloaded molecule.
The extension is part of the output name, so downstream readers can pick
the parser from the suffix:

.. nbcell::
   :language: console
   :prompt-in: "$"

   manim-chemistry pubchem-molecule --name acetone --format json

.. list-table::
   :header-rows: 1
   :widths: 16 56 28

   * - Format
     - File content
     - Reader
   * - ``sdf``
     - Structure-Data File; the default.
     - :class:`~manim_extensions.chemistry.utils.parsers.sdf_parser.SDFParser`
   * - ``asnt``
     - Abstract Syntax Notation text.
     - :class:`~manim_extensions.chemistry.utils.parsers.asnt_parser.ASNTParser`
   * - ``json``
     - JSON representation.
     - :class:`~manim_extensions.chemistry.utils.parsers.json_parser.JSONParser`
   * - ``xml``
     - XML representation.
     - :class:`~manim_extensions.chemistry.utils.parsers.xml_parser.XMLParser`

All four suffixes are understood by
:meth:`~manim_extensions.chemistry.molecule.abstract_molecule.AbstractMolecule.molecule_from_file`,
which selects the parser from the file extension. The four values above are
the supported set; Click does not reject other strings, so unsupported
values fail inside the PubChem client rather than at option parsing.

Three-dimensional data
----------------------

By default the downloaded structures are 2-D. Set ``--three_d`` to ``True``
to ask PubChem for three-dimensional coordinates, which is what
:class:`~manim_extensions.chemistry.threeD.threedmolecule.ThreeDMolecule`
expects:

.. nbcell::
   :language: console
   :prompt-in: "$"

   manim-chemistry pubchem-molecule --name acetone --three_d True

``--three_d`` is a value-taking boolean option, not a bare flag: pass
``True`` or ``False``. The output format is unchanged; the difference is
the coordinate set inside the file.

Choosing a destination folder and file names
--------------------------------------------

``--output_folder`` accepts a path and creates the directory when needed:

.. nbcell::
   :language: console
   :prompt-in: "$"

   manim-chemistry pubchem-molecule --name acetone --output_folder molecules

The output name is the identifier plus the format extension. Characters
that cannot safely appear in a file name are replaced with ``_``. For
example, the slashes in a full InChI become underscores in the ``.sdf``
file name. If the same identifier is downloaded twice with the same
format, the existing file is overwritten.

Using the downloaded files in Python
------------------------------------

The files are ordinary chemistry files and can be loaded by the molecule
classes:

.. code-block:: python

   from manim_extensions.chemistry import MMoleculeObject

   molecule = MMoleculeObject.molecule_from_file("molecules/acetone.sdf")

For a 3-D download, use the 3-D molecule class:

.. code-block:: python

   from manim_extensions.chemistry import ThreeDMolecule

   molecule = ThreeDMolecule.molecule_from_file("molecules/acetone.sdf")

The graph-based representation accepts the same files:

.. code-block:: python

   from manim_extensions.chemistry import GraphMolecule

   molecule = GraphMolecule.molecule_from_file("molecules/acetone.sdf")

Error handling
--------------

At least one identifier is required. If none of ``--cid``, ``--name``,
``--smiles`` or ``--inchi`` is supplied, the command prints the empty
identifier and raises an exception before downloading anything. Invalid
PubChem identifiers and network failures surface as exceptions from the
PubChem client; the command does not silently create empty files.

API reference
-------------

.. autofunction:: manim_extensions.chemistry.cli.cli

.. autofunction:: manim_extensions.chemistry.cli.pubchem_molecule

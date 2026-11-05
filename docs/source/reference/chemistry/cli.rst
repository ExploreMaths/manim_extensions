.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Command-line interface
======================

.. module:: manim_extensions.chemistry.cli

The chemistry subpackage ships a small `Click
<https://click.palletsprojects.com/>`_-based command-line client for
downloading molecule data from `PubChem <https://pubchem.ncbi.nlm.nih.gov/>`_
without writing any Python. Installing the package registers a
``manim-chemistry`` command; the examples below use it:

.. nbcell::
   :language: console
   :prompt-in: "$"
   :output: Usage: manim-chemistry [OPTIONS] COMMAND [ARGS]...
       Options:
         --help  Show this message and exit.
       Commands:
         pubchem-molecule  Download molecule from pubchem.

   manim-chemistry --help

``pubchem-molecule`` accepts a molecule identifier in four forms —
``--cid`` (PubChem compound ID), ``--name``, ``--smiles`` or ``--inchi`` —
each of which may be given multiple times to fetch several molecules in a
single request. ``--format`` selects the output file format (``sdf`` by
default, also ``asnt``, ``json`` or ``xml``), ``--three_d`` requests
three-dimensional coordinates, and ``--output_folder`` chooses where the
files are written.

Download by name
----------------

.. nbcell::
   :language: console
   :prompt-in: "$"
   :output: Retrieved molecule data for ('acetone',). Saving file(s) to . folder.
       File ./acetone.sdf is ready!!
       Finished

   manim-chemistry pubchem-molecule --name acetone

Several identifiers at once
---------------------------

Every identifier option accepts multiple values, and the identifiers may
even be mixed (names, CIDs, SMILES and InChI in one call):

.. nbcell::
   :language: console
   :prompt-in: "$"
   :output: Retrieved molecule data for ('acetone', 'morphine'). Saving file(s) to . folder.
       File ./acetone.sdf is ready!!
       File ./morphine.sdf is ready!!
       Finished

   manim-chemistry pubchem-molecule --name acetone --name morphine

Choosing the identifier type
----------------------------

.. nbcell::
   :language: console
   :prompt-in: "$"
   :output: Retrieved molecule data for ('7028',). Saving file(s) to . folder.
       File ./7028.sdf is ready!!
       Finished

   manim-chemistry pubchem-molecule --cid 7028

.. nbcell::
   :language: console
   :prompt-in: "$"
   :output: Retrieved molecule data for ('CC(=O)C',). Saving file(s) to . folder.
       File ./CC(=O)C.sdf is ready!!
       Finished

   manim-chemistry pubchem-molecule --smiles "CC(=O)C"

.. nbcell::
   :language: console
   :prompt-in: "$"
   :output: Retrieved molecule data for ('InChI=1S/C3H6O/c1-3(2)4/h1-2H3',). Saving file(s) to . folder.
       File ./InChI_1S_C3H6O_c1-3_2_4_h1-2H3.sdf is ready!!
       Finished

   manim-chemistry pubchem-molecule --inchi "InChI=1S/C3H6O/c1-3(2)4/h1-2H3"

An InChIKey works as well, and the ``/`` characters of a full InChI are
turned into ``_`` in the output file name:

.. nbcell::
   :language: console
   :prompt-in: "$"
   :output: Retrieved molecule data for ('CSCPPACGZOOCGX-UHFFFAOYSA-N',). Saving file(s) to . folder.
       File ./CSCPPACGZOOCGX-UHFFFAOYSA-N.sdf is ready!!
       Finished

   manim-chemistry pubchem-molecule --inchi CSCPPACGZOOCGX-UHFFFAOYSA-N

Output formats
--------------

``--format`` changes the file type written for every downloaded molecule;
the files can then be fed straight back into
MMoleculeObject.molecule_from_file()
or GraphMolecule.molecule_from_file():

.. nbcell::
   :language: console
   :prompt-in: "$"
   :output: Retrieved molecule data for ('acetone',). Saving file(s) to . folder.
       File ./acetone.json is ready!!
       Finished

   manim-chemistry pubchem-molecule --name acetone --format json

Available formats are ``sdf`` (default), ``asnt``, ``json`` and ``xml``.

Three-dimensional data
----------------------

By default the downloaded structures are 2-D; pass ``--three_d`` to ask
PubChem for three-dimensional coordinates (e.g. for
:class:`~manim_extensions.chemistry.threeD.threedmolecule.ThreeDMolecule`):

.. nbcell::
   :language: console
   :prompt-in: "$"
   :output: Retrieved molecule data for ('acetone',). Saving file(s) to . folder.
       File ./acetone.sdf is ready!!
       Finished

   manim-chemistry pubchem-molecule --name acetone --three_d True

Choosing a destination folder
-----------------------------

.. nbcell::
   :language: console
   :prompt-in: "$"
   :output: Retrieved molecule data for ('acetone',). Saving file(s) to molecules folder.
       File molecules/acetone.sdf is ready!!
       Finished

   manim-chemistry pubchem-molecule --name acetone --output_folder molecules

.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Chemistry
=========

.. vendored-status:: UnMolDeQuimica/manim-Chemistry

**Original author:** `UMDQ <https://github.com/UnMolDeQuimica>`_

**Source repository:** `GitHub <https://github.com/UnMolDeQuimica/manim-Chemistry>`_

**License:** MIT

``manim-Chemistry`` is a chemistry visualisation toolkit for Manim. It
provides periodic-table elements, 2-D / 3-D molecule rendering, Bohr atoms,
orbital diagrams, and a PubChem API client for fetching molecular data.

The code is bundled inside ``manim_extensions`` as the
``manim_extensions.chemistry`` subpackage.

Features
--------

- :class:`~manim_extensions.chemistry.element.element.Element` – chemical
  element data model (symbol, name, atomic number, mass, colour, etc.).
- :class:`~manim_extensions.chemistry.periodic_table.table_objects.PeriodicTable`
  – full periodic-table layout as a Manim mobject.
- :class:`~manim_extensions.chemistry.twoD.molecule.MMoleculeObject` – 2-D
  molecule from a file or SMILES string.
- :class:`~manim_extensions.chemistry.twoD.graph_molecule.GraphMolecule` –
  graph-based molecule representation using ``networkx``.
- :class:`~manim_extensions.chemistry.threeD.threedmolecule.ThreeDMolecule` –
  interactive 3-D molecule viewer.
- :class:`~manim_extensions.chemistry.bohr_atom.bohr_atom.BohrAtom` – Bohr
  atomic model animation.
- :class:`~manim_extensions.chemistry.orbitals.orbitals.Orbital` – atomic
  orbital visualisation.
- :class:`~manim_extensions.chemistry.molecule.molecule.Molecule` – unified
  facade that loads molecules from files, strings, or PubChem.
- :class:`~manim_extensions.chemistry.utils.pubchem_api.PubchemAPIManager` –
  PubChem REST API client.

Quick start
-----------

.. manim:: ChemistryExample
   :save_last_frame:

   import pandas as pd
   from manim import *
   from manim_extensions.chemistry import Element, PeriodicTable
   from manim_extensions.chemistry.manim_chemistry_molecule import MC_ELEMENT_DICT

   class ChemistryExample(Scene):
       def construct(self):
           data = pd.DataFrame(
               {
                   "AtomicNumber": [e.atomic_number for e in MC_ELEMENT_DICT.values()],
                   "AtomicMass": [e.mass for e in MC_ELEMENT_DICT.values()],
                   "Name": [e.name for e in MC_ELEMENT_DICT.values()],
                   "Symbol": [e.symbol for e in MC_ELEMENT_DICT.values()],
                   "Color": [e.color for e in MC_ELEMENT_DICT.values()],
               }
           )
           data.to_csv("element_data.csv", index=False)
           table = PeriodicTable(data_file="element_data.csv")
           table.scale(1.3)
           self.add(table)

.. toctree::
   :hidden:

   classes
   functions
   constants

.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Chemistry
=========

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

   from manim import *
   from manim_extensions.chemistry import Element, PeriodicTable

   class ChemistryExample(Scene):
       def construct(self):
           table = PeriodicTable()
           table.scale(0.35)
           self.add(table)

.. toctree::
   :hidden:

   classes

.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

molecule
========

.. module:: manim_extensions.chemistry.molecule

Classes
-------

.. autosummary::
   :nosignatures:

   ~molecule.Molecule

Usage
-----

Load a MOL file and get a ready-to-add molecule mobject.

.. code-block:: python

   from manim import *
   from manim_extensions.chemistry.molecule import Molecule

   class MoleculeScene(Scene):
       def construct(self):
           molecule = Molecule().molecule_from_file("acetone_2d.mol")
           self.play(FadeIn(molecule))

Modules
-------

.. autosummary::
   :nosignatures:

   ~abstract_molecule
   ~molecule

.. toctree::
   :hidden:
   :maxdepth: 1

   abstract_molecule
   molecule

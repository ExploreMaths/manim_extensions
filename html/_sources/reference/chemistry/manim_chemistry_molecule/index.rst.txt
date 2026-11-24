.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

manim_chemistry_molecule
========================

.. module:: manim_extensions.chemistry.manim_chemistry_molecule

The original ``MC*`` API, kept for backwards compatibility.

Usage
-----

Represent a molecule as atoms and bonds, then feed it to a 2D or 3D renderer.

.. code-block:: python

   from manim_extensions.chemistry.manim_chemistry_molecule import (
       MCAtom,
       MCBond,
       MCElement,
       MCMolecule,
   )

   carbon = MCElement(symbol="C", name="Carbon", atomic_number=6, mass=12.011)
   hydrogen = MCElement(symbol="H", name="Hydrogen", atomic_number=1, mass=1.008)
   c = MCAtom(carbon, coords=(0, 0, 0))
   h = MCAtom(hydrogen, coords=(1.09, 0, 0))
   molecule = MCMolecule(
       atoms=[c, h],
       bonds=[MCBond(1, from_atom=c, to_atom=h)],
       name="methane fragment",
   )

Modules
-------

.. autosummary::
   :nosignatures:

   ~mc_atom
   ~mc_bond
   ~mc_element
   ~mc_molecule

.. toctree::
   :hidden:
   :maxdepth: 1

   mc_atom
   mc_bond
   mc_element
   mc_molecule

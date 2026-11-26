.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

utils
=====

.. automodule:: manim_extensions.chemistry.utils

Classes
-------

.. autosummary::
   :nosignatures:

   ~manim_extensions.chemistry.threeD.utils.OpenGLSphere

Usage
-----

Parse a chemical file and get the atom/bond dictionaries used by the molecule renderers.

.. code-block:: python

   from manim_extensions.chemistry.utils import FileHandler

   atoms, bonds = FileHandler("acetone_2d.mol").parsed_atoms_bonds_data()

Modules
-------

.. autosummary::
   :nosignatures:

   ~file_handler
   ~parsers
   ~pubchem_api
   ~utils

.. toctree::
   :hidden:
   :maxdepth: 1

   file_handler
   parsers/index
   pubchem_api
   utils

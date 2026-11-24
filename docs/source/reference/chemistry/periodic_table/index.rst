.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

periodic_table
==============

.. module:: manim_extensions.chemistry.periodic_table

Usage
-----

Build the periodic table from the bundled element CSV.

.. code-block:: python

   from manim import *
   from manim_extensions.chemistry.periodic_table import PeriodicTable

   class TableScene(Scene):
       def construct(self):
           table = PeriodicTable("element_data.csv")
           table.scale_to_fit_height(6)
           self.add(table)

Modules
-------

.. autosummary::
   :nosignatures:

   ~table_objects

.. toctree::
   :hidden:
   :maxdepth: 1

   table_objects

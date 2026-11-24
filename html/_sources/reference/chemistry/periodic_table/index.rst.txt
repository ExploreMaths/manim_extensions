.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

periodic_table
==============

.. module:: manim_extensions.chemistry.periodic_table

Usage
-----

Build the periodic table from the bundled element CSV.

.. manim:: PeriodicTableOverview
   :save_last_frame:
   :ref_classes: PeriodicTable

   import pandas as pd
   from manim import *
   from manim_extensions.chemistry import PeriodicTable
   from manim_extensions.chemistry.manim_chemistry_molecule import MC_ELEMENT_DICT

   class PeriodicTableOverview(Scene):
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

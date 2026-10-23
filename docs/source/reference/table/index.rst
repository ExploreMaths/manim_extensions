.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Table
=====

.. vendored-status:: philippe2803/manim-table

**Original author:** `Philippe Oger <https://github.com/philippe2803>`_

**Source repository:** `GitHub <https://github.com/philippe2803/manim-table>`_

**License:** MIT

``manim-table`` is a database-style table animation extension for Manim
Community Edition. It supports animated row/column insertion and deletion,
cell value updates, resizing, and styling.

The code is bundled inside ``manim_extensions`` as the
``manim_extensions.table`` subpackage.

Features
--------

- :class:`~manim_extensions.table.table.Table` – the main table mobject.
  Construct from a list of rows or from separate header + data rows.
- :class:`~manim_extensions.table.row.Row` – a single table row.
- :class:`~manim_extensions.table.cell.Cell` – a single table cell with
  border, background, and text.

Usage
-----

Create a table from a list of rows; the first row is treated as the header.

.. code-block:: python

   from manim import *

   from manim_extensions.table import Table

   class TableExample(Scene):
       def construct(self):
           data = [
               ["Name", "Age", "City"],
               ["Alice", "25", "New York"],
               ["Bob", "30", "Paris"],
           ]

           # Create the table
           table = Table(data)

           # Animate it
           self.play(Write(table))

Add or remove rows and columns with animations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``add_row`` and ``delete_row`` return the affected
:class:`~manim_extensions.table.row.Row` together with the list of animations
to play (row index 1 is the first data row):

.. code-block:: python

   # Add a new row
   new_row, anims = table.add_row(["Charlie", "35", "London"])
   self.play(AnimationGroup(*anims, lag_ratio=0.05))

   # Delete a row (index starts at 1 for data rows)
   deleted_row, anims = table.delete_row(1)
   self.play(AnimationGroup(*anims, lag_ratio=0.05))

Styling
^^^^^^^

Change colors and styles per header, column, or individual cell:

.. code-block:: python

   from manim import BLUE, RED

   # Style the header
   table.set_header_background_color(BLUE)

   # Style specific cells (row, column); row 0 is the header,
   # row 1 is the first data row
   table.get_cell(1, 1).set_font_color(RED)

.. toctree::
   :maxdepth: 1

   classes
   constants

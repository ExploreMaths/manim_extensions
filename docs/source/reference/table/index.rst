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

.. toctree::
   :maxdepth: 1

   classes
   constants

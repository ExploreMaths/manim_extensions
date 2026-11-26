.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

element
=======

.. automodule:: manim_extensions.chemistry.element

Classes
-------

.. autosummary::
   :nosignatures:

   ~element.Element
   ~element.GenericElement

Usage
-----

Read an element record from the bundled CSV data or construct one directly.

.. code-block:: python

   from manim_extensions.chemistry.element import Element

   hydrogen = Element.from_csv_file("element_data.csv", "H")
   carbon = Element(symbol="C", name="Carbon", atomic_number=6, mass=12.011)

Modules
-------

.. autosummary::
   :nosignatures:

   ~element

.. toctree::
   :hidden:
   :maxdepth: 1

   element

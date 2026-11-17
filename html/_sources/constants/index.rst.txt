.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Constants
=========

Manim's official documentation lists the ten direction vectors and the
colour palette, but the Manim intersphinx inventory contains *no*
constant entries at all — WHITE,
UP and SMALL_BUFF
cannot be linked to the official docs.  They are collected here so every
constant name has a link target, and you can write the name (``from
manim import *`` gives you all of them) instead of expanding the value
by hand, e.g. use SMALL_BUFF instead of ``0.2``.

Categories
----------

The constants are grouped by category:

- :doc:`directions` – direction vectors.
- :doc:`fonts` – font weights and styles.
- :doc:`defaults` – ``DEFAULT_*`` values.
- :doc:`buffers` – ``*_BUFF`` spacing values.
- :doc:`axes` – axis constants.
- :doc:`numeric` – numeric constants.
- :doc:`messages` – runtime messages.
- :doc:`colors` – colour palette.

.. toctree::
   :maxdepth: 1
   :hidden:

   directions
   fonts
   defaults
   buffers
   axes
   numeric
   messages
   colors

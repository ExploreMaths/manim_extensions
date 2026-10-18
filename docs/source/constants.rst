.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Constants
=========

Manim's official documentation lists the ten direction vectors and the
colour palette, but the Manim intersphinx inventory contains *no*
constant entries at all — ``WHITE``, ``UP``, ``SMALL_BUFF`` etc. cannot
be linked to the official docs.  They are collected here so every
constant name has a link target, and you can write the name (``from
manim import *`` gives you all of them) instead of expanding the value
by hand, e.g. use ``SMALL_BUFF`` instead of ``0.2``.

The constants are grouped by category:

- :doc:`constants/directions` – direction vectors.
- :doc:`constants/fonts` – font weights and styles.
- :doc:`constants/defaults` – ``DEFAULT_*`` values.
- :doc:`constants/buffers` – ``*_BUFF`` spacing values.
- :doc:`constants/axes` – axis constants.
- :doc:`constants/numeric` – numeric constants.
- :doc:`constants/messages` – runtime messages.
- :doc:`constants/colors` – colour palette.

.. toctree::
   :maxdepth: 1
   :hidden:

   constants/directions
   constants/fonts
   constants/defaults
   constants/buffers
   constants/axes
   constants/numeric
   constants/messages
   constants/colors

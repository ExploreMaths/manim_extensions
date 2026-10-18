.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Constants
=========

Manim's official documentation lists the ten direction vectors
(``ORIGIN``/``UP``/``DOWN``/``LEFT``/``RIGHT``/``IN``/``OUT``/``UL``/
``UR``/``DL``/``DR``) and the colour palette, but many constants that
exist in :mod:`manim.constants` are *not* documented there.  They are
collected here so you can write the name (``from manim import *`` gives
you all of them) instead of expanding the value by hand, e.g. use
``SMALL_BUFF`` instead of ``0.2``.

The constants are grouped by category:

- :doc:`constants/fonts` – font weights and styles.
- :doc:`constants/defaults` – ``DEFAULT_*`` values.
- :doc:`constants/buffers` – ``*_BUFF`` spacing values.
- :doc:`constants/axes` – axis constants.
- :doc:`constants/numeric` – numeric constants.
- :doc:`constants/messages` – runtime messages.

.. toctree::
   :maxdepth: 1

   constants/fonts
   constants/defaults
   constants/buffers
   constants/axes
   constants/numeric
   constants/messages

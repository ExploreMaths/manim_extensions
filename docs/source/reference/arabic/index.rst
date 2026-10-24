.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Arabic
======

.. vendored-status:: razekmh/manim-arabic

**Original author:** `Mahmoud Abdelrazek <https://github.com/razekmh>`_

**Source repository:** `GitHub <https://github.com/razekmh/manim-arabic>`_

**License:** MIT

``manim-arabic`` provides Arabic text rendering helpers for Manim. Arabic
script is written right-to-left and requires ligature shaping; these helpers
take care of the necessary transformations so that Arabic text displays
correctly in Manim scenes.

The code is bundled inside ``manim_extensions`` as the
``manim_extensions.arabic`` subpackage.

Features
--------

- :func:`~manim_extensions.arabic.text.create_arabic_template` – create a
  Tex template configured for Arabic typesetting.
- :func:`~manim_extensions.arabic.text.create_arabic_text` – create a
  Manim ``Text`` mobject with proper Arabic shaping.

Requirements
------------

The helpers render through XeLaTeX (TeX Live, MacTeX, or MiKTeX) with the
``fontspec`` and ``xcolor`` packages, so a working XeLaTeX toolchain must be
available. An Arabic-capable font must also be installed on the system
(upstream suggests "Al Bayan" or "Geeza Pro" on macOS, and "Arial Unicode MS"
as a cross-platform option). The vendored build probes installed fonts via
fontconfig and falls back through "Al Bayan", "Geeza Pro", "Amiri",
"Scheherazade", "Noto Naskh Arabic", and "Arial Unicode MS" when no font is
given explicitly.

Usage
-----

.. code-block:: python

   from manim import Scene, Write
   from manim_extensions.arabic import create_arabic_text


   class ArabicExample(Scene):
       def construct(self):
           label = create_arabic_text("مرحبا", color="arabicblue", font_size=48)
           self.play(Write(label))
           self.wait()

:func:`~manim_extensions.arabic.text.create_arabic_text` takes
``text``, ``color="arabicblue"``, ``font_size=34`` and ``font_name=None``
and returns a Manim ``Tex`` mobject. For lower-level control,
:func:`~manim_extensions.arabic.text.create_arabic_template` with
``font_name="Al Bayan"`` returns a configured ``TexTemplate``.

Built-in colors
---------------

The template predefines three LaTeX color names:

- ``arabicblue`` — RGB (68, 114, 196)
- ``arabicgreen`` — RGB (112, 173, 71)
- ``arabicred`` — RGB (192, 0, 0)

Any other color name supported by ``xcolor`` can be passed to ``color`` as
well.

.. toctree::
   :hidden:
   :maxdepth: 1

   functions

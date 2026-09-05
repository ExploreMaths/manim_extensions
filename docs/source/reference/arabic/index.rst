.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Arabic
======

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

Quick start
-----------

.. manim:: ArabicExample
   :save_last_frame:

   from manim import *
   from manim_extensions.arabic import create_arabic_text

   class ArabicExample(Scene):
       def construct(self):
           text = create_arabic_text("مرحبا بالعالم")
           self.add(text)

.. toctree::
   :hidden:

   functions

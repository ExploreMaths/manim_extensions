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

- :class:`~manim_extensions.arabic.text.ArabicTemplate` – a Tex template
  configured for Arabic typesetting.
- :class:`~manim_extensions.arabic.text.ArabicText` – a Manim ``Tex`` mobject
  with proper Arabic shaping.

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

.. manim:: ArabicGreeting
   :ref_classes: ArabicText

   from manim import Scene, Write, FadeOut
   from manim_extensions.arabic import ArabicText

   class ArabicGreeting(Scene):
       def construct(self):
           label = ArabicText("مرحبا", color="arabicblue", font_size=48)
           self.play(Write(label.scale(4)))
           # fade the greeting back out so the first and last frames match
           # and the animation loops seamlessly
           self.play(FadeOut(label))

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

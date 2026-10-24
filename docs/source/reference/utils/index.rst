.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Utilities
=========

.. vendored-status:: Alexander-Nasuta/manim-nerdfont-icons

Helper subpackages: ``manim_extensions.utils.deps`` (lazy optional
dependency loading), ``manim_extensions.utils.deprecation`` (RST-aware
:func:`~manim_extensions.utils.deprecation.deprecated` decorator) and
``manim_extensions.utils.nerdfont`` (vendored Nerd Font icons).

Nerd Font Icons
---------------

``manim_extensions.utils.nerdfont`` is a vendored copy of
``manim-nerdfont-icons`` (see the vendored-status directive above). It
provides icons from the `Nerd Fonts <https://www.nerdfonts.com/>`_ project
for use in Manim. Manim can use any font in principle, and Nerd Font icons
are no exception: this module lets you build a Nerd Font icon by
referencing its icon name or its Unicode codepoint, which is more convenient
than copy-pasting raw glyph strings into your code. The matching Symbols
Nerd Font Mono TTF is bundled inside the package and registered
automatically, so you do not need a Nerd Font installed on your system.
Because the code is bundled in ``manim_extensions``, no separate
``pip install manim-nerdfont-icons`` step is required.

Usage
^^^^^

Construct a :class:`~manim_extensions.utils.nerdfont.icons.NerdFontIcon`
(an :class:`~manim.mobject.text.text_mobject.Text` subclass) and add it to
the scene. The ``icon`` argument accepts three forms:

- an icon name resolved through
  :data:`~manim_extensions.utils.nerdfont.icons_dict.SYMBOLS_UNICODE`,
  e.g. ``"language-python"``;
- an integer Unicode code point, e.g. ``9829``;
- any literal string, rendered as-is.

All extra keyword arguments are forwarded to
:class:`~manim.mobject.text.text_mobject.Text`, so ``color``, ``font_size``
and the usual ``Text`` options work as expected. Render the scene normally
with the ``manim`` command.

.. manim:: NerdfontIconExample
   :ref_classes: NerdFontIcon
   :save_last_frame:

   import manim as m

   from manim_extensions.utils.nerdfont import NerdFontIcon


   class NerdfontIconExample(m.Scene):

       def construct(self):
           # Set the background color
           self.camera.background_color = "#ece6e2"

           icon = NerdFontIcon("language-python", color=m.BLUE)

           self.add(icon)

Icon sets and lookup
^^^^^^^^^^^^^^^^^^^^

The library ships about 10 000 icons. The upstream
`icon gallery <https://manim-nerdfont-icons.readthedocs.io/en/latest/icon-gallery.html>`_
lists them all in a table of icon name, Unicode codepoint, integer value
and glyph preview; the upstream
`home page <https://manim-nerdfont-icons.readthedocs.io/en/latest/>`_ also
collects an example gallery of short code snippets with their output. To
look icons up by glyph shape, use the `Nerd Font Cheat Sheet
<https://www.nerdfonts.com/cheat-sheet>`_; note that the cheat-sheet names
do not always match the names in this library — in that case use the
Unicode codepoint to find the icon you want.

.. toctree::
   :hidden:
   :maxdepth: 1

   classes
   functions
   constants

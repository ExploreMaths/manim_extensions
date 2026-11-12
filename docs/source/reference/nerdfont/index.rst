.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Nerd Font Icons
===============

.. module:: manim_extensions.nerdfont

.. vendored-status:: Alexander-Nasuta/manim-nerdfont-icons

``manim_extensions.nerdfont`` is a vendored copy of
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
-----

Construct a :class:`~manim_extensions.nerdfont.icons.NerdFontIcon`
(an :class:`~manim.mobject.text.text_mobject.Text` subclass) and add it to
the scene. The ``icon`` argument accepts three forms:

- an icon name resolved through
  :data:`~manim_extensions.nerdfont.icons_dict.SYMBOLS_UNICODE`,
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

   from manim import *

   from manim_extensions.nerdfont import NerdFontIcon

   class NerdfontIconExample(Scene):
       def construct(self):
           # Set the background color
           self.camera.background_color = "#ece6e2"

           icon = NerdFontIcon("language-python", color=BLUE)

           self.add(icon.scale(6))

Icon sets and lookup
--------------------

The library ships about 10 000 icons. See :doc:`icon_gallery` for a
searchable, filterable gallery of every icon (name, Unicode codepoint and
glyph preview); the upstream
`icon gallery <https://manim-nerdfont-icons.readthedocs.io/en/latest/icon-gallery.html>`_
and `home page <https://manim-nerdfont-icons.readthedocs.io/en/latest/>`_
collect the same data as tables and short code snippets. To look icons up
by glyph shape, use the `Nerd Font Cheat Sheet
<https://www.nerdfonts.com/cheat-sheet>`_; note that the cheat-sheet names
do not always match the names in this library — in that case use the
Unicode codepoint to find the icon you want.

Modules
-------

.. autosummary::
   :nosignatures:

   ~icons
   ~icons_dict

Constants
---------

.. autoall:: manim_extensions.nerdfont
   :types: data

.. toctree::
   :hidden:
   :maxdepth: 1

   icon_gallery
   icons
   icons_dict

.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Frequently Asked Questions
==========================

Do I need to install LaTeX?
---------------------------

Only if you want to use :class:`~manim_extensions.mobjects.ChineseMathTex`.
For English-only formulas, Manim's default :class:`~manim.MathTex` works
without additional LaTeX packages.

Which Python versions are supported?
------------------------------------

``manim_extensions`` supports Python 3.11 through 3.14.

Can I use the bundled plugins without installing ``manim_extensions``?
----------------------------------------------------------------------

Yes. The plugins are also available from their original repositories and are
kept as subpackages within ``manim_extensions``. However, installing
``manim_extensions`` lets you import them directly from the package namespace
and guarantees compatible versions.

Why does my example render as a still image instead of a video?
---------------------------------------------------------------

The ``.. manim::`` directive renders a video by default. If you add the
``:save_last_frame:`` option, it renders only the last frame as an image. Use
that option for static scenes and omit it for animations.

How do I report a bug or request a feature?
-------------------------------------------

Open an issue on the `GitHub repository <https://github.com/ExploreMaths/manim_extensions/issues>`_.
.. manim_extensions documentation master file

================
Manim Extensions
================

**manim_extensions** is an extension toolkit for `Manim Community <https://www.manim.community/>`_,
providing extra mobjects, geometric utilities, animation effects, and curated
third-party plugins to help you create mathematical animations more efficiently.

What is in this package?
========================

The library is organised into four areas:

**Core extensions** (``manim_extensions``)
    Additional mobjects and helpers built directly on top of Manim:

    * :class:`~manim_extensions.mobjects.ChineseMathTex` – Chinese-aware LaTeX
      rendering with ``xeCJK``.
    * :class:`~manim_extensions.mobjects.LabelDot`,
      :class:`~manim_extensions.mobjects.MathTexLine`,
      :class:`~manim_extensions.mobjects.MathTexBrace`,
      :class:`~manim_extensions.mobjects.MathTexDoublearrow` – annotated
      geometric primitives.
    * :class:`~manim_extensions.mobjects.ExtendedLine`,
      :class:`~manim_extensions.mobjects.PerpendicularLine`,
      :class:`~manim_extensions.mobjects.PerpendicularSign` – construction-style
      line helpers.
    * :class:`~manim_extensions.mobjects.FileTree` – ASCII file-tree rendering
      from a nested dictionary.
    * :class:`~manim_extensions.mobjects.CropImageMobject` – image mobject with
      rounded-corner cropping via an alpha mask.
    * :class:`~manim_extensions.mobjects.VideoMobject` – video playback mobject
      built on OpenCV.
    * :func:`~manim_extensions.geometry.CircleInt`,
      :func:`~manim_extensions.geometry.LineCircleInt`,
      :func:`~manim_extensions.geometry.LineInt`,
      :func:`~manim_extensions.geometry.LineArcInt`,
      :func:`~manim_extensions.geometry.TangentPoint` – analytic geometry
      utilities.
    * :func:`~manim_extensions.animations.VisDrawArc` and
      :class:`~manim_extensions.animations.TypeWriter` – ready-to-use
      animations.

**Bundled plugins**
    Three popular Manim plugins are included as subpackages and Git submodules,
    with full API documentation and attribution to the original authors:

    * :doc:`reference/gearbox/index` – realistic involute gears and mechanisms.
    * :doc:`reference/compass/index` – compass-and-straightedge constructions.
    * :doc:`reference/mindmap/index` – mind maps, timelines, and catalog trees.

Quick Links
===========

* **GitHub repository:** https://github.com/ExploreMaths/manim_extensions
* **PyPI package:** https://pypi.org/project/manim_extensions/
* **Manim Community:** https://www.manim.community/

Getting Started
===============

Install the latest stable release from PyPI:

.. code-block:: bash

   pip install manim_extensions

The only runtime dependency is `manim <https://pypi.org/project/manim/>`_.

Then head over to the :doc:`tutorials/quickstart` guide for a hands-on
introduction, or browse the :doc:`examples/index` gallery.

.. toctree::
   :maxdepth: 2
   :hidden:

   examples/index
   installation/index
   tutorials/index
   reference/index
   changelog
   contributing
   code_of_conduct

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

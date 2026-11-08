.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

.. manim_extensions documentation master file

================
Manim Extensions
================

**Manim Extensions** is an extension toolkit for `Manim Community <https://www.manim.community/>`_,
providing extra mobjects, geometric utilities, animation effects, and curated
third-party plugins to help you create mathematical animations more efficiently.

What is in this package?
========================

The library is organised into two areas:

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
* :func:`~manim_extensions.geometry.VMobjectInt`,
  :func:`~manim_extensions.geometry.TangentPoint` – geometry utilities
  for intersecting arbitrary VMobjects and finding circle tangent points.
* :class:`~manim_extensions.animations.TypeWriter` – ready-to-use
  animations.

**Bundled plugins**

Several popular Manim plugins are included as subpackages,
with full API documentation and attribution to the original authors:

* :vendorstatus:`algorithm` – algorithm visualization toolkit.
* :vendorstatus:`arabic` – Arabic text rendering helpers.
* :vendorstatus:`automata` – finite-state, pushdown, and Turing automata.
* :vendorstatus:`chemistry` – periodic table, molecules, orbitals, and Bohr atoms.
* :vendorstatus:`circuit` – circuit elements and diagrams.
* :vendorstatus:`compass` – compass-and-straightedge constructions.
* :vendorstatus:`data_structures` – array and variable visualization.
* :vendorstatus:`economics` – supply-demand, AD-AS, IS-LM, and Solow diagrams.
* :vendorstatus:`fontawesome` – 2 000+ Font Awesome SVG icons.
* :vendorstatus:`gearbox` – realistic involute gears and mechanisms.
* :vendorstatus:`machine_learning` – neural networks and decision tree diagrams.
* :vendorstatus:`meshes` – 2D/3D mesh data structures and visualization.
* :vendorstatus:`mindmap` – mind maps, timelines, and catalog trees.
* :vendorstatus:`nerdfont` – Nerd Font icon mobjects with a searchable gallery.
* :vendorstatus:`physics` – waves, mechanics, optics, and electromagnetism.
* :vendorstatus:`pymunk` – 2-D rigid-body physics simulation with Pymunk.
* :vendorstatus:`qr_codes` – QR code generation with optional Nerd Font icons.
* :vendorstatus:`rubikscube` – Rubik's cube mobject and animations.
* :vendorstatus:`sequence_diagram` – UML sequence diagram helpers.
* :vendorstatus:`svg_animations` – export scenes as interactive HTML/SVG animations.
* :vendorstatus:`table` – animated database tables, rows, and cells.
* :vendorstatus:`tikz` – TikZ diagram integration.
* :vendorstatus:`weighted_line` – weighted line mobject with midpoint weight labels.

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

The only runtime dependencies are `manim <https://pypi.org/project/manim/>`_
and `numpy <https://pypi.org/project/numpy/>`_ — everything else is
either bundled or an optional extra (see :doc:`installation/index`).

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
   vendored
   code_of_conduct

.. toctree::
   :maxdepth: 1
   :caption: Resources
   :hidden:

   constants
   GitHub Repository <https://github.com/ExploreMaths/manim_extensions>
   PyPI Package <https://pypi.org/project/manim_extensions/>
   Manim Community <https://www.manim.community/>
  

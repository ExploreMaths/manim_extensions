.. SPDX-FileCopyrightText: 2026 jj-math
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

MindMap
=======

.. vendored-status:: jj-math/manim-mindmap

**Original author:** `jj-math <https://github.com/jj-math>`_ (Bilibili creator **Jiujin Math**)

**Source repository:** `GitHub <https://github.com/jj-math/manim-mindmap>`_

**License:** MIT (see the upstream repository for the full license text)

:attr:`~manim_extensions.mindmap.algorithms.layout_config.LayoutType.MindMap` brings mind-map, timeline, and catalog / organisation-chart
diagrams to Manim. It is bundled inside ``manim_extensions`` as the
``manim_extensions.mindmap`` subpackage.

Features
--------

- :class:`~manim_extensions.mindmap.nodes.node.Node` – the basic tree-node class.
- :attr:`~manim_extensions.mindmap.algorithms.layout_config.LayoutType.MindMap` / :class:`~manim_extensions.mindmap.mindmap.mindmap.StandardMap` – mind-map classes with multiple layout directions.
- :class:`~manim_extensions.mindmap.mindmap.mindmap.CatalogMap` – organisation / directory-structure diagrams.
- :attr:`~manim_extensions.mindmap.algorithms.layout_config.LayoutType.TimeLine` – timeline diagrams.
- Animation helpers: :class:`~manim_extensions.mindmap.animations.animations.LayoutAnimation`, :class:`~manim_extensions.mindmap.animations.animations.InsertNode`, :class:`~manim_extensions.mindmap.animations.animations.RemoveNode`,
  :class:`~manim_extensions.mindmap.animations.animations.ScaleNode`, :class:`~manim_extensions.mindmap.animations.animations.AlterNode`.
- Styling / layout options: :class:`~manim_extensions.mindmap.nodes.node.NodeStyle`, :class:`~manim_extensions.mindmap.algorithms.layout_config.LayoutType`, :class:`~manim_extensions.mindmap.algorithms.layout_config.LayoutConfig`.

Layout types
^^^^^^^^^^^^

The ``layout_type`` argument of the animation classes accepts:

- :attr:`~manim_extensions.mindmap.algorithms.layout_config.LayoutType.MindMap` – default mind-map layout.
- :attr:`~manim_extensions.mindmap.algorithms.layout_config.LayoutType.Standard` – left/right or top/bottom two-sided layout.
- :attr:`~manim_extensions.mindmap.algorithms.layout_config.LayoutType.TimeLine` – timeline layout.
- :attr:`~manim_extensions.mindmap.algorithms.layout_config.LayoutType.Catalog` – top-down catalog / directory layout.

.. toctree::
   :maxdepth: 1

   nodes
   maps
   animations
   layout
   classes
   functions
   constants

See the `original README <https://github.com/jj-math/manim-mindmap>`_
for full animated demos and the complete API.

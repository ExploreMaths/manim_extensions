.. SPDX-FileCopyrightText: 2024 sinianluoye
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Algorithm
=========

.. vendored-status:: sinianluoye/manim-algorithm

**Original author:** `sinianluoye <https://github.com/sinianluoye>`_

**Source repository:** `GitHub <https://github.com/sinianluoye/manim-algorithm>`_

**License:** MIT (see the upstream repository for the full license text)

``manim-algorithm`` is a computer-science visualization toolkit for Manim. It
provides algorithmic objects such as nodes, arrays, queues, and code blocks that
can be used directly in classroom or tutorial scenes.

The code is bundled inside ``manim_extensions`` as the
``manim_extensions.algorithm`` subpackage.

Features
--------

- :class:`~manim_extensions.mindmap.nodes.node.Node` – node-like visual block for algorithm state display.
- :class:`~manim_extensions.algorithm.array.Array` – array-like structures for indexed values.
- :class:`~manim_extensions.algorithm.queue.Queue` – queue animation helpers and visual containers.
- animation helpers for selection, overwrite, update, and value transitions.

Status
------

The upstream project is still under internal development. It experiments with
Manim encapsulations that make it easier to display algorithms and data
structures, such as linked lists, arrays, and binary trees. It does not yet
accept external code contributions until it reaches a certain scale, though
suggestions and requests are welcome in the upstream repository. The package
targets Manim Community Edition (CE).

.. toctree::
   :maxdepth: 1

   classes
   constants
   functions

.. SPDX-FileCopyrightText: 2024 sinianluoye
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Algorithm
=========

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
- :class:`~manim_extensions.algorithm.code.Code` / :class:`~manim_extensions.algorithm.code.PythonCode` / :class:`~manim_extensions.algorithm.code.JavaCode` / :class:`~manim_extensions.algorithm.code.CppCode` – code blocks with
  syntax-oriented styling.
- animation helpers for selection, overwrite, update, and value transitions.

Quick start
-----------

.. manim:: AlgorithmLibraryExample
   :save_last_frame:

   from manim import *
   from manim_extensions.algorithm import Node, Queue

   class AlgorithmLibraryExample(Scene):
       def construct(self):
           left = Node("A")
           right = Node("B")
           queue = Queue(capacity=3, init_data=[left, right])
           self.add(queue)

The library is most useful when explaining:

* sorting and traversal steps,
* data structures in motion,
* algorithmic state updates and pointer movement,
* code-plus-visual narration during lectures.

See the `original README <https://github.com/sinianluoye/manim-algorithm>`_
for more complete examples and API details.

.. toctree::
   :hidden:

   classes
   functions
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

- ``Node`` – node-like visual block for algorithm state display.
- ``Array`` – array-like structures for indexed values.
- ``Queue`` – queue animation helpers and visual containers.
- ``Code`` / ``PythonCode`` / ``JavaCode`` / ``CppCode`` – code blocks with
  syntax-oriented styling.
- animation helpers for selection, overwrite, update, and value transitions.

Quick start
-----------

Import the package directly from the vendored namespace:

.. code-block:: python

   from manim import *
   from manim_extensions.algorithm import Node, Queue

   class AlgorithmExample(Scene):
       def construct(self):
           left = Node("A")
           right = Node("B")
           queue = Queue(capacity=3, init_data=[left, right])
           self.add(queue)
           self.wait(0.5)

A simple algorithm scene
^^^^^^^^^^^^^^^^^^^^^^^^

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
           self.wait(0.5)

The library is most useful when explaining:

* sorting and traversal steps,
* data structures in motion,
* algorithmic state updates and pointer movement,
* code-plus-visual narration during lectures.

See the `original README <https://github.com/sinianluoye/manim-algorithm/blob/main/README.md>`_
for more complete examples and API details.

.. toctree::
   :hidden:

   classes
   functions
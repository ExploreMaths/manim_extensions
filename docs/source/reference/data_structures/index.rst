Data structures
===============

**Original author:** `Hammad Nasir <https://github.com/drageelr>`_

**Source repository:** `GitHub <https://github.com/drageelr/manim-data-structures>`_

**License:** MIT (see the upstream repository for the full license text)

``manim-data-structures`` is a Manim toolkit for visualising common data
structures such as arrays, variables, and indices in algorithm explanations.

The code is bundled inside ``manim_extensions`` as the
``manim_extensions.data_structures`` subpackage.

Features
--------

- :class:`~manim_extensions.data_structures.m_array.MArray` – array-style container for indexed values.
- :class:`~manim_extensions.data_structures.m_variable.MVariable` – variable display for value updates.
- :class:`~manim_extensions.data_structures.m_array.MArrayElement` / :class:`~manim_extensions.data_structures.m_array.MArrayPointer` – element and pointer visual helpers.
- :class:`~manim_extensions.data_structures.m_array.MArraySlidingWindow` – windowed array layout for algorithms.
- directional helpers for array traversal and highlighting.

Quick start
-----------

.. code-block:: python

   from manim import *
   from manim_extensions.data_structures import MArray

   class ArrayExample(Scene):
       def construct(self):
           arr = MArray(self, [8, 7, 6, 5])
           self.add(arr)
           self.wait(0.5)

Displaying an array
^^^^^^^^^^^^^^^^^^^

.. manim:: DataStructureArrayExample
   :save_last_frame:

   from manim import *
   from manim_extensions.data_structures import MArray

   class DataStructureArrayExample(Scene):
       def construct(self):
           arr = MArray(self, [3, 1, 4, 1, 5, 9, 2, 6], label="arr")
           self.add(arr)

Attaching a pointer
^^^^^^^^^^^^^^^^^^^

.. manim:: DataStructurePointerExample
   :save_last_frame:

   from manim import *
   from manim_extensions.data_structures import MArray, MArrayPointer, MArrayDirection

   class DataStructurePointerExample(Scene):
       def construct(self):
           arr = MArray(self, [10, 20, 30, 40, 50], label="data")
           ptr = MArrayPointer(self, arr, index=2, label="i", pointer_pos=MArrayDirection.UP)
           self.add(arr, ptr)

Sliding window
^^^^^^^^^^^^^^

.. manim:: DataStructureSlidingWindowExample
   :save_last_frame:

   from manim import *
   from manim_extensions.data_structures import (
       MArray, MArraySlidingWindow, MArrayDirection
   )

   class DataStructureSlidingWindowExample(Scene):
       def construct(self):
           arr = MArray(self, [7, 2, 5, 1, 8, 3, 6, 4], label="nums")
           window = MArraySlidingWindow(
               self, arr, index=1, size=3, label="window",
               label_pos=MArrayDirection.UP
           )
           self.add(arr, window)

Updating a variable
^^^^^^^^^^^^^^^^^^^^

.. manim:: DataStructureVariableExample

   from manim import *
   from manim_extensions.data_structures import MVariable

   class DataStructureVariableExample(Scene):
       def construct(self):
           var = MVariable(self, value=0, index="x", label="count")
           var.to_edge(UP)
           self.play(Write(var))
           self.wait(0.5)
           var.update_value(5)
           self.wait(0.5)
           var.update_value(10)
           self.wait(0.5)
           var.update_label("total")
           self.wait(0.5)

Insert and remove elements
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. manim:: DataStructureInsertRemoveExample

   from manim import *
   from manim_extensions.data_structures import MArray

   class DataStructureInsertRemoveExample(Scene):
       def construct(self):
           arr = MArray(self, [1, 3, 5, 7], label="arr")
           self.play(Write(arr))
           self.wait(0.5)
           arr.append_elem(2)
           self.wait(0.5)
           arr.append_elem(4)
           self.wait(0.5)
           arr.remove_elem(index=1)
           self.wait(0.5)

This library is ideal for:

* sorting and searching walkthroughs,
* array and pointer tutorials,
* teaching data-structure state changes over time.

See the `official documentation <https://manim-data-structures.readthedocs.io/en/latest/>`_
for more detailed examples and the full API.

.. toctree::
   :hidden:

   classes
   enums
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

- ``MArray`` – array-style container for indexed values.
- ``MVariable`` – variable display for value updates.
- ``MArrayElement`` / ``MArrayPointer`` – element and pointer visual helpers.
- ``MArraySlidingWindow`` – windowed array layout for algorithms.
- directional helpers for array traversal and highlighting.

Quick start
-----------

.. code-block:: python

   from manim import *
   from manim_extensions.data_structures import MArray

   class ArrayExample(Scene):
       def construct(self):
           arr = MArray([8, 7, 6, 5])
           self.add(arr)
           self.wait(0.5)

A simple array scene
^^^^^^^^^^^^^^^^^^^^

.. manim:: DataStructureLibraryExample
   :save_last_frame:

   from manim import *
   from manim_extensions.data_structures import MArray

   class DataStructureLibraryExample(Scene):
       def construct(self):
           arr = MArray([8, 7, 6, 5])
           self.add(arr)
           self.wait(0.5)

This library is ideal for:

* sorting and searching walkthroughs,
* array and pointer tutorials,
* teaching data-structure state changes over time.

See the `official documentation <https://manim-data-structures.readthedocs.io/en/latest/>`_
for more detailed examples and the full API.

.. toctree::
   :hidden:

   api
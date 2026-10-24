.. SPDX-FileCopyrightText: 2022 Hammad Nasir
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Data structures
===============

.. vendored-status:: drageelr/manim-data-structures

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
- Per-element appearance (square / value / index styling), growth direction, array label placement, hex index display, index offset, and hidden indices.
- Element lifecycle animations: append, remove, value and index updates with configurable animation types.
- :class:`~manim_extensions.data_structures.m_enum.MArrayDirection` and :class:`~manim_extensions.data_structures.m_enum.MArrayElementComp` enums for directions and animation targets.

Usage
-----

All constructors take the current ``Scene`` as their first argument. Animations
triggered on an array play automatically through that scene; pass
``play_anim=False`` to receive the animation objects and play them yourself.

.. manim:: MainScene
   :ref_classes: MArray

   from manim import *

   from manim_extensions.data_structures import MArray

   class MainScene(Scene):
       def construct(self):
           # Create an array (the scene is the first argument)
           arr = MArray(self, [8, 7, 6, 5, 4], label="Arr")
           self.play(Create(arr))

           # Animate the whole array
           self.play(arr.animate.shift(UP * 2.5 + LEFT * 5))

           # Animate a single element
           self.play(arr.animate_elem(3).shift(DOWN * 0.5))

           # Animate the element square, value, and index individually
           self.play(
               arr.animate_elem_square(0).set_fill(BLACK),
               arr.animate_elem_value(0).rotate(PI / 2).set_fill(RED),
               arr.animate_elem_index(0).rotate(PI / 2),
           )

Configuring the array
^^^^^^^^^^^^^^^^^^^^^

Pass ``mob_square_args``, ``mob_value_args``, and ``mob_index_args`` to style
the element bodies, values, and indices:

.. code-block:: python

   arr = MArray(
       self,
       [1, 1, 2],
       mob_square_args={"color": GRAY_A, "fill_color": RED_E, "side_length": 0.5},
       mob_value_args={"color": GOLD_A, "font_size": 28},
       mob_index_args={"color": RED_E, "font_size": 22},
   )

Choose the growth direction with :class:`~manim_extensions.data_structures.m_enum.MArrayDirection`,
and position an array label with ``arr_label_pos`` / ``arr_label_gap`` (the gap
is the distance between the element squares and the label):

.. code-block:: python

   arr_up = MArray(self, [1, 2], arr_dir=MArrayDirection.UP)
   arr_right = MArray(self, [3, 4], arr_dir=MArrayDirection.RIGHT)

   arr = MArray(self, [1, 2, 3], label="Arr",
                arr_label_pos=MArrayDirection.DOWN, arr_label_gap=0.75)

Show indices as hexadecimal (e.g. for an address view), offset them, or hide
them entirely:

.. code-block:: python

   arr = MArray(self, [0, 2, 4, 6, 8], index_hex_display=True, index_offset=4)
   hidden = MArray(self, [1, 2, 3, 4], hide_index=True)

Element lifecycle
^^^^^^^^^^^^^^^^^

Append an element with :meth:`~manim_extensions.data_structures.m_array.MArray.append_elem`.
It accepts ``mob_square_args`` / ``mob_value_args`` / ``mob_index_args`` for the
new element, an ``append_anim`` animation type (and ``append_anim_args``), and
an ``append_anim_target`` chosen from :class:`~manim_extensions.data_structures.m_enum.MArrayElementComp`.
With ``play_anim=False`` it returns the list of animations to play yourself:

.. code-block:: python

   arr2 = MArray(self, [0, 2, 4, 6, 8], index_hex_display=True, index_offset=4)
   self.play(Write(arr2.append_elem(10)))
   self.play(Write(arr2.append_elem(12, mob_square_args={"fill_color": BLACK})))
   self.play(Write(arr2.update_elem_value(3, 0, mob_value_args={"color": RED})),
             arr2.animate_elem_square(3).set_fill(WHITE))

   arr.append_elem(4, append_anim=GrowFromCenter)
   self.play(*arr.append_elem(4, play_anim=False))

Remove an element with :meth:`~manim_extensions.data_structures.m_array.MArray.remove_elem`,
passing ``removal_anim`` and ``update_anim`` animation types. It returns a
removal animation plus an ``update_indices`` callable; play removal first, then
the index update:

.. code-block:: python

   arr.remove_elem(1)
   remove_anim, update_indices = arr.remove_elem(
       1, removal_anim=ShowPassingFlash, update_anim=Write, play_anim=False
   )
   self.play(remove_anim)
   self.play(*update_indices(play_anim=False))

Update an existing element's value or index with
:meth:`~manim_extensions.data_structures.m_array.MArray.update_elem_value` and
:meth:`~manim_extensions.data_structures.m_array.MArray.update_elem_index`:

.. code-block:: python

   arr.update_elem_value(1, 20)
   arr.update_elem_index(1, -2)

Variables
^^^^^^^^^

:class:`~manim_extensions.data_structures.m_variable.MVariable` displays a
single labeled value. Read it back with ``fetch_value`` / ``fetch_index`` and
mutate it with ``update_value`` / ``update_index``:

.. code-block:: python

   from manim_extensions.data_structures import MVariable

   var = MVariable(self, 10, 0, "Var")
   self.add(var)

   var.update_value(20)
   var.update_index("x")
   current = var.fetch_value()

Pointers
^^^^^^^^

Attach a :class:`~manim_extensions.data_structures.m_array.MArrayPointer` to an
array and move it between elements with ``shift_to_elem`` / ``attach_to_elem``:

.. code-block:: python

   from manim_extensions.data_structures import MArray, MArrayPointer

   arr = MArray(self, [1, 2, 3, 4, 5], label="Array")
   arr.shift(UP + LEFT * 2)
   self.add(arr)

   pointer = MArrayPointer(self, arr, 2, "P")
   self.play(Create(pointer))
   pointer.shift_to_elem(4)
   pointer.attach_to_elem(2)

Sliding windows
^^^^^^^^^^^^^^^

:class:`~manim_extensions.data_structures.m_array.MArraySlidingWindow` attaches
a window of a given width to an array; ``resize_window`` changes its size:

.. code-block:: python

   from manim_extensions.data_structures import MArray, MArraySlidingWindow

   arr = MArray(self, [1, 2, 3, 4, 5], label="Array")
   arr.shift(UP + LEFT * 2)
   self.add(arr)

   window = MArraySlidingWindow(self, arr, 1, 1, "W")
   self.play(Create(window))
   window.shift_to_elem(2)
   window.resize_window(3)
   window.attach_to_elem(2)

Example scenes
^^^^^^^^^^^^^^

Two-pointer technique for a pair sum in a sorted array:

.. code-block:: python

   from manim_extensions.data_structures import (
       MArray, MArrayPointer, MVariable,
   )

   class PairSumExample(Scene):
       def is_pair_sum(self, arr, n, val):
           p_i = MArrayPointer(self, arr, 0, "i",
                               mob_arrow_args={"color": GREEN},
                               mob_label_args={"color": GREEN})
           p_j = MArrayPointer(self, arr, n - 1, "j",
                               mob_arrow_args={"color": YELLOW},
                               mob_label_args={"color": YELLOW})
           pair_sum = MVariable(self, 0, label="Sum")
           pair_sum.shift(DOWN * 2)
           self.play(Create(pair_sum), Create(p_i), Create(p_j))
           while p_i.fetch_index() < p_j.fetch_index():
               pair_sum.update_value(
                   arr.fetch_arr()[p_i.fetch_index()]
                   + arr.fetch_arr()[p_j.fetch_index()]
               )
               if pair_sum.fetch_value() == val:
                   self.play(pair_sum.fetch_mob_square().animate.set(fill_color=GREEN))
                   return True
               elif pair_sum.fetch_value() < val:
                   p_i.shift_to_elem(p_i.fetch_index() + 1)
               else:
                   p_j.shift_to_elem(p_j.fetch_index() - 1)
           self.play(pair_sum.fetch_mob_square().animate.set(fill_color=RED))
           return False

       def construct(self):
           arr = MArray(self, [2, 3, 5, 8, 9, 10, 11], label="Array")
           arr.shift(UP + LEFT * 2)
           self.add(arr)
           self.is_pair_sum(arr, 7, 17)

Sliding-window technique for the maximum sum of ``k`` consecutive elements:

.. code-block:: python

   from manim_extensions.data_structures import (
       MArray, MArraySlidingWindow, MVariable,
   )

   class MaxKSumExample(Scene):
       def max_k_sum(self, arr, k):
           values = arr.fetch_arr()
           n = len(values)
           window = MArraySlidingWindow(self, arr, 0, k, "Window")
           window_sum = MVariable(self, sum(values[:k]), label="Window Sum")
           max_sum = MVariable(self, window_sum.fetch_value(), label="Max Sum")
           window_sum.shift(DOWN)
           max_sum.shift(DOWN * 2.5)
           self.play(Create(window), Create(window_sum), Create(max_sum))
           for i in range(n - k):
               window.shift_to_elem(i + 1)
               window_sum.update_value(
                   window_sum.fetch_value() - values[i] + values[i + k]
               )
               if window_sum.fetch_value() > max_sum.fetch_value():
                   max_sum.update_value(window_sum.fetch_value())
                   self.play(max_sum.fetch_mob_square().animate.set(fill_color=GREEN))
           return max_sum.fetch_value()

       def construct(self):
           arr = MArray(self, [1, 4, 2, 10, 2, 3, 1, 0, 20], label="Array")
           arr.shift(UP * 1.5 + LEFT * 4)
           self.add(arr)
           self.max_k_sum(arr, 4)

.. toctree::
   :hidden:
   :maxdepth: 1

   classes
   constants
   enums

See the `upstream documentation <https://manim-data-structures.readthedocs.io/en/latest/>`_,
the `animating-arrays guide <https://manim-data-structures.readthedocs.io/en/latest/guides/arrays.html>`_,
the `example gallery <https://manim-data-structures.readthedocs.io/en/latest/example.html>`_,
and the `changelog <https://github.com/drageelr/manim-data-structures/blob/main/CHANGELOG.md>`_
for more animated examples.

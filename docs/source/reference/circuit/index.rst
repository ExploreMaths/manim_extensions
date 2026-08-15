Circuit
=======

**Original author:** `Mr-FuzzyPenguin <https://github.com/Mr-FuzzyPenguin>`_

**Source repository:** `GitHub <https://github.com/Mr-FuzzyPenguin/manim-circuit>`_

**License:** MIT (see the upstream repository for the full license text)

``manim-circuit`` adds custom Manim mobjects for electrical components so that
basic circuit diagrams can be built and animated directly inside a scene.

The code is bundled inside ``manim_extensions`` as the
``manim_extensions.circuit`` subpackage.

Features
--------

- ``Resistor`` / ``Inductor`` / ``Capacitor`` components.
- ``VoltageSource`` and ``CurrentSource`` objects.
- terminal-based connection points for wiring diagrams.
- labeled component support and circuit assembly helpers.
- educational scene objects for engineering and electronics demos.

Quick start
-----------

.. code-block:: python

   from manim import *
   from manim_extensions.circuit.mobjects import Resistor, Capacitor

   class CircuitExample(Scene):
       def construct(self):
           r = Resistor().shift(LEFT)
           c = Capacitor().shift(RIGHT)
           self.add(r, c)
           self.wait(0.5)

A simple circuit scene
^^^^^^^^^^^^^^^^^^^^^^

.. manim:: CircuitLibraryExample
   :save_last_frame:

   from manim import *
   from manim_extensions.circuit.mobjects import Resistor, Capacitor

   class CircuitLibraryExample(Scene):
       def construct(self):
           r = Resistor().shift(LEFT)
           c = Capacitor().shift(RIGHT)
           self.add(r, c)
           self.wait(0.5)

This library is especially useful for:

* electrical engineering tutorials,
* circuit diagrams in lecture scenes,
* component-by-component introductions to circuitry.

See the `original repository <https://github.com/Mr-FuzzyPenguin/manim-circuit>`_
for more advanced wiring examples and circuit layouts.

.. toctree::
   :hidden:

   mobjects
   helpers
   functions
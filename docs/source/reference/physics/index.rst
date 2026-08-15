Physics
=======

**Original author:** `Matheart <https://github.com/Matheart>`_

**Source repository:** `GitHub <https://github.com/Matheart/manim-physics>`_

**License:** MIT (see the upstream repository for the full license text)

``manim-physics`` is a physics toolkit for Manim. It covers optics, waves,
rigid mechanics, and electromagnetism in a form that is convenient for lecture
and demonstration scenes.

The code is bundled inside ``manim_extensions`` as the
``manim_extensions.physics`` subpackage.

Features
--------

- ``Lens`` / ray helpers for geometrical optics.
- wave models such as linear, radial, and standing waves.
- pendulum and rigid-body mechanisms for mechanics scenes.
- electrostatics and magnetostatics helpers.
- scene-level physics objects designed for educational visualisation.

Quick start
-----------

.. code-block:: python

   from manim import *
   from manim_extensions.physics import Lens

   class PhysicsExample(Scene):
       def construct(self):
           lens = Lens(f=1.0, d=0.4)
           self.add(lens)
           self.wait(0.5)

A simple optics scene
^^^^^^^^^^^^^^^^^^^^^

.. manim:: PhysicsLibraryExample
   :save_last_frame:

   from manim import *
   from manim_extensions.physics import Lens

   class PhysicsLibraryExample(Scene):
       def construct(self):
           lens = Lens(f=1.0, d=0.4)
           self.add(lens)
           self.wait(0.5)

This library is useful for:

* optics demonstrations,
* wave propagation scenes,
* pendulum and motion examples,
* educational visual explanations in mechanics and E&M.

See the `original repository <https://github.com/Matheart/manim-physics>`_
for the full physics API and additional examples.

.. toctree::
   :hidden:

   electromagnetism
   optics
   mechanics
   waves
.. SPDX-FileCopyrightText: 2024 Matheart
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Physics
=======

.. vendored-status:: Matheart/manim-physics

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

- :class:`~manim_extensions.physics.optics.lenses.Lens` / ray helpers for geometrical optics.
- wave models such as linear, radial, and standing waves.
- pendulum and rigid-body mechanisms for mechanics scenes.
- electrostatics and magnetostatics helpers.
- scene-level physics objects designed for educational visualisation.

.. toctree::
   :maxdepth: 1

   electromagnetism
   optics
   mechanics
   waves

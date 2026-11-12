.. SPDX-FileCopyrightText: 2024 Matheart
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Physics
=======

.. module:: manim_extensions.physics

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

Usage
-----

Upstream distributed ``manim-physics`` on PyPI (and advised users not to clone
the development repository directly); here it is bundled inside
``manim_extensions.physics``. Import the modules, then construct and add the
mobjects like any other Manim object.

Optics
^^^^^^

:class:`~manim_extensions.physics.optics.lenses.Lens` takes a focal length
``f``, a diameter ``d`` and a refractive index ``n`` (default 1.52).
:class:`~manim_extensions.physics.optics.rays.Ray` takes a ``start`` point and a
``direction`` vector (plus an optional ``propagate`` list of lenses it passes
through):

.. manim:: LensScene
   :save_last_frame:
   :ref_classes: Lens Ray

   from manim import *
   from manim_extensions.physics.optics.lenses import Lens
   from manim_extensions.physics.optics.rays import Ray

   class LensScene(Scene):
       def construct(self):
           lens = Lens(-5, 1)
           ray = Ray(LEFT * 0.5, RIGHT, 1, [lens])
           self.add(lens, ray)

Waves
^^^^^

:class:`~manim_extensions.physics.wave.LinearWave`,
:class:`~manim_extensions.physics.wave.RadialWave` and
:class:`~manim_extensions.physics.wave.StandingWave` render 2D and 3D wave
surfaces. :class:`~manim_extensions.physics.wave.LinearWave` accepts
``wavelength``, ``period``, ``amplitude`` and ``x_range`` / ``y_range``;
:class:`~manim_extensions.physics.wave.StandingWave` accepts a mode number
``n``, a ``length``, a ``period`` and an ``amplitude``:

.. manim:: WaveScene
   :save_last_frame:
   :ref_classes: LinearWave StandingWave

   from manim import *
   from manim_extensions.physics.wave import LinearWave, StandingWave

   class WaveScene(Scene):
       def construct(self):
           self.add(LinearWave(wavelength=1, period=1, amplitude=0.2,
                               x_range=(-3.5, 3.5), y_range=(-2, 2)))
           self.add(StandingWave(n=2, length=4, period=1, amplitude=1).shift(UP * 1.2))

Rigid mechanics
^^^^^^^^^^^^^^^

A :class:`~manim_extensions.physics.rigid_mechanics.pendulum.Pendulum`
(``length``, ``initial_theta``, ``pivot_point``) or a
:class:`~manim_extensions.physics.rigid_mechanics.pendulum.MultiPendulum`
(one pivot followed by the bob positions) animates a hanging mechanism:

.. manim:: PendulumScene
   :save_last_frame:
   :ref_classes: Pendulum

   from manim import *
   from manim_extensions.physics.rigid_mechanics.pendulum import (
       Pendulum,
   )

   class PendulumScene(Scene):
       def construct(self):
           pendulum = Pendulum(length=3.5, initial_theta=0.3).scale(2)
           self.add(pendulum)

Electromagnetism
^^^^^^^^^^^^^^^^

Place a point
:class:`~manim_extensions.physics.electromagnetism.electrostatics.Charge`
(``magnitude``, ``point``) and visualise its field with
:class:`~manim_extensions.physics.electromagnetism.electrostatics.ElectricField`;
draw a current-carrying
:class:`~manim_extensions.physics.electromagnetism.magnetostatics.Wire`
(``stroke``, ``current``) and its
:class:`~manim_extensions.physics.electromagnetism.magnetostatics.MagneticField`:

.. manim:: ElectrostaticsScene
   :save_last_frame:
   :ref_classes: Charge ElectricField Wire MagneticField

   from manim import *
   from manim_extensions.physics.electromagnetism.electrostatics import (
       Charge,
       ElectricField,
   )
   from manim_extensions.physics.electromagnetism.magnetostatics import (
       Wire,
       MagneticField,
   )

   class ElectrostaticsScene(Scene):
       def construct(self):
           charge = Charge(magnitude=1, point=ORIGIN)
           self.add(charge, ElectricField(charge).scale(0.5))


Modules
-------

.. autosummary::
   :nosignatures:

   ~electromagnetism
   ~optics
   ~rigid_mechanics
   ~wave

.. toctree::
   :hidden:
   :maxdepth: 1

   electromagnetism/index
   optics/index
   rigid_mechanics/index
   wave

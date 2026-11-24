.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

future_classes
==============

.. module:: manim_extensions.chemistry.future_classes

Classes
-------

.. autosummary::
   :nosignatures:

   ~future_classes.BatterySchema
   ~future_classes.BatterySide
   ~future_classes.Electron
   ~future_classes.Element
   ~future_classes.ElementFrame
   ~future_classes.Hole
   ~future_classes.MOSFETTransistor
   ~future_classes.NPNTransistor

Usage
-----

These models are scaffold classes for upcoming circuit and chemistry work. Import the concrete class you need rather than relying on package-wide side effects.

.. code-block:: python

   from manim_extensions.chemistry.future_classes import (
       BatterySchema,
       Electron,
       Hole,
       MOSFETTransistor,
       NPNTransistor,
   )

Modules
-------

.. autosummary::
   :nosignatures:

   ~future_classes

.. toctree::
   :hidden:
   :maxdepth: 1

   future_classes

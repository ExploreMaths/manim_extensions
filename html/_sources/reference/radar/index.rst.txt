.. SPDX-FileCopyrightText: 2026 FTZ-OPUS
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Radar Charts
============

.. automodule:: manim_extensions.radar

.. vendored-status:: FTZ-OPUS/manim-radar

**Original author:** `FTZ-OPUS <https://github.com/FTZ-OPUS>`_

**Source repository:** `GitHub <https://github.com/FTZ-OPUS/manim-radar>`_

**License:** MIT (see the upstream repository for the full license text)

``manim-radar`` provides animated radar (spider) charts, comparison layouts,
reveal and morph animations, and a reusable radar reel.

The code is bundled inside ``manim_extensions`` as the
:mod:`~manim_extensions.radar` subpackage.

Features
--------

- :class:`~manim_extensions.radar.chart.RadarChart` with reveal and morph animations.
- :class:`~manim_extensions.radar.data.RadarData` snapshots and overflow-aware scaling.
- :class:`~manim_extensions.radar.overflow.OverflowRadarChart` and
  :class:`~manim_extensions.radar.poly.PolyRadarChart` variants.
- :class:`~manim_extensions.radar.reel.RadarReel` for sequenced comparisons.
- built-in themes, styles, rolling numbers, and camera rigs.

Usage
-----

Reveal a radar chart built from four axes:

.. manim:: RadarChartDemo
   :ref_classes: RadarChart

   from manim import *
   from manim_extensions.radar import RadarChart

   class RadarChartDemo(Scene):
       def construct(self):
           chart = RadarChart(
               axes=["Speed", "Power", "Range", "Comfort"],
               values=[8, 6, 7, 9],
               title="Demo",
           )
           self.play(chart.reveal())

Modules
----------

.. autosummary::
   :nosignatures:

   ~animations
   ~backdrop
   ~camera
   ~chart
   ~cli
   ~config
   ~data
   ~legacy
   ~numbers
   ~overflow
   ~poly
   ~reel
   ~theme
   ~utils

Type Aliases
------------

.. autoall:: manim_extensions.radar
   :recursive:
   :types: typealias

Constants
---------

.. autoall:: manim_extensions.radar
   :types: data

.. toctree::
   :hidden:
   :maxdepth: 1

   animations
   backdrop
   camera
   chart
   cli
   config
   data
   legacy
   numbers
   overflow
   poly
   reel
   theme
   utils

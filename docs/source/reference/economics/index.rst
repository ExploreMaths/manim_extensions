.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Economics
=========

**Original author:** `ddzhang04 <https://github.com/ddzhang04>`_

**Source repository:** `GitHub <https://github.com/ddzhang04/manim_ec>`_

**License:** MIT

``manim_ec`` provides ready-to-animate economic diagram classes for Manim,
including supply-demand, AD-AS, IS-LM, and Solow growth models.

The code is bundled inside ``manim_extensions`` as the
``manim_extensions.economics`` subpackage.

Features
--------

- :class:`~manim_extensions.economics.base.EconDiagram` – abstract base class
  for all economic diagrams.
- :class:`~manim_extensions.economics.supply_demand.SupplyDemandDiagram` –
  supply-and-demand cross diagram.
- :class:`~manim_extensions.economics.ad_as.ADASDiagram` – aggregate-demand /
  aggregate-supply diagram.
- :class:`~manim_extensions.economics.is_lm.ISLMDiagram` – IS-LM model diagram.
- :class:`~manim_extensions.economics.linked.LinkedISLM_ADAS` – linked IS-LM
  and AD-AS diagrams.
- :class:`~manim_extensions.economics.solow.SolowDiagram` – Solow growth
  model diagram.

Quick start
-----------

.. manim:: EconomicsExample
   :save_last_frame:

   from manim import *
   from manim_extensions.economics import SupplyDemandDiagram

   class EconomicsExample(Scene):
       def construct(self):
           diagram = SupplyDemandDiagram()
           self.add(diagram)

.. toctree::
   :hidden:

   classes

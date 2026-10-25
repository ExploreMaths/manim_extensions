.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Economics
=========

.. vendored-status:: ddzhang04/manim_ec

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
- Shock methods that return lists of animations (demand/supply shocks,
  monetary/fiscal policy) and annotation helpers (equilibrium dots, axis
  arrows, share braces, golden rule).

.. important::

   ``manim_ec`` requires Python 3.11+ and a working Manim Community Edition
   installation; it is bundled here inside ``manim_extensions``.

Usage
-----

Quick start: build a diagram, create it, then play the animation list
returned by a shock method one animation at a time.

.. manim:: ADASQuickStart
   :ref_classes: ADASDiagram

   from manim import Create, Scene

   from manim_extensions.economics import ADASDiagram

   class ADASQuickStart(Scene):
       def construct(self):
           diagram = ADASDiagram()
           self.play(Create(diagram))
           self.wait()

           for anim in diagram.positive_demand_shock(m=30, show_arrows=True):
               self.play(anim)
               self.wait(0.5)

Supply and demand
^^^^^^^^^^^^^^^^^

:class:`~manim_extensions.economics.supply_demand.SupplyDemandDiagram` draws
the basic supply-and-demand cross with the equilibrium marked. Pass custom
inverse demand/supply functions (``P(Q)``):

.. code-block:: python

   diagram = SupplyDemandDiagram(
       demand_func=lambda q: 8 - 0.5 * q,   # inverse demand P(Q)
       supply_func=lambda q: 2 + 0.5 * q,   # inverse supply P(Q)
       show_equilibrium=True,
   )

Shift a curve with :meth:`~manim_extensions.economics.base.EconDiagram.get_shift_animation`
and the new function:

.. code-block:: python

   diagram.get_shift_animation("demand", new_func, show_arrows=True)
   diagram.get_shift_animation("supply", new_func, show_arrows=True)

AD-AS
^^^^^

:class:`~manim_extensions.economics.ad_as.ADASDiagram` renders the AD-AS model
with demand/supply shocks and long-run adjustment. Aggregate demand is derived
from the quantity theory, ``P = MV/Y``. Short-run aggregate supply is flat by
default (Keynesian); pass ``sras_slope`` for the upward-sloping Mankiw
formulation ``P = Pe + slope * (Y - Y_bar)``:

.. code-block:: python

   diagram = ADASDiagram(
       m=20,              # money supply
       v=1,               # velocity
       sras_price=4,      # expected price level Pe
       sras_slope=None,   # None = flat, positive = upward-sloping
       lras_y=5,          # potential output Y_bar
       sras_only=False,   # hide LRAS
       lras_only=False,   # hide SRAS
   )

Shift the curves directly:

.. code-block:: python

   diagram.shift_ad(m=30, show_arrows=True)
   diagram.shift_sras(sras_price=6)
   diagram.shift_lras(new_y=7)

The shock methods shift AD or SRAS and optionally animate the long-run
adjustment back to potential output; they return a list of animations to play
in sequence:

.. code-block:: python

   diagram.positive_demand_shock(m=30, long_run=True, show_arrows=True)
   diagram.negative_demand_shock(m=12)
   diagram.adverse_supply_shock(sras_price=6)
   diagram.positive_supply_shock(sras_price=2)

With an upward-sloping SRAS, shifts move the expected price level Pe while the
slope is kept:

.. code-block:: python

   diagram = ADASDiagram(sras_slope=0.5)
   for anim in diagram.positive_demand_shock(m=30, show_arrows=True):
       self.play(anim)

IS-LM
^^^^^

:class:`~manim_extensions.economics.is_lm.ISLMDiagram` draws the IS-LM model
with fiscal and monetary policy shifts. The constructor takes the autonomous
spending ``a``, the investment sensitivity to the interest rate ``b``, the
real money supply ``ms``, and the income / interest sensitivities of money
demand ``k`` and ``h``:

.. code-block:: python

   diagram = ISLMDiagram(
       a=9.5,   # autonomous spending
       b=1.5,   # investment sensitivity to interest rate
       ms=2,    # real money supply
       k=1,     # income sensitivity of money demand
       h=1,     # interest sensitivity of money demand
   )

Shift the curves:

.. code-block:: python

   diagram.shift_is(a=13, show_arrows=True)
   diagram.shift_lm(ms=5, show_arrows=True)

Policy methods:

.. code-block:: python

   diagram.monetary_expansion(ms=5, show_arrows=True)
   diagram.monetary_contraction(ms=1)
   diagram.fiscal_expansion(a=13)
   diagram.fiscal_contraction(a=6)

Solow growth model
^^^^^^^^^^^^^^^^^^

:class:`~manim_extensions.economics.solow.SolowDiagram` renders the Solow
growth model, ``y = k^a``, savings ``s f(k)``, and break-even
``(d + n + g) k``:

.. code-block:: python

   diagram = SolowDiagram(
       s=0.3,       # savings rate
       alpha=0.5,   # capital share
       delta=0.1,   # depreciation
       n=0.05,      # population growth
       g=0.05,      # technology growth
       show_production=True,
   )

Shift the curves:

.. code-block:: python

   diagram.shift_savings(s=0.5, show_arrows=True)
   diagram.shift_breakeven(delta=0.15, n=0.08)

Shock methods:

.. code-block:: python

   diagram.increase_savings(s=0.5, show_arrows=True)
   diagram.decrease_savings(s=0.15)
   diagram.population_growth(n=0.1)
   diagram.increase_depreciation(delta=0.2)

Show consumption / investment share braces at the steady state or at a given
capital level:

.. code-block:: python

   diagram.show_shares()            # at steady state k*
   diagram.show_shares(k=3)         # at a specific k
   diagram.hide_shares()

Slide the braces along the curve to visualise how the shares change:

.. code-block:: python

   diagram.animate_shares_along(k_start=1, k_end=8, run_time=4)

Shares update automatically when you shift curves while they are visible. Mark
the golden-rule capital level where consumption is maximised:

.. code-block:: python

   diagram.show_golden_rule()
   diagram.hide_golden_rule()

Linked IS-LM and AD-AS
^^^^^^^^^^^^^^^^^^^^^^

:class:`~manim_extensions.economics.linked.LinkedISLM_ADAS` places an IS-LM
and an AD-AS diagram side by side so that they shift simultaneously:

.. code-block:: python

   linked = LinkedISLM_ADAS(
       numbered_eq=True,
       show_arrows=True,
       spacing=1.0,
   )

.. code-block:: python

   linked.monetary_expansion(ms=5, m=30)
   linked.monetary_contraction(ms=1, m=10)
   linked.fiscal_expansion(a=13, m=30)
   linked.fiscal_contraction(a=6, m=12)
   linked.adverse_supply_shock(sras_price=6)

Common options
^^^^^^^^^^^^^^

These options work across all diagram classes:

.. list-table::
   :header-rows: 1

   * - Parameter
     - Default
     - Description
   * - ``show_equilibrium``
     - ``True``
     - Mark the initial equilibrium with a dot and dashed lines.
   * - ``numbered_eq``
     - ``False``
     - Subscripted labels (P1, Y1 -> P2, Y2) that persist across shifts.
   * - ``show_arrows``
     - ``False``
     - Arrows on the axes showing the direction of the equilibrium change.
   * - ``x_range`` / ``y_range``
     - ``[0, 10, 1]``
     - Axis range as ``[min, max, step]``.
   * - ``x_length`` / ``y_length``
     - ``6`` / ``4``
     - Axis display size in Manim units.

Ready-to-run scenes live in the upstream ``examples/`` directory (AD-AS,
Solow shares, IS-LM monetary expansion, and a linked-diagram scene).

.. toctree::
   :hidden:
   :maxdepth: 1

   classes
   functions
   constants

See the `upstream README <https://github.com/ddzhang04/manim_ec>`_ for the
diagram walk-through and example scenes.

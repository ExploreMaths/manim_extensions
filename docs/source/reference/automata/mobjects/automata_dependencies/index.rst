.. SPDX-FileCopyrightText: 2022 Sean Nelson
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

automata_dependencies
=====================

.. automodule:: manim_extensions.automata.mobjects.automata_dependencies

Usage
-----

Low-level state, transition, and automaton records used by the automata mobjects. Build them directly when you need a custom transition graph.

.. code-block:: python

   from manim_extensions.automata.mobjects.automata_dependencies.automata import (
       FiniteStateAutomaton,
   )
   from manim_extensions.automata.mobjects.automata_dependencies.state import State
   from manim_extensions.automata.mobjects.automata_dependencies.transition import Transition

Modules
-------

.. autosummary::
   :nosignatures:

   ~automata
   ~state
   ~transition
   ~xml_parser

.. toctree::
   :hidden:
   :maxdepth: 1

   automata
   state
   transition
   xml_parser

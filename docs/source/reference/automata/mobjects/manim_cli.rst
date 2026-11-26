.. SPDX-FileCopyrightText: 2022 Sean Nelson
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

manim_cli
=========

.. automodule:: manim_extensions.automata.mobjects.manim_cli

:class:`~manim_extensions.automata.mobjects.manim_cli.ManimAutomataCLI` is an interactive helper embedded in the automata
constructors, not a standalone ``manim-*`` shell command. It is activated
by passing ``cli=True`` to a finite automaton and is used to choose a
single accepting path through a non-deterministic automaton. The chosen
path can then be exported and replayed without prompting again.

How it is activated
-------------------

Pass ``cli=True`` when constructing the automaton, then call
``play_string`` from a scene as usual. The constructor prints the banner
and asks which builder to use; the path questions appear while
``play_string`` reads the input:

.. code-block:: python

   from manim_extensions.automata import ManimNondeterministicFiniteAutomaton

   # inside Scene.construct
   machine = ManimNondeterministicFiniteAutomaton(cli=True)
   self.add(machine)
   for step in machine.play_string("01"):
       self.play(*step, run_time=0.5)
   self.wait()

The first menu is deliberately short because the finite-automaton
constructors currently expose one builder:

.. code-block:: text

   0: Non-deterministic Automaton Path Builder
   Choice: 0

Choosing ``0`` sets ``machine.nda_builder = True``. From that point on,
whenever the automaton has more than one outgoing transition for the
current token, the CLI prints the possible next states and asks for one:

.. code-block:: text

   0: q0 --> q1
   Choice: 0

The number is the zero-based index of the transition shown by
``generate_next_state_options``. Selecting it restricts the run to that
branch, so the animation follows one path instead of showing every
non-deterministic branch at once.

Using the CLI in a scene
------------------------

A complete scene follows the same pattern as the non-interactive
automaton examples; the only difference is the ``cli=True`` flag and the
terminal prompts during ``play_string``:

.. code-block:: python

   from manim import *
   from manim_extensions.automata import ManimNondeterministicFiniteAutomaton

   class GuidedAutomatonPath(Scene):
       def construct(self):
           machine = ManimNondeterministicFiniteAutomaton(cli=True)
           self.add(machine)

           for step in machine.play_string("01"):
               self.play(*step, run_time=0.5)
           self.wait()

The prompts are read from standard input, so the scene must be rendered
from an interactive terminal. Rendering through a non-interactive
subprocess without piped choices will block at the first ``Choice:``
prompt.

The default non-deterministic template used by
:class:`~manim_extensions.automata.mobjects.manim_non_deterministic_finite_state_automaton.ManimNondeterministicFiniteAutomaton` already contains an epsilon
transition and several competing branches, which makes it a useful
starting point for trying the path builder. Pass ``json_template`` or
``xml_file`` to load a different automaton.

Recording and replaying a path
------------------------------

When ``nda_builder`` is active, each chosen transition is appended to
``machine.recorded_path`` as a ``(from_state, to_state)`` pair. At the end
of ``run_input_through_automaton`` the path is written to
``recorded_path.txt`` as JSON:

.. code-block:: text

   [["q0", "q1"], ["q1", "q2"]]

The relevant methods are:

.. list-table::
   :header-rows: 1
   :widths: 42 58

   * - Method
     - Purpose
   * - ``export_recorded_path_to_file()``
     - Write ``recorded_path`` to ``recorded_path.txt``.
   * - ``load_recorded_path_from_file(file_name)``
     - Load a JSON path list, or return ``None`` for invalid content.
   * - ``run_input_through_automaton(input, path_file)``
     - Replay a recorded path instead of prompting for choices.
   * - ``play_string(input)``
     - Build the input mobject, run the automaton, and return animations.

The two-step replay form is useful when the same path should be animated
again without a terminal:

.. code-block:: python

   automaton_input = machine.construct_automaton_input("01")
   history = machine.run_input_through_automaton(
       automaton_input, "recorded_path.txt"
   )

``run_input_through_automaton`` returns the run history; use
``generate_history_animations(history)`` if the history needs to be
converted into Manim animations manually.

Menu helpers
------------

The class exposes the prompt helpers separately so custom launchers can
reuse them without duplicating the input handling:

.. list-table::
   :header-rows: 1
   :widths: 44 56

   * - Helper
     - Behaviour
   * - ``display_options(options)``
     - Print numbered strings and return the chosen index.
   * - ``display_dictionary_options(options)``
     - Print one entry per mapping key and return the chosen key.
   * - ``display_nda_options()``
     - Show the single NDA path-builder choice and store it in
       ``nda_option``.
   * - ``creation_menu()``
     - Ask for an automaton type and a schema file path; intended for custom
       launchers, not called by the built-in finite-automaton constructors.

``display_options`` and ``display_dictionary_options`` both read a single
integer with ``input()``. They do not validate the range; an out-of-range
choice raises ``IndexError`` or ``KeyError`` when the caller indexes the
result.

API reference
-------------

Classes
~~~~~~~

.. autosummary::
   :nosignatures:

   ~ManimAutomataCLI

Constants
~~~~~~~~~

.. autoall:: manim_extensions.automata.mobjects.manim_cli
   :types: data

.. toctree::
   :hidden:
   :maxdepth: 1

   manim_cli.ManimAutomataCLI

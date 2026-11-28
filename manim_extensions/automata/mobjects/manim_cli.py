# SPDX-FileCopyrightText: 2022 Sean Nelson
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
# patched: document module-level constants

"""CLI utilities for automata.

This module provides the :class:`~manim_extensions.automata.mobjects.manim_cli.ManimAutomataCLI` class for interactive command-line interface.
"""

from typing import Any

#: ASCII-art banner printed by the interactive CLI.
cli_logo = r"""
  __  __          _   _ _____ __  __           _    _ _______ ____  __  __       _______          _____ _      _____
 |  \/  |   /\   | \ | |_   _|  \/  |     /\  | |  | |__   __/ __ \|  \/  |   /\|__   __|/\      / ____| |    |_   _|
 | \  / |  /  \  |  \| | | | | \  / |    /  \ | |  | |  | | | |  | | \  / |  /  \  | |  /  \    | |    | |      | |
 | |\/| | / /\ \ | . ` | | | | |\/| |   / /\ \| |  | |  | | | |  | | |\/| | / /\ \ | | / /\ \   | |    | |      | |
 | |  | |/ ____ \| |\  |_| |_| |  | |  / ____ \ |__| |  | | | |__| | |  | |/ ____ \| |/ ____ \  | |____| |____ _| |_
 |_|  |_/_/    \_\_| \_|_____|_|  |_| /_/    \_\____/   |_|  \____/|_|  |_/_/    \_\_/_/    \_\  \_____|______|_____|

"""


class ManimAutomataCLI:
    """Interactive command-line assistant for building automata paths.

    When activated via the ``cli=True`` flag on an automaton constructor,
    this class prints a banner and guides the user through the creation of
    a deterministic or non-deterministic finite automaton, or a pushdown
    automaton.  The recorded path can later be replayed without the CLI.

    Examples
    --------
    .. manim:: ManimAutomataCLIOverview
       :save_last_frame:

       from manim import *
       from manim_extensions.automata.mobjects.manim_cli import ManimAutomataCLI

       ManimAutomataCLITarget = ManimAutomataCLI

       class ManimAutomataCLIOverview(Scene):
           def construct(self):
               public = [n for n in dir(ManimAutomataCLITarget) if not n.startswith("_")]
               card = VGroup(
                   Text('ManimAutomataCLI', font_size=36),
                   Text('module: manim_extensions.automata.mobjects.manim_cli', font_size=18, color=GREY),
                   Text('Interactive command-line assistant for building automata paths', font_size=22),
                   Text("API: " + ", ".join(public[:6]), font_size=18, color=BLUE),
               ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
               card.scale_to_fit_width(11.5).move_to(ORIGIN)
               frame = RoundedRectangle(
                   width=12.1, height=card.height + 0.5, corner_radius=0.2, color=BLUE_D
               ).move_to(card)
               self.add(frame, card)

    The CLI is activated through the ``cli`` flag of an automaton
    constructor; it prints a banner and interactively records an accepting
    path through a non-deterministic automaton:

    .. code-block:: python

       from manim_extensions.automata import ManimNondeterministicFiniteAutomaton

       nda = ManimNondeterministicFiniteAutomaton(cli=True)
       # terminal menu:
       # 0: Non-deterministic Automaton Path Builder
       # Choice: 0
    """

    def __init__(self) -> None:
        print(cli_logo)

    def creation_menu(self) -> None:
        """Prompt the user to choose an automaton type and schema file path."""
        options = [
            "Deterministic Finite Automaton",
            "Non-deterministic Finite Automaton",
            "Pushdown Automaton",
        ]
        self.creation_option = self.display_options(options)
        self.file_path = input("Schema File Path: ")

    def display_nda_options(self) -> None:
        """Prompt the user to choose an NDA-specific option."""
        options = ["Non-deterministic Automaton Path Builder"]
        self.nda_option = self.display_options(options)

    def display_options(self, options: list[str]) -> int:
        """Print a list of options and return the user's choice.

        Parameters
        ----------
        options
            The options to display.

        Returns
        -------
            The user's zero-based choice index.
        """
        for index, option in enumerate(options):
            print(str(index) + ": " + option)

        return int(input("Choice: "))

    def display_dictionary_options(self, options: dict[Any, Any]) -> int:
        """Print dictionary keys with their first value column and return the user's choice.

        Parameters
        ----------
        options
            Mapping from option keys to tuples whose first element is shown.

        Returns
        -------
            The user's chosen key.
        """
        for index in options:
            print(f"{index}: {options[index][0]}")

        return int(input("Choice: "))


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    cli = ManimAutomataCLI()

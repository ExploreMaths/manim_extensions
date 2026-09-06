# SPDX-FileCopyrightText: 2022 Sean Nelson
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Non-deterministic finite state automaton visualization.

This module provides the ManimNonDeterministicFiniteAutomaton class for visualizing NFAs.

"""

from manim import *  # noqa: F401

from .manim_automaton import ManimAutomaton

nfa_automaton_json = {
    "structure": {
        "type": "nfa",
        "automaton": {
            "state": [
                {"@id": "0", "@name": "q0", "x": "84.0", "y": "122.0", "initial": None},
                {"@id": "1", "@name": "q1", "x": "218.0", "y": "175.0"},
                {"@id": "2", "@name": "q2", "x": "386.0", "y": "131.0", "final": None},
                {"@id": "3", "@name": "q3", "x": "227.0", "y": "36.0"},
            ],
            "transition": [
                {"from": "0", "to": "1", "read": "0"},
                {"from": "0", "to": "1", "read": "1"},
                {"from": "0", "to": "2", "read": None},
                {"from": "2", "to": "3", "read": "0"},
                {"from": "1", "to": "2", "read": "1"},
                {"from": "3", "to": "0", "read": "1"},
                {"from": "3", "to": "0", "read": "0"},
            ],
        },
    }
}


class ManimNondeterministicFiniteAutomaton(ManimAutomaton):
    """A non-deterministic finite automaton (NFA) with Manim visualisation.

    This subclass of :class:`~manim_extensions.automata.mobjects.manim_automaton.ManimAutomaton` represents an NFA where states
    may have multiple outgoing transitions for the same input symbol, including
    epsilon (``\\epsilon``) transitions.  It supports the CLI path-builder for
    interactively exploring accepting paths through the automaton.

    Parameters
    ----------
    json_template : dict, optional
        JSON dictionary describing the automaton states and transitions.
    xml_file : str, optional
        Path to an XML file (e.g. JFLAP format) describing the automaton.
    camera_follow : bool, optional
        If ``True``, the camera follows the active state during playback.
    animation_style : dict, optional
        Style configuration for state and transition animations.
    cli : bool, optional
        If ``True``, launch the interactive CLI for building NDA paths.
    **kwargs
        Key words arguments forwarded to :class:`~manim.mobject.types.vectorized_mobject.VGroup`.

    Examples
    --------
    .. manim:: ManimNondeterministicFiniteAutomatonExample

       from manim import *
       from manim_extensions.automata.mobjects.manim_non_deterministic_finite_state_automaton import ManimNondeterministicFiniteAutomaton

       class ManimNondeterministicFiniteAutomatonExample(MovingCameraScene):
           def construct(self):
               # build the NFA from the default JSON template (contains an
               # epsilon transition and multiple branches per symbol)
               nda = ManimNondeterministicFiniteAutomaton(animate_subscripts=False)

               # Adjust camera frame to fit the automaton in the scene
               self.camera.frame_width = nda.width + 4
               self.camera.frame_height = nda.height + 4
               self.camera.frame.move_to(nda)

               # Create an mobject version of the input for the automaton
               automaton_input = nda.construct_automaton_input("01")
               automaton_input.next_to(nda, UP, buff=0.5)

               self.play(
                   DrawBorderThenFill(nda),
                   FadeIn(automaton_input),
               )

               # Play all the animations generated from play_string()
               for sequence in nda.play_string(automaton_input):
                   self.play(*sequence, run_time=0.5)
    """

    nda_builder = False

    def __init__(
        self,
        json_template: dict[str, object] | None = None,
        xml_file: str | None = None,
        camera_follow: bool = False,
        animation_style: dict[str, object] | None = None,
        cli: bool = False,
        **kwargs: object,
    ) -> None:
        """Initialize the ManimNondeterministicFiniteAutomaton instance."""
        if json_template is None and xml_file is None:
            json_template = nfa_automaton_json
        if animation_style is None:
            super().__init__(json_template, xml_file, camera_follow, cli=cli, **kwargs)
        else:
            super().__init__(
                json_template,
                xml_file,
                camera_follow,
                animation_style,
                cli=cli,
                **kwargs,
            )

        if cli:  # if cli exist display options to user
            self.cli.display_nda_options()
            if (
                self.cli.nda_option == 0
            ):  # check the settings of the cli (what the user wants to do)
                self.nda_builder = True
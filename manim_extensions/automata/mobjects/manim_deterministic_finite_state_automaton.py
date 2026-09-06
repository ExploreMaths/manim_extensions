# SPDX-FileCopyrightText: 2022 Sean Nelson
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Deterministic finite state automaton visualization.

This module provides the ManimdeterministicFiniteAutomaton class for visualizing DFAs.

"""

from manim import *  # noqa: F401

from .manim_automaton import ManimAutomaton


class ManimdeterministicFiniteAutomaton(ManimAutomaton):
    """A deterministic finite automaton (DFA) with Manim visualisation.

    This subclass of :class:`~manim_extensions.automata.mobjects.manim_automaton.ManimAutomaton` represents a DFA where each
    state has exactly one outgoing transition for every input symbol.  It
    can be constructed from a JSON template or an XML file (JFLAP format).

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
    .. manim:: ManimdeterministicFiniteAutomatonExample

       from manim import *
       from manim_extensions.automata.mobjects.manim_deterministic_finite_state_automaton import ManimdeterministicFiniteAutomaton

       class ManimdeterministicFiniteAutomatonExample(MovingCameraScene):
           def construct(self):
               # build the DFA from the default JSON template
               dfa = ManimdeterministicFiniteAutomaton(animate_subscripts=False)

               # Adjust camera frame to fit the automaton in the scene
               self.camera.frame_width = dfa.width + 4
               self.camera.frame_height = dfa.height + 4
               self.camera.frame.move_to(dfa)

               # Create an mobject version of the input for the automaton
               automaton_input = dfa.construct_automaton_input("11")
               automaton_input.next_to(dfa, UP, buff=0.5)

               self.play(
                   DrawBorderThenFill(dfa),
                   FadeIn(automaton_input),
               )

               # Play all the animations generated from play_string()
               for sequence in dfa.play_string(automaton_input):
                   self.play(*sequence, run_time=0.5)
    """

    def __init__(
        self,
        json_template: dict[str, object] | None = None,
        xml_file: str | None = None,
        camera_follow: bool = False,
        animation_style: dict[str, object] | None = None,
        cli: bool = False,
        **kwargs: object,
    ) -> None:
        """Initialize the ManimdeterministicFiniteAutomaton instance."""
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
# SPDX-FileCopyrightText: 2022 Sean Nelson
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


"""Contains classes for Manim automaton."""

from __future__ import annotations

from manim import (
    BLUE,
    FadeToColor,
    GREEN,
    MathTex,
    PURE_YELLOW,
    RED,
    Tex,
    Transform,
    VGroup,
)
from .automata_dependencies.automata import FiniteStateAutomaton, automaton_json
from .manim_state import ManimState, State
from .manim_automaton_input import ManimAutomataInput
from .manim_transition import ManimTransition
from .manim_animations import ManimAnimations

from .manim_cli import ManimAutomataCLI

from typing import Optional, Union

import abc

import json

__all__ = ["ManimAutomaton"]

default_animation_style = {
    "animate_transition": {
        "animation_function": FadeToColor,
        "accept_color": PURE_YELLOW,
        "reject_color": RED,
        "run_time": 0.5,
        "time_width": 2,
    },
    "highlight_state": {"color": PURE_YELLOW},
    "token_highlight": {"animation_function": FadeToColor, "color": PURE_YELLOW},
}


class ManimAutomaton(FiniteStateAutomaton, VGroup, abc.ABC):
    """Graphical finite-state automaton for animating state transitions.

    The automaton combines a formal automaton model with a Manim visual graph,
    allowing states and transitions to be highlighted as an input string is read.

    .. note::

        This is an abstract base class.  Use one of the concrete subclasses
        :class:`~manim_extensions.automata.mobjects.manim_deterministic_finite_state_automaton.ManimdeterministicFiniteAutomaton`,
        :class:`~manim_extensions.automata.mobjects.manim_non_deterministic_finite_state_automaton.ManimNondeterministicFiniteAutomaton`, or
        :class:`~manim_extensions.automata.mobjects.manim_pushdown_automaton.ManimPushDownAutomaton` instead.

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
    manim_animations : ManimAnimations, optional
        Custom animation strategy.  Defaults to :class:`~manim_extensions.automata.mobjects.manim_animations.ManimAnimations`.
    cli : bool, optional
        If ``True``, launch the interactive CLI for building NDA paths.
    animate_subscripts : bool, optional
        If ``True`` (default), animate state subscripts to show
        the number of branches ending in each state.
    **kwargs
        Key words arguments forwarded to :class:`~manim.mobject.types.vectorized_mobject.VGroup`.

    Attributes
    ----------

    automaton : FiniteStateAutomaton
        The underlying formal automaton model.
    initial_state : State
        The start state of the automaton.
    manim_states : list[ManimState]
        Visual state mobjects.
    manim_transitions : list[ManimTransition]
        Visual transition arrow mobjects.

    Examples
    --------
    .. manim:: ManimAutomatonDocExample

       from manim import *
       from manim_extensions.automata.mobjects.manim_animations import (
           ManimAnimations,
       )
       from manim_extensions.automata.mobjects.manim_deterministic_finite_state_automaton import (
           ManimdeterministicFiniteAutomaton,
       )

       class ManimAutomatonDocExample(Scene):
           def construct(self):
               dfa = ManimdeterministicFiniteAutomaton()
               self.add(dfa)
               dfa.manim_automata_input = dfa.construct_automaton_input("11")
               dfa.set_default_position_of_input_string()
               self.play(FadeIn(dfa.manim_automata_input))
               animations = ManimAnimations()
               q0 = dfa.get_initial_state()
               q2 = dfa.get_state("q2")
               self.play(animations.animate_highlight_state(q0))
               self.play(animations.animate_highlight_state(q2))
               result = "ACCEPTED" if dfa.check_automaton_result([q2]) else "REJECTED"
               verdict = Text(
                   result, color=GREEN if result == "ACCEPTED" else RED
               ).next_to(dfa.manim_automata_input, UP)
               self.play(FadeIn(verdict))
    """

    def __init__(
        self,
        json_template: dict[str, object] | None = None,
        xml_file: str | None = None,
        camera_follow: bool = False,
        animation_style: dict[str, object] = default_animation_style,
        manim_animations: object | None = None,
        cli: bool = False,
        animate_subscripts: bool = True,
        **kwargs: object,
    ) -> None:
        """Initialize the automaton with JSON/XML templates, animation style, and optional CLI mode."""
        if json_template is None and xml_file is None:
            json_template = automaton_json

        FiniteStateAutomaton.__init__(self)

        self.animation_style = animation_style
        self.camera_follow = camera_follow

        if manim_animations is None:
            self.manim_animations = ManimAnimations()
        else:
            self.manim_animations = manim_animations

        self.cli = None
        if cli:
            self.cli = ManimAutomataCLI()
            self.nda_builder = True
        else:
            self.nda_builder = False

        self._animate_subscripts = animate_subscripts

        VGroup.__init__(self, **kwargs)

        if json_template:
            self.construct_from_json(json_template)
        elif xml_file:
            self.process_xml(xml_file)

        self.add(*self.states)
        self.add(*self.transitions)

        if self.states:
            self.center()

    def add_manim_state(self, manim_state: ManimState) -> None:
        """Add an existing ManimState mobject to the automaton's VGroup.

        Parameters
        ----------
        manim_state : ManimState
            The state mobject to add.
        """
        # maybe need validation
        # adds an already existing manim_state to automaton
        self.add(manim_state)

    def construct_state(self, state: dict[str, object], scaling: float = 10) -> None:
        """Create a ManimState from a state dict and append it to self.states.

        Parameters
        ----------
        state : dict
            State definition with ``"@name"``, ``"x"``, ``"y"``, ``"@id"``
            and optional ``"initial"``/``"final"`` flags.
        scaling : float, optional
            Coordinate scaling factor. Defaults to ``10``.
        """
        initial = False
        final = False
        if "initial" in state.keys():
            initial = True
            for state_object in self.states:
                if state_object.initial == True:
                    initial = False

        if "final" in state.keys():
            final = True

        new_x = float(state["x"]) - self.origin_offset_x
        new_y = float(state["y"]) - self.origin_offset_y
        self.states.append(
            ManimState(
                state["@name"],
                new_x,
                new_y,
                animation_style=self.animation_style,
                initial=initial,
                final=final,
                id=state["@id"],
                scaling=scaling,
            )
        )

    def construct_states(self, states: list[dict[str, object]]) -> None:
        """Build all ManimState objects from a list of state dicts with auto-scaling.

        Parameters
        ----------
        states : list of dict
            State definitions from JSON or XML parsing.
        """
        for state in states:
            if "initial" in state.keys():
                self.origin_offset_x = float(state["x"])
                self.origin_offset_y = float(state["y"])
                break

        coords = []
        for state in states:
            x = float(state["x"]) - self.origin_offset_x
            y = float(state["y"]) - self.origin_offset_y
            coords.append((x, y))

        auto_scaling = 10.0
        if coords:
            xs = [c[0] for c in coords]
            ys = [c[1] for c in coords]
            width = max(xs) - min(xs)
            height = max(ys) - min(ys)
            if width > 0 or height > 0:
                target_width = 7.0
                target_height = 4.0
                scale_x = width / target_width if width > 0 else 1.0
                scale_y = height / target_height if height > 0 else 1.0
                auto_scaling = max(scale_x, scale_y, 1.0)

        for state in states:
            self.construct_state(state, scaling=auto_scaling)

        if auto_scaling > 10.0:
            size_factor = 10.0 / auto_scaling
            for state_obj in self.states:
                state_obj.scale(size_factor)

    def construct_transitions(self, transitions: list[dict[str, object]]) -> None:
        """Build ManimTransition objects from transition dicts, grouping read symbols by state pair.

        Parameters
        ----------
        transitions : list of dict
            Transition definitions from JSON or XML parsing.
        """
        # counts the number of transitions between two states
        transition_counter: dict[tuple[str, str], list[object]] = {}
        for transition in transitions:
            """put from and to states into tuple to be used as
            dictionary key."""
            state_key = (transition["from"], transition["to"])

            transition_group = transition_counter.setdefault(
                state_key, []
            )  # if key doesn't exist then create new key list pair
            # if symbol already exists then skip
            if transition["read"] not in transition_group:
                if transition["read"] == None:
                    transition["read"] = r"\epsilon"
                transition_group.append(
                    transition["read"]
                )  # append transition read value to transition[state_key]

        # avoids creating multiple manim_transitions.
        # Creates one manim_transition with multiple read values
        for state_key in transition_counter:
            read_values = transition_counter[state_key]

            transition_from = self.get_state_by_id(int(state_key[0]))
            transition_to = self.get_state_by_id(
                int(state_key[1])
            )  # this is using the id from xml which will be different, can't use name either - has to be passed in

            self.construct_transition(transition_from, transition_to, read_values)

    def construct_transition(
        self,
        transition_from: ManimState,
        transition_to: ManimState,
        read_symbols: list[str],
    ) -> None:
        """Create a single ManimTransition between two states and register it.

        Parameters
        ----------
        transition_from : ManimState
            The source state of the transition.
        transition_to : ManimState
            The destination state of the transition.
        read_symbols : list of str
            The symbols that trigger this transition.
        """
        new_transition = ManimTransition(
            transition_from,
            transition_to,
            read_symbols,
            parent_automaton=self,
            animation_style=self.animation_style,
        )
        self.transitions.append(new_transition)
        # add the transition to the from_states link list
        transition_from.add_transition_to_state(new_transition)

    def construct_automaton_input(self, input_string: str) -> "ManimAutomataInput":
        """Create a ManimAutomataInput mobject from an input string.

        Parameters
        ----------
        input_string : str
            The input string to display and run through the automaton.

        Returns
        -------
        ManimAutomataInput
            The constructed input mobject.
        """
        return ManimAutomataInput(input_string, animation_style=self.animation_style)

    def set_default_position_of_input_string(self) -> None:
        """Position the input string mobject centered above the automaton."""
        # get centre of self
        c1 = self.get_x()
        c2 = self.get_y()
        # set position of manim_automata_input relative to self
        self.manim_automata_input.set_x(c1)
        self.manim_automata_input.set_y(c2 + self.height / 4)

    def check_automaton_result(self, state_pointers: list[State]) -> bool:
        """Return True if any state in state_pointers is a final (accepting) state.

        Parameters
        ----------
        state_pointers : list of State
            The currently active states.

        Returns
        -------
        bool
            ``True`` if any active state is a final state, otherwise ``False``.
        """
        for state in state_pointers:
            if state.final == True:
                return True
        return False

    def determine_input(
        self, input: str | "ManimAutomataInput"
    ) -> "ManimAutomataInput | None":
        """Checks to if input is a string or already an manim mobject,
        if it is type string then create manim_input instance using
        the input string.

        Parameters
        ----------
        input : str or ManimAutomataInput
            The input string, or an already constructed input mobject.

        Returns
        -------
        ManimAutomataInput or None
            The input mobject if it was already constructed, otherwise ``None``.
        """
        if type(input) is str:
            # create mobject of input string
            self.manim_automata_input = self.construct_automaton_input(input)
            # position the mobject
            self.set_default_position_of_input_string()
        else:
            return input  # if input is already an instance of ManimAutomataInput

    def run_sequence(
        self,
        token: str | MathTex,
        state_pointers: list[State],
        iteration_history: list[dict[str, object]],
        predetermined_transition: "ManimTransition | None" = None,
    ) -> tuple[list[State], bool]:
        """Process one input token across all active state pointers and record the step history.

        Parameters
        ----------
        token : str or MathTex
            The input token to process.
        state_pointers : list of State
            The currently active states.
        iteration_history : list of dict
            The per-step history to append this iteration's result to.
        predetermined_transition : ManimTransition or None, optional
            Unused; kept for interface compatibility. Defaults to ``None``.

        Returns
        -------
        tuple
            ``(next_states, sequence_result)`` with the reachable next states
            and whether any active state accepted the token.
        """
        next_states: list[State] = []
        for (
            state_pointer
        ) in (
            state_pointers
        ):  # look at each state and calculate the steps that state can take.
            step_result, next_neighbour_states, transitions = self.automaton_step(
                token, state_pointer
            )  # simulates the machine

            iteration_history.append(
                {
                    "state_pointer": state_pointer,
                    "next_neighbour_states": next_neighbour_states,
                    "transitions": transitions,
                    "result": step_result,
                    "token": token,
                }
            )

            if self.nda_builder:
                path_options = self.generate_next_state_options(
                    state_pointer, transitions
                )
                user_choice = self.cli.display_dictionary_options(path_options)
                transition = path_options[user_choice][
                    1
                ]  # get transition given user choice

                # record the transition choice
                self.recorded_path.append(
                    (transition.transition_from.name, transition.transition_to.name)
                )

                transition_ids = [
                    transition.id
                ]  # There is now only one transition that the state_pointer can take
                next_neighbour_states = [transition.transition_to]

            if step_result is True:
                if len(next_neighbour_states) > 0:
                    next_states = next_states + next_neighbour_states

        # if all state_pointers steps fail then automaton failed
        sequence_result = False
        for iteration in iteration_history:
            if iteration["result"] == True:
                sequence_result = True
                break

        return next_states, sequence_result

    def run_input_through_automaton(
        self, input: Union[str, "ManimAutomataInput"], automaton_path_name: Optional[str] = None
    ) -> list:
        """Run the input through the automaton and return the run history.

        Parameters
        ----------
        input : str or ManimAutomataInput
            The input string, or an already constructed input mobject.
        automaton_path_name : str, optional
            Path to a recorded path file that provides a single path used to
            navigate through the NDA; the purpose of this is to allow the user
            to animate a single path through the NDA instead of animating all
            of the branches that are created by the NDA. Defaults to ``None``.

        Returns
        -------
        list
            The history of the run, including the final ``"information"``
            entry with the active states and the automaton result.
        """

        # example_structure = [("q0", "q1")]
        # if this transition does not exist or the token does not match
        # then return error with the number of the tuple in the list
        if (
            automaton_path_name
        ):  # The nda will animate the predetermined path from the user
            automaton_path = self.load_recorded_path_from_file(automaton_path_name)
            return self.play_automaton_path(
                input, automaton_path
            )  # create animations to do with given path
        elif self.nda_builder:  # Stores the path of of a single branch within the nda
            self.recorded_path = []

        # keeps track of what happend throughout each iteration
        global_history = {}

        initial_state = self.get_initial_state()
        state_pointers = [
            initial_state
        ]  # Keeps track of all the states that are activated

        # Animate the automaton going through the sequence
        for i, token in enumerate(input.tokens):
            iteration_history = []

            state_pointers, sequence_result = self.run_sequence(
                token, state_pointers, iteration_history
            )  # goes through each state_pointer

            global_history[token.id] = {
                "token": token,
                "iteration_history": iteration_history,
            }

            # if the input token failed then cancel input loop early
            if sequence_result == False:
                break

        # export the recorded path so the user can use it again without using nda builder
        if self.nda_builder:
            self.export_recorded_path_to_file()

        # add information about whether the input was accepted
        global_history["information"] = {
            "state_pointers": state_pointers,
            "automaton_result": self.check_automaton_result(state_pointers),
        }

        return global_history

    def generate_next_state_options(
        self,
        state_pointer: State,
        transitions: list[ManimTransition],
    ) -> dict[int, tuple[str, ManimTransition]]:
        """Build a dict of possible transitions from a state for the CLI NDA builder.

        Parameters
        ----------
        state_pointer : State
            The current state.
        transitions : list of ManimTransition
            The transitions outgoing from the current state.

        Returns
        -------
        dict
            Mapping of option index to ``(description, transition)`` tuples.
        """
        options: dict[int, tuple[str, ManimTransition]] = {}
        for index, transition in enumerate(transitions):
            next_state = transition.transition_to
            options[index] = (f"{state_pointer.name} --> {next_state.name}", transition)

        return options

    def export_recorded_path_to_file(self) -> None:
        """Save the recorded NDA path as JSON to recorded_path.txt."""
        with open("recorded_path.txt", "w") as fp:
            json.dump(self.recorded_path, fp)

    def load_recorded_path_from_file(
        self, file_name: str
    ) -> list[tuple[str, str]] | None:
        """Load a recorded NDA path from a JSON file, or return None if invalid.

        Parameters
        ----------
        file_name : str
            Path to the JSON file with the recorded path.

        Returns
        -------
        list of tuple of str or None
            The recorded path as a list of ``(from_state, to_state)`` tuples,
            or ``None`` if the file content is invalid.
        """
        with open(f"{file_name}", "r") as fp:
            path_list = json.load(fp)
            # check that the type is a list
            if type(path_list) is list:
                return path_list
        return None

    def play_string(self, input: Union[str, "ManimAutomataInput"]) -> list:
        """Run *input* through the automaton and return the animations.

        Parameters
        ----------
        input : str or :class:`~manim_extensions.automata.mobjects.manim_automaton_input.ManimAutomataInput`
            The input string, or an already constructed input mobject.

        Returns
        -------
        list of list of :class:`~manim.animation.animation.Animation`
            One entry per step; each entry is a list of animations that can
            be played with ``self.play(*entry)``.
        """
        if type(input) is str:
            # create mobject of input string
            self.manim_automata_input = self.construct_automaton_input(input)
            # position the mobject
            self.set_default_position_of_input_string()
            input_to_run = self.manim_automata_input
        else:
            self.manim_automata_input = (
                input  # if input is already an instance of ManimAutomataInput
            )
            input_to_run = input

        # display manim_automaton_input to the screen
        list_of_animations = [
            self.manim_animations.animate_display_input(self.manim_automata_input)
        ]

        # run the input through the machine, returning a history of what happend
        history = self.run_input_through_automaton(input_to_run)

        list_of_animations = list_of_animations + self.generate_history_animations(
            history
        )

        # normalize: every entry must be a list of animations so that callers
        # can uniformly do ``self.play(*entry)`` for each entry
        return [
            entry if isinstance(entry, list) else [entry]
            for entry in list_of_animations
        ]

    def generate_history_animations(self, history: dict[str, object]) -> list[object]:
        """Given a history of events of each iteration of the input ran through the manim automaton,
        generate all of the manim animations to visualise the process of the input going through the
        automaton

        Parameters
        ----------
        history : dict
            The run history returned by :meth:`~manim_extensions.automata.mobjects.manim_automaton.ManimAutomaton.run_input_through_automaton`.

        Returns
        -------
        list
            The animations visualising the input going through the automaton.
        """

        list_of_animations: list[object] = []

        # generate the pre-run animations
        state_pointer = self.get_initial_state()
        # Highlight current state with yellow
        list_of_animations.append(self.highlight_initial_state(state_pointer))
        for iteration_key in history:
            if (
                iteration_key == "information"
            ):  # provides information about the automaton and if it passed
                if history[iteration_key][
                    "automaton_result"
                ]:  # if the automaton has an active accepting state
                    list_of_animations.append(
                        self.generate_accept_animations()
                    )  # THIS IS GENERATED BEFORE ALL BRANCHES HAVE FINISHED
                else:  # if there is no final state then the machine is not accepted.
                    list_of_animations.append(self.generate_reject_animations())
            else:
                token = history[iteration_key]["token"]  # list of step histories
                iteration_history = history[iteration_key]["iteration_history"]

                # animate the token highlight
                list_of_animations.append(
                    [self.manim_animations.animate_highlight_input_token(token)]
                )

                for step_history in iteration_history:
                    list_of_animations = list_of_animations + self.animate_step_history(
                        step_history
                    )

                if self._animate_subscripts:
                    list_of_animations.append(
                        self.animate_subscripts(iteration_history)
                    )

                # animate the token fades
                list_of_animations.append(
                    [self.manim_animations.animate_input_token_spent(token)]
                )

        # generate outcome animations
        return list_of_animations

    def animate_step_history(self, step_history: dict[str, object]) -> list[object]:
        """Generate Manim animations for a single step's history entry.

        Parameters
        ----------
        step_history : dict
            A single step entry from the iteration history.

        Returns
        -------
        list
            The animations for this step.
        """
        list_of_animations: list[object] = []

        state_pointer = step_history["state_pointer"]
        next_neighbour_states = step_history["next_neighbour_states"]
        transitions = step_history["transitions"]
        step_result = step_history["result"]
        token = step_history["token"]

        # if step result is False then there are no more steps, check for final state and highlight state pointer as finished.
        step_animations = self.step(
            transitions, token, state_pointer, next_neighbour_states, step_result
        )  # self.step returns a list of animations for that step

        if step_animations is not None:
            list_of_animations = list_of_animations + step_animations

        return list_of_animations

    def highlight_initial_state(self, initial_state: ManimState) -> list[object]:
        """Return animations to highlight the initial state and set its subscript to 1.

        Parameters
        ----------
        initial_state : ManimState
            The initial state of the automaton.

        Returns
        -------
        list
            The highlight and subscript transform animations.
        """
        new_subscript_object = Tex(1, color=PURE_YELLOW)
        new_subscript_object.set_x(initial_state.subscript.get_x())
        new_subscript_object.set_y(initial_state.subscript.get_y())

        return [
            self.manim_animations.animate_highlight_state(initial_state),
            self.manim_animations.animate_transform_to_new_subscript_object(
                initial_state.subscript, new_subscript_object
            ),
        ]

    def generate_accept_animations(self) -> list[object]:
        """Return animations that transform the input text into green "ACCEPTED".

        Returns
        -------
        list
            The accept animations.
        """
        list_of_accept_animations: list[object] = []

        text = Tex("ACCEPTED", color=GREEN, font_size=100)
        text.set_x(self.manim_automata_input.get_x())
        text.set_y(self.manim_automata_input.get_y())

        list_of_accept_animations.append(Transform(self.manim_automata_input, text))
        # list_of_accept_animations.append(FadeToColor(self, color=GREEN))

        return list_of_accept_animations

    def generate_reject_animations(self) -> list[object]:
        """Return animations that transform the input text into red "REJECTED".

        Returns
        -------
        list
            The reject animations.
        """
        list_of_reject_animations: list[object] = []

        text = Tex("REJECTED", color=RED, font_size=100)
        text.set_x(self.manim_automata_input.get_x())
        text.set_y(self.manim_automata_input.get_y())

        list_of_reject_animations.append(Transform(self.manim_automata_input, text))
        # list_of_reject_animations.append(FadeToColor(self, color=RED))

        return list_of_reject_animations

    def step(
        self,
        manim_transitions: list[ManimTransition],
        token: "Tex",
        state_pointer: State,
        next_neighbour_states: list[State],
        step_result: bool,
    ) -> list[list[object]]:
        """Generate animation sequences for a single automaton step (transitions and state highlights).

        Parameters
        ----------
        manim_transitions : list of ManimTransition
            The transitions taken in this step.
        token : Tex
            The input token being processed.
        state_pointer : State
            The state the step starts from.
        next_neighbour_states : list of State
            The states reachable from the current state.
        step_result : bool
            Whether the token matched any transition.

        Returns
        -------
        list of list
            The animation sequences for this step.
        """
        # creates a list of animations for the step
        list_of_step_animations: list[list[object]] = []

        if step_result is False:  # if branch dies turn state red
            state_died_animation = []
            state_revert_back_to_default_animation = []

            # state_died_animation.append(FadeToColor(state_pointer, color=RED))
            state_died_animation.append(
                self.manim_animations.animate_dead_branch_state(state_pointer)
            )

            state_revert_back_to_default_animation.append(
                self.manim_animations.animate_state_to_default_color(state_pointer)
            )

            list_of_step_animations.append(state_died_animation)
            list_of_step_animations.append(state_revert_back_to_default_animation)

        else:
            activate_transition_animation = [
                self.manim_animations.animate_highlight_transition(x)
                for x in manim_transitions
            ]

            # if successful point to the next state
            state_animations = []

            if step_result is True:

                if len(next_neighbour_states) > 0:
                    state_animations.append(
                        self.manim_animations.animate_state_to_default_color(
                            state_pointer
                        )
                    )

                    state_animations = state_animations + [
                        self.manim_animations.animate_highlight_state(x)
                        for x in next_neighbour_states
                    ]

            deactivate_transition_animation = [
                self.manim_animations.animate_transition_to_default_color(x)
                for x in manim_transitions
            ]

            # add the animations in the correct order
            list_of_step_animations.append(activate_transition_animation)

            list_of_step_animations.append(state_animations)

            list_of_step_animations.append(deactivate_transition_animation)

        return list_of_step_animations

    def animate_subscripts(
        self, iteration_history: list[dict[str, object]]
    ) -> list[object]:
        """Animate state subscripts to show the count of active branches ending in each state.

        Parameters
        ----------
        iteration_history : list of dict
            The step histories of the current iteration.

        Returns
        -------
        list
            The subscript transform animations.
        """
        animations: list[object] = []
        # record the number of branches that end on each states
        state_counter = {}

        for step_history in iteration_history:
            next_neighbour_states = step_history["next_neighbour_states"]

            for state in next_neighbour_states:
                counter = state_counter.setdefault(
                    state.id, 0
                )  # key might exist already
                state_counter[state.id] = state_counter[state.id] + 1

                # state_counter.setdefault(state.id, 1)
                # state_counter[state.id] = state_counter[state.id] + 1

        for state in self.states:
            if state.id in state_counter:
                new_subscript_object = Tex(state_counter[state.id], color=PURE_YELLOW)
                new_subscript_object.set_x(state.subscript.get_x())
                new_subscript_object.set_y(state.subscript.get_y())
                animations.append(
                    self.manim_animations.animate_transform_to_new_subscript_object(
                        state.subscript, new_subscript_object
                    )
                )
            else:
                new_subscript_object = Tex(0, color=BLUE)
                new_subscript_object.set_x(state.subscript.get_x())
                new_subscript_object.set_y(state.subscript.get_y())
                animations.append(
                    self.manim_animations.animate_transform_to_new_subscript_object(
                        state.subscript, new_subscript_object
                    )
                )

        return animations

# SPDX-FileCopyrightText: 2022 Sean Nelson
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


"""Contains pushdown automaton."""

from __future__ import annotations

from manim import *

from .manim_non_determinstic_finite_state_automaton import ManimNonDeterminsticFiniteAutomaton
from .manim_state import ManimState, State
from .manim_transition import ManimTransition, ManimPushDownAutomatonTransition
from .manim_automaton_input import ManimAutomataInput

from typing import Union

pushdown_automaton_json = {
    'structure': {
        'type': 'pda',
        'automaton': {
            'state': [
                {'@id': '0', '@name': 'q0', 'x': '84.0', 'y': '122.0', 'initial': None},
                {'@id': '1', '@name': 'q1', 'x': '218.0', 'y': '175.0'},
                {'@id': '2', '@name': 'q2', 'x': '386.0', 'y': '131.0', 'final': None},
                {'@id': '3', '@name': 'q3', 'x': '227.0', 'y': '36.0'}
            ],
            'transition': [
                {'from': '0', 'to': '1', 'read': '0', 'pop': 'Z', 'push': 'XZ'},
                {'from': '0', 'to': '1', 'read': '1', 'pop': 'Z', 'push': 'XZ'},
                {'from': '2', 'to': '3', 'read': '0', 'pop': 'X', 'push': ''},
                {'from': '1', 'to': '2', 'read': '1', 'pop': 'X', 'push': 'XX'},
                {'from': '3', 'to': '0', 'read': '1', 'pop': 'X', 'push': ''},
                {'from': '3', 'to': '0', 'read': '0', 'pop': 'X', 'push': ''}
            ]
        }
    }
}

class ManimPushDownAutomaton(ManimNonDeterminsticFiniteAutomaton):
    """Pushdown automaton that also tracks a stack during simulation.

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
    **kwargs
        Key words arguments forwarded to :class:`~manim.mobject.types.vectorized_mobject.VGroup`.

    Examples
    --------
    .. manim:: ManimPushDownAutomatonExample
       :save_last_frame:

       from manim import *
       from manim_extensions.automata.mobjects.manim_pushdown_automaton import ManimPushDownAutomaton

       class ManimPushDownAutomatonExample(Scene):
           def construct(self):
               pda = ManimPushDownAutomaton()
               self.add(pda)
"""

    stack: list

    def __init__(self, json_template: dict[str, object] | None = None, xml_file: str | None = None, camera_follow: bool = False, animation_style: dict[str, object] | None = None, **kwargs: object) -> None:
        """Initialize the ManimPushDownAutomaton instance."""
        if json_template is None and xml_file is None:
            json_template = pushdown_automaton_json
        super().__init__(json_template, xml_file, camera_follow, animation_style, **kwargs)
        #initialise stack - Z is the bottom stack symbol
        self.stack = ["Z"]

    #override ManimAutomaton method
    def construct_transitions(self, transitions: list[dict[str, object]]) -> None:
        """Build pushdown-automaton transitions from XML or JSON definitions.

    Parameters
    ----------
    transitions
    Transitions processed by this operation.
    """
        # counts the number of transitions between two states
        transition_counter = {}
        # for transition in self.automaton.transitions:
        #if 2 or more transitions exist between states then this will merge them together in one transition.
        for transition in transitions:
            """put from and to states into tuple to be used as
            dictionary key."""
            state_key = (transition['from'], transition['to'])
            
            transition_group = transition_counter.setdefault(state_key, [])

            rule = PushDownAutomatonRule(
                transition.get('read'),
                transition.get('pop', ''),
                transition.get('push', ''),
            )

            transition_group.append(rule)

        #avoids creating multiple manim_transitions.
        #Creates one manim_transition with multiple rules
        for state_key in transition_counter:
            rules = transition_counter[state_key]

            transition_from = self.get_state_by_id(int(state_key[0]))
            transition_to = self.get_state_by_id(int(state_key[1]))

            self.construct_transition(transition_from, transition_to, rules)

    def construct_transition(self, transition_from: ManimState, transition_to: ManimState, rules: list[PushDownAutomatonRule]) -> None:
        """Create and attach a pushdown transition between two states.

        Parameters
        ----------
        transition_from : ManimState
            Source state of the transition.
        transition_to : ManimState
            Target state of the transition.
        rules : list of PushDownAutomatonRule
            Pushdown rules (input symbol, pop symbol, push symbol)
            associated with this transition.
        """
        new_transition = ManimPushDownAutomatonTransition(transition_from, transition_to, rules, parent_automaton=self, animation_style=self.animation_style)
        self.transitions.append(new_transition)
        #add the transition to the from_states link list
        transition_from.add_transition_to_state(new_transition)

    def push(self, push_item: str) -> list[str]:
        """Push a token onto the automaton stack.

        Parameters
        ----------
        push_item : str
            Symbol to push onto the stack.

        Returns
        -------
        list of str
            The stack contents after the push.
        """
        self.stack.append(push_item)
        return self.stack

    def pop(self) -> str | None:
        """Remove and return the top stack symbol."""
        if not self.stack:
            return None
        return self.stack.pop()

    #pushdown automata can accept if the stack is empty or if it falls on a final state TODO
    #overriden
    def play_string(self, input: Union[str, "ManimAutomataInput"], automaton_path_name: str | None = None, accept_on_final_state: bool = True) -> list:
        """Animate the pushdown automaton processing an input string.

        Parameters
        ----------
        input : str or ManimAutomataInput
            The input string or pre-constructed input mobject.
        automaton_path_name : str or None
            Optional path name for the automaton traversal.
        accept_on_final_state : bool
            If ``True``, acceptance requires ending on a final state.

        Returns
        -------
        list
            A list of animations to play.
        """
        if type(input) is str:
            #create mobject of input string
            self.manim_automata_input = self.construct_automaton_input(input)
            #position the mobject
            self.set_default_position_of_input_string()
            #display manim_automaton_input to the screen
            list_of_animations.append(self.manim_animations.animate_display_input(self.manim_automata_input))
        else: self.manim_automata_input = input #if input is already an instance of ManimAutomataInput

        #run the input through the machine, returning a history of what happend
        history = self.run_input_through_automaton(input)

        list_of_animations = self.generate_history_animations(history)

                    # if self.check_automaton_result([state_pointer]): #if the automaton has an active accepting state
                    #     list_of_animations.append(self.generate_accept_animations()) #THIS IS GENERATED BEFORE ALL BRANCHES HAVE FINISHED
                    # else: #if there is no final state then the machine is not accepted.
                    #     list_of_animations.append(self.generate_reject_animations())

        return list_of_animations


    #overriden
    def automaton_step(self, token: str, state_pointer: State) -> tuple[bool, list[State], list[ManimTransition]]:
        """Perform one step of the pushdown automaton on the given token.

        Parameters
        ----------
        token : str
            The input token to process.
        state_pointer : State
            The current state.

        Returns
        -------
        tuple
            ``(accepted, next_states, transitions)`` indicating whether the
            token was accepted, the reachable next states, and the
            corresponding transitions.
        """
        next_states = [] #stores all of the next states that can be jumped to
        transitions = [] #store the transitions that transition from current to next states.
        
        #go through each transition of this state
        state_transitions = state_pointer.get_transitions()
        for transition in state_transitions:


            #check if any transition's rules match the input token
            for rule in transition.rules: #Iterate through the transtion's read options
                if rule.read_symbol == token.tex_string or rule.read_symbol == r"\epsilon":
                    next_states.append(transition.transition_to)
                    transitions.append(transition)

                    #some code for stack too - TODO


        if len(next_states) != 0:
            return True, next_states, transitions #the token matches the transition's input

        return False, next_states, transitions #There are no other transitions/ reachable next states given the token

    #nondeterministic pushdown automata have difference stacks - maybe a later requirement? Probably

    #the only difference in history is that we have a stack
    #check to see if the transition matches the input token
    #if not - fail
    #if true then execute the transition rule
    #update stack

    # transition.rules has each rule

    #change the way we generate animations / add the animations needed for stack, push and pop
    #need to probably animate which transition rule it takes too




class PushDownAutomatonRule():
    """A single pushdown-automaton transition rule.

    Parameters
    ----------
    read_symbol : str
        Input symbol consumed by this rule.
    pop : str
        Symbol popped from the stack.
    push : str
        Symbol pushed onto the stack.
    empty_transition : str, optional
        Symbol used when ``read_symbol`` is ``None``.  Defaults to ``"\\epsilon"``.

    Examples
    --------
    .. manim:: PushDownAutomatonRuleExample
       :save_last_frame:

       from manim import *
       from manim_extensions.automata.mobjects.manim_pushdown_automaton import PushDownAutomatonRule

       class PushDownAutomatonRuleExample(Scene):
           def construct(self):
               rule = PushDownAutomatonRule("a", "X", "XY")
               label = Text(f"Rule: read={rule.read_symbol}, pop={rule.pop}, push={rule.push}", font_size=20)
               self.add(label)
"""

    read_symbol: str
    pop: str
    push: list[str]

    def __init__(self, read_symbol: str, pop: str, push: str, empty_transition: str = r"\epsilon") -> None:
        """Initialize the PushDownAutomatonRule instance."""
        if read_symbol is None:
            self.read_symbol = empty_transition
        else:
            self.read_symbol = read_symbol

        self.pop = pop
        self.push = []

        if not push:
            self.push = [empty_transition]
        else:
            for push_item in push:
                self.push.append(push_item)

    def __str__(self) -> str:
        """Internal __str__ hook."""
        formatted_push_string = ''.join(str(x) for x in self.push)
        return f'{self.read_symbol},{self.pop};{formatted_push_string}'





    #every transition we pop one item of the stack,

    #if there is an 'a' and we pop a Z then we push YZ, first the Z and then the Y
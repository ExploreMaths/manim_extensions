from asyncio import constants
from .xml_parser import parse_xml_file


from .state import State
from .transitition import Transition

import itertools

        
automaton_json = {
    'structure': {
        'type': 'fa',
        'automaton': {
            'state': [
                {'@id': '0', '@name': 'q0', 'x': '84.0', 'y': '122.0', 'initial': None},
                {'@id': '1', '@name': 'q1', 'x': '218.0', 'y': '175.0'},
                {'@id': '2', '@name': 'q2', 'x': '386.0', 'y': '131.0', 'final': None},
                {'@id': '3', '@name': 'q3', 'x': '227.0', 'y': '36.0'}
            ],
            'transition': [
                {'from': '0', 'to': '1', 'read': '0'},
                {'from': '0', 'to': '1', 'read': '1'},
                {'from': '2', 'to': '3', 'read': '0'},
                {'from': '1', 'to': '2', 'read': '1'},
                {'from': '3', 'to': '0', 'read': '1'},
                {'from': '3', 'to': '0', 'read': '0'}
            ]
        }
    }
}
# class PushdownAutomaton(Automaton): TODO
#     def __init__(self) -> None:
#         pass

#create error message here - need to look up standard. TODO


#this class manages states and transitions, including simulation
class FiniteStateAutomaton():

    """Formal finite-state automaton model.

    This class manages the underlying data structures for states and
    transitions, and provides methods for simulating input strings through
    the automaton.  It can be constructed from a JSON dictionary or parsed
    from an XML file (e.g. JFLAP format).

    Parameters
    ----------
    json_template : dict, optional
        JSON dictionary describing the automaton states and transitions.

    Examples
    --------
    .. manim:: FiniteStateAutomatonExample
       :save_last_frame:

       from manim import *
       from manim_extensions.automata.mobjects.automata_dependencies.automata import FiniteStateAutomaton

       class FiniteStateAutomatonExample(Scene):
           def construct(self):
               fa = FiniteStateAutomaton()
               label = Text(f"States: {len(fa.states)}", font_size=24)
               self.add(label)
"""
    id_iter = itertools.count()

    def __init__(self, json_template: dict | None = None) -> None:
        """Initialize the FiniteStateAutomaton instance."""
        self.id = next(self.id_iter)
        self.states: list[State] = []
        self.transitions: list[Transition] = []
        self.origin_offset_x = 0.0
        self.origin_offset_y = 0.0

        if json_template:
            self.construct_from_json(json_template)

    def process_xml(self, xml_file: str) -> None:
        """Construct the automaton from an XML file.

        Parameters
        ----------
        xml_file : str
            Path to the XML file describing the automaton.
        """
        self.construct_from_json(parse_xml_file(xml_file))

    def construct_from_json(self, json_dictionary: dict) -> None:
        """Construct the automaton from a JSON-like dictionary.

        Parameters
        ----------
        json_dictionary : dict
            Structured automaton data containing the state and transition lists.
        """
        states = json_dictionary["structure"]["automaton"]["state"]
        transitions = json_dictionary["structure"]["automaton"]["transition"]

        self.construct_states(states)
        self.construct_transitions(transitions)

    def construct_states(self, states: list[dict[str, object]]) -> None:
        """Construct state objects from a list of state dictionaries.

        Parameters
        ----------
        states : list of dict
            State definitions from JSON or XML parsing.
        """
        for state_data in states:
            initial = state_data.get('initial') is not None
            final = state_data.get('final') is not None
            state_id = int(state_data.get('@id', 0))
            name = state_data.get('@name', str(state_id))
            self.states.append(State(name, initial=initial, final=final, id=state_id))

    def construct_transitions(self, transitions: list[dict[str, object]]) -> None:
        """Construct transition objects from a list of transition dictionaries.

        Parameters
        ----------
        transitions : list of dict
            Transition definitions from JSON or XML parsing.
        """
        for trans_data in transitions:
            from_id = int(trans_data['from'])
            to_id = int(trans_data['to'])
            read = trans_data.get('read')
            from_state = self.get_state_by_id(from_id)
            to_state = self.get_state_by_id(to_id)
            if from_state and to_state:
                transition = Transition(from_state, to_state)
                transition.read_symbols = [read] if read else []
                self.transitions.append(transition)
                from_state.add_transition_to_state(transition)
    

    #State Methods
    def get_initial_state(self) -> State:
        """Return the state marked as the initial state.

        Returns
        -------
        State
            The initial state.
        """
        for state in self.states:
            if state.initial == True:
                return state

    def get_state(self, name: str) -> State | None:
        """Return the state with the provided name.

        Parameters
        ----------
        name
            Name of the state to retrieve.
        """
        for state in self.states:
            if state.name == name:
                return state
        return None

    def get_state_by_id(self, id: int) -> State | None:
        """Return the state with the provided identifier.

        Parameters
        ----------
        id : int
            Identifier of the state to retrieve.
        """
        for state in self.states:
            if state.id == id:
                return state
        return None

    def automaton_step(self, token: str, state_pointer: State) -> tuple[bool, list[State], list[Transition]]:
        """Advance the automaton by one token from the current state.

        Parameters
        ----------
        token : str
            Input token to consume.
        state_pointer : State
            Current state from which the step is evaluated.
        """
        next_states = [] #stores all of the next states that can be jumped to
        transitions = [] #store the transitions that transition from current to next states.
        
        #go through each transition of this state
        state_transitions = state_pointer.get_transitions()
        for transition in state_transitions:
            #check if any transition's symbols match the input token
            for read_symbol in transition.read_symbols: #Iterate through the transtion's read options
                if read_symbol.tex_string == token.tex_string or read_symbol.tex_string == r"\epsilon":
                    next_states.append(transition.transition_to)
                    transitions.append(transition)


        if len(next_states) != 0:
            return True, next_states, transitions #the token matches the transition's input

        return False, next_states, transitions #There are no other transitions/ reachable next states given the token

    #IMPORTANT
    #if there is an epsilon transition then take it regardless of the input
    #needs to be added
    #also possibly redesign the play_string method.



    #Transition Methods
    def get_transition_by_id(self, id: int) -> Transition | None:
        """Return the transition with the given identifier.

        Parameters
        ----------
        id : int
            The transition's unique id.

        Returns
        -------
        Transition or None
            The matching transition, or ``None`` if not found.
        """
        for transition in self.transitions:
            if transition.id == id:
                return transition
        return None



class PushDownAutomaton(FiniteStateAutomaton):
    """Formal pushdown automaton model.

    Extends :class:`~manim_extensions.automata.mobjects.automata_dependencies.automata.FiniteStateAutomaton` with stack-based computation.
    Pushdown automata can be constructed from JSON templates or XML files
    and support non-deterministic branching via the CLI builder.

    Examples
    --------
    .. manim:: PushDownAutomatonExample
       :save_last_frame:

       from manim import *
       from manim_extensions.automata.mobjects.automata_dependencies.automata import PushDownAutomaton

       class PushDownAutomatonExample(Scene):
           def construct(self):
               pda = PushDownAutomaton()
               label = Text(f"States: {len(pda.states)}", font_size=24)
               self.add(label)
"""
    def __init__(self) -> None:
        """Initialize the PushDownAutomaton instance."""
        super().__init__()

    def automaton_step(self, token: str, state_pointer: State, determinstic: bool = True) -> tuple[bool, list[State], list[int]]:
        """Perform one step of the automaton on the given token.

        Parameters
        ----------
        token : str
            The input token to process.
        state_pointer : State
            The current state.
        determinstic : bool
            If ``True``, return as soon as the first matching transition is found.

        Returns
        -------
        tuple
            ``(accepted, next_states, transition_ids)`` indicating whether the
            token was accepted, the reachable next states, and the matching
            transition ids.
        """
        next_states = [] #stores all of the next states that can be jumped to
        transition_ids = [] #store the ids of the transitions that transition from current to next states.
        
        #go through each transition of this state
        state_transitions = state_pointer.get_transitions()
        for transition in state_transitions:
            #check if any transition's symbols match the input token
            for read_symbol in transition.read_symbols: #Iterate through the transtion's read options
                if read_symbol.tex_string == token.tex_string:
                    next_states.append(transition.transition_to)
                    transition_ids.append(transition.id)
                    if determinstic: #pick the first valid transition and next state then returns.
                        return True, next_states, transition_ids #the token matches the transition's input

        if len(next_states) != 0:
            return True, next_states, transition_ids #the token matches the transition's input

        return False, next_states, transition_ids #There are no other transitions/ reachable next states given the token
from manim import *

from .manim_automaton import ManimAutomaton
from .manim_state import ManimState, State
from .manim_automaton_input import ManimAutomataInput
from .manim_transition import ManimTransition


from typing import Union

class ManimDeterminsticFiniteAutomaton(ManimAutomaton):

    """A deterministic finite automaton (DFA) with Manim visualisation.

    This subclass of :class:`ManimAutomaton` represents a DFA where each
    state has exactly one outgoing transition for every input symbol.  It
    can be constructed from a JSON template or an XML file (JFLAP format).

    Examples
    --------
    .. manim:: ManimDeterminsticFiniteAutomatonExample
       :save_last_frame:

       from manim import *
       from manim_extensions.automata.mobjects.manim_determinstic_finite_state_automaton import ManimDeterminsticFiniteAutomaton

       class ManimDeterminsticFiniteAutomatonExample(Scene):
           def construct(self):
               dfa = ManimDeterminsticFiniteAutomaton()
               self.add(dfa)
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
        """Initialize the ManimDeterminsticFiniteAutomaton instance."""
        if animation_style is None:
            super().__init__(json_template, xml_file, camera_follow, cli=cli, **kwargs)
        else:
            super().__init__(json_template, xml_file, camera_follow,  animation_style, cli=cli, **kwargs)

        if cli: #if cli exist display options to user
            self.cli.display_nda_options()
            if self.cli.nda_option == 0: #check the settings of the cli (what the user wants to do)
                self.nda_builder = True
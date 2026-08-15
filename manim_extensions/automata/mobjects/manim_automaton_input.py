from typing import Any

from manim import *

import itertools

class ManimAutomataInput(VGroup):
    """Graphical representation of an input string used in automata animations.

    Parameters
    ----------
    input_string : str
        The string to display as input tokens.
    animation_style : dict
        Styling configuration used to animate token highlighting.
    font_size : int, optional
        Font size used for each token. Defaults to ``100``.
    **kwargs
        Additional keyword arguments passed to :class:`~manim.mobject.types.vectorized_mobject.VGroup`.

    Attributes
    ----------
    tokens : list
        Text mobjects representing the individual input characters.

    Examples
    --------
    .. manim:: ManimAutomataInputExample
       :save_last_frame:

       from manim import *
       from manim_extensions.automata.mobjects.manim_automaton_input import ManimAutomataInput

       class ManimAutomataInputExample(Scene):
           def construct(self):
               inp = ManimAutomataInput("0101", animation_style={})
               self.add(inp)
    """
    def __init__(self, input_string: str, animation_style: dict[str, Any], font_size: int = 100, **kwargs: Any) -> None:

        """Initialize the ManimAutomataInput instance."""
        super().__init__(**kwargs)

        self.animation_style = animation_style

        #token creation
        self.tokens = []
        spacing = 0
        for token_symbol in input_string:
            token_mobject = Token(token_symbol, spacing, font_size)
            

            self.add(token_mobject)
            self.tokens.append(token_mobject)

            spacing = spacing + 1

        

    @staticmethod
    def highlight_token(token: MathTex, animation_style: dict[str, Any]) -> Any:
        """Highlight a token using the configured animation style.

        Parameters
        ----------
        token
            The token to highlight.
        animation_style : dict
            Animation configuration containing the highlight function and color.
        """
        animation_function = animation_style["token_highlight"]["animation_function"]
        color = animation_style["token_highlight"]["color"]

        return animation_function(token, color=color)
    

class Token(MathTex):

    """A single input token rendered as maths text.

    Each token has a unique numeric identifier and stores its horizontal
    spacing offset so that tokens can be laid out sequentially.

    Parameters
    ----------
    symbol : str
        The character or symbol to display.
    spacing : float
        Horizontal offset applied when positioning the token.
    font_size : int, optional
        Font size for the token text.  Defaults to ``100``.

    Examples
    --------
    .. manim:: TokenExample
       :save_last_frame:

       from manim import *
       from manim_extensions.automata.mobjects.manim_automaton_input import Token

       class TokenExample(Scene):
           def construct(self):
               token = Token("a", 0)
               self.add(token)
"""
    id_iter = itertools.count()

    def __init__(self, token_symbol: str, spacing: int, font_size: int = 100, **kwargs: Any) -> None:

        """Initialize the Token instance."""
        super().__init__(token_symbol, font_size=font_size, **kwargs)

        self.id = next(self.id_iter)

        self.set_x(0 + spacing)
        self.set_y(0)

        # self.text
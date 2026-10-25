# SPDX-FileCopyrightText: 2022 Sean Nelson
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Input representation for automata visualization.

This module provides the ManimAutomataInput class for representing input strings in automata.

"""


from manim import MathTex, VGroup
from typing import Any

import itertools


class ManimAutomataInput(VGroup):
    """Graphical representation of an input string used in automata animations.

    Parameters
    ----------
    input_string
        The string to display as input tokens.
    animation_style
        Styling configuration used to animate token highlighting.
    font_size
        Font size used for each token. 
    **kwargs
        Additional keyword arguments passed to :class:`~manim.mobject.types.vectorized_mobject.VGroup`.

    Attributes
    ----------
    tokens : list
        Text mobjects representing the individual input characters.

    Examples
    --------
    .. manim:: ManimAutomataInputExample

       from manim import *
       from manim_extensions.automata.mobjects.manim_animations import ManimAnimations
       from manim_extensions.automata.mobjects.manim_automaton_input import ManimAutomataInput

       class ManimAutomataInputExample(Scene):
           def construct(self):
               inp = ManimAutomataInput("0101", animation_style={})
               inp.scale_to_fit_height(2.5).move_to(ORIGIN)
               self.add(inp)
               animations = ManimAnimations()
               for token in inp.tokens:
                   self.play(animations.animate_highlight_input_token(token))
                   self.play(animations.animate_input_token_spent(token))
    """

    def __init__(
        self,
        input_string: str,
        animation_style: dict[str, Any],
        font_size: int = 100,
        **kwargs: Any,
    ):
        """Initialize the ManimAutomataInput instance."""
        super().__init__(**kwargs)

        self.animation_style = animation_style

        # token creation
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
        animation_style
            Animation configuration containing the highlight function and color.

        Returns
        -------
            The animation highlighting the token.
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
    token_symbol
        The character or symbol to display.
    spacing
        Horizontal offset applied when positioning the token.
    font_size
        Font size for the token text.  
    **kwargs
        Additional keyword arguments forwarded to :class:`~manim.mobject.types.vectorized_mobject.MathTex`.

    Examples
    --------
    .. manim:: TokenExample

       from manim import *
       from manim_extensions.automata.mobjects.manim_automaton_input import Token

       class TokenExample(Scene):
           def construct(self):
               tokens = [Token(symbol, spacing) for spacing, symbol in enumerate("010")]
               content = VGroup(*tokens)
               content.scale_to_fit_height(2.5).move_to(ORIGIN)
               self.add(content)
               self.play(FadeToColor(tokens[1], PURE_YELLOW))
    """

    id_iter = itertools.count()

    def __init__(
        self, token_symbol: str, spacing: int, font_size: int = 100, **kwargs: Any
    ):
        """Initialize the Token instance."""
        super().__init__(token_symbol, font_size=font_size, **kwargs)

        self.id = next(self.id_iter)

        self.set_x(0 + spacing)
        self.set_y(0)
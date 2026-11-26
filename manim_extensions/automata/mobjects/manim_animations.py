# SPDX-FileCopyrightText: 2022 Sean Nelson
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Animation utilities for automata visualization.

This module provides the :class:`~manim_extensions.automata.mobjects.manim_animations.ManimAnimations` class for animating automata visualizations.
"""

from typing import Any, cast

from manim import (
    Animation,
    BLUE,
    FadeIn,
    FadeToColor,
    Mobject,
    PURE_YELLOW,
    RED,
    Transform,
    WHITE,
)


class ManimAnimations:
    """Default animation strategy for automata visualisation.

    .. doc-example-covers: animate_dead_branch_state, animate_display_input, animate_highlight_input_token, animate_highlight_state, animate_highlight_transition, animate_input_token_spent, animate_state_to_default_color, animate_transform_to_new_subscript_object, animate_transition_to_default_color


    This class encapsulates all individual animations used during automaton
    simulation: highlighting states and transitions, marking tokens as
    consumed, transforming subscripts, and displaying input strings.

    Each method returns a Manim :class:`~manim.animation.animation.Animation`
    that can be composed into an :class:`~manim.animation.composition.AnimationGroup`
    or :class:`~manim.animation.composition.Succession`.

    Examples
    --------
    .. manim:: ManimAnimationsScene

       from manim import *
       from manim_extensions.automata.mobjects.manim_animations import ManimAnimations

       class ManimAnimationsScene(Scene):
           def construct(self):
               animations = ManimAnimations()
               state = Circle(radius=1)
               token = MathTex("0").next_to(state, UP)
               self.add(state, token)
               self.play(animations.animate_highlight_state(state))
               self.play(animations.animate_highlight_input_token(token))
               self.play(animations.animate_input_token_spent(token))
               self.play(animations.animate_dead_branch_state(state))
               self.play(animations.animate_state_to_default_color(state))
               self.wait()
    """

    def __init__(self) -> None:
        pass

    # state animations
    def animate_dead_branch_state(self, state: Mobject) -> Animation:
        """Return an animation that marks a rejected state as dead.

        Parameters
        ----------
        state
            :class:`~manim_extensions.automata.mobjects.automata_dependencies.state.State` mobject to recolor as a rejected branch.

        Returns
        -------
            The animation marking the state as dead.
        """
        return FadeToColor(state, color=cast(Any, RED))

    def animate_state_to_default_color(self, state: Mobject) -> Animation:
        """Return an animation resetting a state to its default color.

        Parameters
        ----------
        state
            :class:`~manim_extensions.automata.mobjects.automata_dependencies.state.State` mobject to recolor back to its normal styling.

        Returns
        -------
            The animation resetting the state color.
        """
        return FadeToColor(state, color=cast(Any, BLUE))

    def animate_highlight_state(self, state: Mobject) -> Animation:
        """Return an animation highlighting a state.

        Parameters
        ----------
        state
            :class:`~manim_extensions.automata.mobjects.automata_dependencies.state.State` mobject to highlight during a transition or match.

        Returns
        -------
            The animation highlighting the state.
        """
        return FadeToColor(state, color=cast(Any, PURE_YELLOW))

    # transition animations
    def animate_transition_to_default_color(self, transition: Mobject) -> Animation:
        """Return an animation resetting a transition to its default color.

        Parameters
        ----------
        transition
            :class:`~manim_extensions.automata.mobjects.automata_dependencies.transition.Transition` mobject to recolor to its default appearance.

        Returns
        -------
            The animation resetting the transition color.
        """
        return FadeToColor(transition, color=cast(Any, WHITE))

    def animate_highlight_transition(self, transition: Mobject) -> Animation:
        """Return an animation highlighting a transition.

        Parameters
        ----------
        transition
            :class:`~manim_extensions.automata.mobjects.automata_dependencies.transition.Transition` mobject to emphasize during a successful match.

        Returns
        -------
            The animation highlighting the transition.
        """
        return FadeToColor(transition, color=cast(Any, PURE_YELLOW))

    # input animations
    def animate_input_token_spent(self, token: Mobject) -> Animation:
        """Return an animation marking an input token as consumed.

        Parameters
        ----------
        token
            Input token mobject to dim after being used.

        Returns
        -------
            The animation marking the token as consumed.
        """
        return cast(Animation, token.animate.set_opacity(0.5))

    def animate_highlight_input_token(self, token: Mobject) -> Animation:
        """Return an animation highlighting an input token.

        Parameters
        ----------
        token
            Input token mobject to highlight during processing.

        Returns
        -------
            The animation highlighting the token.
        """
        return FadeToColor(token, color=cast(Any, PURE_YELLOW))

    def animate_display_input(self, input: Mobject) -> Animation:
        """Return an animation that reveals the input display.

        Parameters
        ----------
        input
            Input object to fade in on the scene.

        Returns
        -------
            The animation revealing the input display.
        """
        return FadeIn(input)

    # subscript animations
    def animate_transform_to_new_subscript_object(
        self, initial_subscript: Mobject, new_subscript: Mobject
    ) -> Animation:
        """Return a transform animation between two subscript labels.

        Parameters
        ----------
        initial_subscript
            The current subscript object being replaced.
        new_subscript
            The replacement subscript object.

        Returns
        -------
            The transform animation between the two subscript objects.
        """
        return Transform(initial_subscript, new_subscript)

from manim import Animation, Mobject, Transform, FadeToColor, RED, BLUE, WHITE, YELLOW, FadeIn


class ManimAnimations():

    """Default animation strategy for automata visualisation.

    This class encapsulates all individual animations used during automaton
    simulation: highlighting states and transitions, marking tokens as
    consumed, transforming subscripts, and displaying input strings.

    Each method returns a Manim :class:`~manim.animation.animation.Animation`
    that can be composed into an :class:`~manim.animation.composition.AnimationGroup`
    or :class:`~manim.animation.composition.Succession`.

    Examples
    --------
    .. manim:: ManimAnimationsExample
       :save_last_frame:

       from manim import *
       from manim_extensions.automata.mobjects.manim_animations import ManimAnimations

       class ManimAnimationsExample(Scene):
           def construct(self):
               anim = ManimAnimations()
               circle = Circle()
               self.add(circle)
"""
    def __init__(self) -> None:
        """Initialize the ManimAnimations instance."""
        pass

    #state animations
    def animate_dead_branch_state(self, state: Mobject) -> Animation:
        """Return an animation that marks a rejected state as dead.

        Parameters
        ----------
        state
            State mobject to recolor as a rejected branch.
        """
        return FadeToColor(state, color=RED)

    def animate_state_to_default_color(self, state: Mobject) -> Animation:
        """Return an animation resetting a state to its default color.

        Parameters
        ----------
        state
            State mobject to recolor back to its normal styling.
        """
        return FadeToColor(state, color=BLUE)

    def animate_highlight_state(self, state: Mobject) -> Animation:
        """Return an animation highlighting a state.

        Parameters
        ----------
        state
            State mobject to highlight during a transition or match.
        """
        return FadeToColor(state, color=YELLOW)

    #transition animations
    def animate_transition_to_default_color(self, transition: Mobject) -> Animation:
        """Return an animation resetting a transition to its default color.

        Parameters
        ----------
        transition
            Transition mobject to recolor to its default appearance.
        """
        return FadeToColor(transition, color=WHITE)

    def animate_highlight_transition(self, transition: Mobject) -> Animation:
        """Return an animation highlighting a transition.

        Parameters
        ----------
        transition
            Transition mobject to emphasize during a successful match.
        """
        return FadeToColor(transition, color=YELLOW)

    #input animations
    def animate_input_token_spent(self, token: Mobject) -> Animation:
        """Return an animation marking an input token as consumed.

        Parameters
        ----------
        token
            Input token mobject to dim after being used.
        """
        return token.animate.set_opacity(0.5)

    def animate_highlight_input_token(self, token: Mobject) -> Animation:
        """Return an animation highlighting an input token.

        Parameters
        ----------
        token
            Input token mobject to highlight during processing.
        """
        return FadeToColor(token, color=YELLOW)

    def animate_display_input(self, input: Mobject) -> Animation:
        """Return an animation that reveals the input display.

        Parameters
        ----------
        input
            Input object to fade in on the scene.
        """
        return FadeIn(input)

    #subscript animations
    def animate_transform_to_new_subscript_object(self, initial_subscript: Mobject, new_subscript: Mobject) -> Animation:
        """Return a transform animation between two subscript labels.

        Parameters
        ----------
        initial_subscript
            The current subscript object being replaced.
        new_subscript
            The replacement subscript object.
        """
        return Transform(initial_subscript, new_subscript)
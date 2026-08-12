from manim import *
import numpy as np


def VisDrawArc(
    scene: Scene,
    arc: Arc,
    axis: np.ndarray = OUT,
    run_time: float = 1,
) -> None:
    """Visualised arc-drawing animation.

    Plays an animation in *scene* that draws *arc* while simultaneously
    showing a moving dot travelling along the arc and a dashed radius line.

    .. note::

        This is a **convenience function** — call it directly; there is no
        need to wrap it in ``self.play()``.

    Parameters
    ----------
    scene : :class:`~manim.scene.scene.Scene`
        The Manim scene in which the animation is played.
    arc : :class:`~manim.mobject.geometry.Arc`
        The arc to draw.
    axis : numpy.ndarray, optional
        Rotation axis. ``OUT`` gives counter‑clockwise motion, ``IN`` gives
        clockwise motion. Defaults to ``OUT``.
    run_time : float, optional
        Duration of the animation in seconds. Defaults to ``1``.

    Examples
    --------

    .. manim:: VisDrawArcDocExample

       from manim import *
       from manim_extensions import VisDrawArc

       class VisDrawArcDocExample(Scene):
           def construct(self):
               arc = Arc(start_angle=0, angle=PI, radius=2, color=YELLOW)
               VisDrawArc(self, arc, axis=OUT, run_time=2)
               self.wait()
    """

    # Get the start point, end point, and centre of the arc
    start_point = arc.point_from_proportion(0)
    end_point = arc.point_from_proportion(1)
    center = arc.get_arc_center()

    # Determine rotation start point and direction from the axis
    if np.array_equal(axis, OUT):  # counter-clockwise
        draw_arc = arc  # use the original arc
        rotation_start = start_point
        total_angle = arc.get_angle()
    else:  # clockwise (axis=IN)
        # Create a new arc with the opposite direction
        draw_arc = Arc(
            start_angle=angle_of_vector(end_point - center),
            angle=-arc.get_angle(),  # negative angle means opposite direction
            radius=np.linalg.norm(end_point - center),
            arc_center=center,
            color=arc.get_color(),
            stroke_width=arc.get_stroke_width(),
        )
        rotation_start = end_point
        total_angle = -arc.get_angle()

    # Create the moving-dot marker
    moving_dot = Dot(point=rotation_start)

    # Create a dashed line from the centre to the moving dot
    radius_line = DashedLine(center, rotation_start)

    # Compute the actual arc radius and start angle
    r = np.linalg.norm(rotation_start - center)
    start_angle = angle_of_vector(rotation_start - center)

    # Create a progress tracker
    progress = ValueTracker(0)

    # Update the moving-dot position
    moving_dot.add_updater(
        lambda d: d.move_to(
            center
            + r
            * np.array(
                [
                    np.cos(start_angle + progress.get_value() * total_angle),
                    np.sin(start_angle + progress.get_value() * total_angle),
                    0,
                ]
            )
        )
    )

    # Update the radius line
    radius_line.add_updater(
        lambda l: l.become(DashedLine(center, moving_dot.get_center()))
    )

    # Add all elements to the scene
    scene.add(moving_dot, radius_line)

    # Play the arc creation and dot rotation in sync
    scene.play(
        Create(draw_arc, rate_func=linear),  # use the adjusted arc
        progress.animate.set_value(1),
        run_time=run_time,
        rate_func=linear,
    )

    # Clear updaters
    moving_dot.clear_updaters()
    radius_line.clear_updaters()

    # Remove temporary elements
    scene.remove(moving_dot, radius_line)


class TypeWriter(Animation):
    """Typewriter effect animation.

    Reveals the content of a :class:`~manim.mobject.text.text_mobject.Text` object character by
    character, simulating a typewriter.  The total run time is automatically
    calculated from the character count and *interval* unless an explicit
    ``run_time`` is passed in ``kwargs``.

    .. inheritance-diagram:: manim_extensions.animations.TypeWriter
       :parts: 1

    Parameters
    ----------
    mobject : :class:`~manim.mobject.text.text_mobject.Text`
        The ``Text`` object to animate.
    interval : float, optional
        Display interval between consecutive characters in seconds.
        Defaults to ``2``.
    **kwargs
        Additional keyword arguments forwarded to :class:`~manim.animation.animation.Animation`.

    Attributes
    ----------
    interval : float
        The stored interval between characters.
    char_count : int
        Number of characters in *mobject*.

    Examples
    --------

    .. manim:: TypeWriterDocExample

       from manim import *
       from manim_extensions import TypeWriter

       class TypeWriterDocExample(Scene):
           def construct(self):
               text = Text("Hello World")
               self.play(TypeWriter(text, interval=0.1))
               self.wait()
    """

    def __init__(self, mobject: Text, interval: float = 2, **kwargs) -> None:
        assert isinstance(mobject, Text), "TypeWriter only supports Text mobjects."
        self.interval = interval
        self.char_count = len(mobject.submobjects)

        # Automatically compute run_time
        if "run_time" not in kwargs:
            kwargs["run_time"] = self.char_count * self.interval

        super().__init__(mobject, **kwargs)

    def interpolate_mobject(self, alpha: float) -> Text:
        """Set the visible characters based on the animation progress *alpha*.

        This method is called internally by Manim during the animation.  It
        reveals characters one by one as *alpha* goes from ``0`` to ``1``.

        Examples
        --------
        """
        current_index = int(alpha * self.char_count)
        for i, char in enumerate(self.mobject.submobjects):
            char.set_opacity(1 if i < current_index else 0)
        return self.mobject


# ---------------------------------------------------------------------------
# Ported from manim-kindergarten/manim_sandbox
#   <https://github.com/manim-kindergarten/manim_sandbox>
# Individual original authors are noted on each function / class.
# ---------------------------------------------------------------------------

import random

from manim.animation.transform import Restore
from manim.utils.bezier import interpolate
from manim.utils.rate_functions import smooth, linear, rush_into


# --- Rate functions ------------------------------------------------


def easeOutBounce(t: float) -> float:
    """Bounce easing that starts fast and bounces as it approaches ``1``.

    .. note::

        Adapted from `manim_sandbox
        <https://github.com/manim-kindergarten/manim_sandbox>`_ (``utils/functions/calculation.py``).
        Original author: @pdcxs.

    Args:
        t: Progress in ``[0, 1]``.

    Returns:
        The eased value in ``[0, 1]``.

    Examples
    --------


    .. manim:: EaseOutBounceExample

       from manim import *
       from manim_extensions import easeOutBounce

       class EaseOutBounceExample(Scene):
           def construct(self):
               dot = Dot()
               self.add(dot)
               self.play(dot.animate(rate_func=easeOutBounce).shift(RIGHT * 5), run_time=3)
               self.wait()
    """
    if t < 1 / 2.75:
        return 7.5625 * t * t
    elif t < 2 / 2.75:
        c = t - 1.5 / 2.75
        return 7.5625 * c * c + 0.75
    elif t < 2.5 / 2.75:
        c = t - 2.25 / 2.75
        return 7.5625 * c * c + 0.9375
    else:
        c = t - 2.625 / 2.75
        return 7.5625 * c * c + 0.984375


def easeInBounce(t: float) -> float:
    """Bounce easing that accelerates into the bounce.

    .. note::

        Adapted from `manim_sandbox
        <https://github.com/manim-kindergarten/manim_sandbox>`_ (``utils/functions/calculation.py``).
        Original author: @pdcxs.

    Args:
        t: Progress in ``[0, 1]``.

    Returns:
        The eased value in ``[0, 1]``.

    Examples
    --------


    .. manim:: EaseInBounceExample

       from manim import *
       from manim_extensions import easeInBounce

       class EaseInBounceExample(Scene):
           def construct(self):
               dot = Dot()
               self.add(dot)
               self.play(dot.animate(rate_func=easeInBounce).shift(RIGHT * 5), run_time=3)
               self.wait()
    """
    return 1 - easeOutBounce(1 - t)


def easeInOutBounce(t: float) -> float:
    """Mirrored ease-in/out bounce.

    .. note::

        Adapted from `manim_sandbox
        <https://github.com/manim-kindergarten/manim_sandbox>`_ (``utils/functions/calculation.py``).
        Original author: @pdcxs.

    Args:
        t: Progress in ``[0, 1]``.

    Returns:
        The eased value in ``[0, 1]``.

    Examples
    --------


    .. manim:: EaseInOutBounceExample

       from manim import *
       from manim_extensions import easeInOutBounce

       class EaseInOutBounceExample(Scene):
           def construct(self):
               dot = Dot()
               self.add(dot)
               self.play(dot.animate(rate_func=easeInOutBounce).shift(RIGHT * 5), run_time=3)
               self.wait()
    """
    if t < 0.5:
        return easeInBounce(2 * t)
    return easeOutBounce(2 * t - 1)


def easeOutElastic(t: float) -> float:
    """Elastic easing that overshoots and oscillates towards ``1``.

    .. note::

        Adapted from `manim_sandbox
        <https://github.com/manim-kindergarten/manim_sandbox>`_ (``utils/functions/calculation.py``).
        Original author: @pdcxs.

        Because this function can return values greater than ``1`` it should not be
        used with animations that sample ``points_from_proportion`` (e.g.
        ``MoveAlongPath``).

    Args:
        t: Progress in ``[0, 1]``.

    Returns:
        The eased value, which may exceed ``1`` near the end.

    Examples
    --------


    .. manim:: EaseOutElasticExample

       from manim import *
       from manim_extensions import easeOutElastic

       class EaseOutElasticExample(Scene):
           def construct(self):
               dot = Dot()
               self.add(dot)
               self.play(dot.animate(rate_func=easeOutElastic).shift(RIGHT * 5), run_time=3)
               self.wait()
    """
    s, a = 1.70158, 1
    if t == 0 or t == 1:
        return t
    p = 0.3
    if a < 1:
        a, s = 1, p / 4
    else:
        s = p / (2 * np.pi) * np.arcsin(1 / a)
    return a * pow(2, -10 * t) * np.sin((t - s) * (2 * np.pi) / p) + 1


# --- Random-order animations ---------------------------------------


class WriteRandom(LaggedStart):
    """Write the submobjects of *mobject* one by one in random order.

    .. note::

        Adapted from `manim_sandbox
        <https://github.com/manim-kindergarten/manim_sandbox>`_ (``utils/animations/RandomScene.py``).
        Original author: widcardw (style popularised by @贝多芬).

    Parameters
    ----------
    mobject : :class:`~manim.mobject.mobject.Mobject`
        The mobject whose submobjects are written.
    lag_ratio : float, optional
        Delay between consecutive submobjects.  Defaults to ``0.1``.
    run_time : float, optional
        Total run time in seconds.  Defaults to ``2.5``.
    **kwargs
        Additional keyword arguments forwarded to :class:`~manim.animation.composition.LaggedStart`.

    Examples
    --------

    .. manim:: WriteRandomDocExample

       from manim import *
       from manim_extensions import WriteRandom

       class WriteRandomDocExample(Scene):
           def construct(self):
               text = Text("Hello").scale(2)
               self.add(text)
               self.play(WriteRandom(text, run_time=2))
    """

    def __init__(self, mobject, lag_ratio: float = 0.1, run_time: float = 2.5, **kwargs):
        indices = list(range(len(mobject.submobjects)))
        random.shuffle(indices)
        super().__init__(
            *[Write(mobject[i], rate_func=linear) for i in indices],
            lag_ratio=lag_ratio,
            run_time=run_time,
            **kwargs,
        )


class ReversedWrite(LaggedStart):
    """Write the submobjects of *mobject* in reverse order.

    .. note::

        Adapted from `manim_sandbox
        <https://github.com/manim-kindergarten/manim_sandbox>`_ (``utils/animations/RandomScene.py``).
        Original author: widcardw (style popularised by @贝多芬).

    Parameters
    ----------
    mobject : :class:`~manim.mobject.mobject.Mobject`
        The mobject whose submobjects are written.
    lag_ratio : float, optional
        Delay between consecutive submobjects.  Defaults to ``0.1``.
    run_time : float, optional
        Total run time in seconds.  Defaults to ``2.0``.
    **kwargs
        Additional keyword arguments forwarded to :class:`~manim.animation.composition.LaggedStart`.

    Examples
    --------


    .. manim:: ReversedWriteDocExample

       from manim import *
       from manim_extensions import ReversedWrite

       class ReversedWriteDocExample(Scene):
           def construct(self):
               mob = Text("Hello")
               self.play(ReversedWrite(mob, run_time=3))
               self.wait()
    """

    def __init__(self, mobject, lag_ratio: float = 0.1, run_time: float = 2.0, **kwargs):
        indices = list(range(len(mobject.submobjects) - 1, -1, -1))
        super().__init__(
            *[Write(mobject[i], rate_func=linear) for i in indices],
            lag_ratio=lag_ratio,
            run_time=run_time,
            **kwargs,
        )


class UnWrite(Write):
    """Reverse a :class:`~manim.animation.creation.Write`, then remove the mobject.

    .. note::

        Adapted from `manim_sandbox
        <https://github.com/manim-kindergarten/manim_sandbox>`_ (``utils/animations/RandomScene.py``).
        Original author: widcardw.

    Parameters
    ----------
    mobject : :class:`~manim.mobject.mobject.Mobject`
        The mobject to un-write.
    **kwargs
        Additional keyword arguments forwarded to :class:`~manim.animation.creation.Write`.

    Examples
    --------


    .. manim:: UnWriteDocExample

       from manim import *
       from manim_extensions import UnWrite

       class UnWriteDocExample(Scene):
           def construct(self):
               mob = Text("Hello")
               self.play(Write(mob))
               self.play(UnWrite(mob))
               self.wait()
    """

    def __init__(self, mobject, **kwargs):
        kwargs.setdefault("rate_func", lambda t: smooth(1 - t))
        kwargs.setdefault("remover", True)
        super().__init__(mobject, **kwargs)


class FadeInRandom(LaggedStart):
    """Fade in the submobjects of *mobject* one by one in random order.

    .. note::

        Adapted from `manim_sandbox
        <https://github.com/manim-kindergarten/manim_sandbox>`_ (``utils/animations/RandomScene.py``).
        Original author: widcardw.

    Parameters
    ----------
    mobject : :class:`~manim.mobject.mobject.Mobject`
        The mobject whose submobjects are faded in.
    lag_ratio : float, optional
        Delay between consecutive submobjects.  Defaults to ``0.08``.
    run_time : float, optional
        Total run time in seconds.  Defaults to ``1.5``.
    **kwargs
        Additional keyword arguments forwarded to :class:`~manim.animation.composition.LaggedStart`.

    Examples
    --------


    .. manim:: FadeInRandomDocExample

       from manim import *
       from manim_extensions import FadeInRandom

       class FadeInRandomDocExample(Scene):
           def construct(self):
               mob = Text("Hello")
               self.play(FadeInRandom(mob, run_time=3))
               self.wait()
    """

    def __init__(self, mobject, lag_ratio: float = 0.08, run_time: float = 1.5, **kwargs):
        indices = list(range(len(mobject.submobjects)))
        random.shuffle(indices)
        super().__init__(
            *[FadeIn(mobject[i], rate_func=linear) for i in indices],
            lag_ratio=lag_ratio,
            run_time=run_time,
            **kwargs,
        )


class FadeOutRandom(LaggedStart):
    """Fade out the submobjects of *mobject* one by one in random order.

    .. note::

        Adapted from `manim_sandbox
        <https://github.com/manim-kindergarten/manim_sandbox>`_ (``utils/animations/RandomScene.py``).
        Original author: widcardw.

    Parameters
    ----------
    mobject : :class:`~manim.mobject.mobject.Mobject`
        The mobject whose submobjects are faded out.
    lag_ratio : float, optional
        Delay between consecutive submobjects.  Defaults to ``0.08``.
    run_time : float, optional
        Total run time in seconds.  Defaults to ``1.5``.
    **kwargs
        Additional keyword arguments forwarded to :class:`~manim.animation.composition.LaggedStart`.

    Examples
    --------


    .. manim:: FadeOutRandomDocExample

       from manim import *
       from manim_extensions import FadeOutRandom

       class FadeOutRandomDocExample(Scene):
           def construct(self):
               mob = Text("Hello")
               self.add(mob)
               self.play(FadeOutRandom(mob, run_time=2))
               self.wait()
    """

    def __init__(self, mobject, lag_ratio: float = 0.08, run_time: float = 1.5, **kwargs):
        indices = list(range(len(mobject.submobjects)))
        random.shuffle(indices)
        super().__init__(
            *[FadeOut(mobject[i], rate_func=linear) for i in indices],
            lag_ratio=lag_ratio,
            run_time=run_time,
            **kwargs,
        )


class GrowRandom(LaggedStart):
    """Grow the submobjects of *mobject* from their centres in random order.

    .. note::

        Adapted from `manim_sandbox
        <https://github.com/manim-kindergarten/manim_sandbox>`_ (``utils/animations/RandomScene.py``).
        Original author: widcardw.

    Parameters
    ----------
    mobject : :class:`~manim.mobject.mobject.Mobject`
        The mobject whose submobjects are grown.
    lag_ratio : float, optional
        Delay between consecutive submobjects.  Defaults to ``0.1``.
    run_time : float, optional
        Total run time in seconds.  Defaults to ``2.0``.
    **kwargs
        Additional keyword arguments forwarded to :class:`~manim.animation.composition.LaggedStart`.

    Examples
    --------


    .. manim:: GrowRandomDocExample

       from manim import *
       from manim_extensions import GrowRandom

       class GrowRandomDocExample(Scene):
           def construct(self):
               mob = Text("Hello")
               self.play(GrowRandom(mob, run_time=2))
               self.wait()
    """

    def __init__(self, mobject, lag_ratio: float = 0.1, run_time: float = 2.0, **kwargs):
        indices = list(range(len(mobject.submobjects)))
        random.shuffle(indices)
        super().__init__(
            *[GrowFromCenter(mobject[i], rate_func=linear) for i in indices],
            lag_ratio=lag_ratio,
            run_time=run_time,
            **kwargs,
        )


# --- Emphasis animations -------------------------------------------


class PassingRectangle(Animation):
    """A filled rectangle that sweeps across *mobject* from left to right.

    .. note::

        Adapted from `manim_sandbox
        <https://github.com/manim-kindergarten/manim_sandbox>`_ (``utils/animations/paperclip.py``).
        Original author: @鹤翔万里.

    Parameters
    ----------
    mobject : :class:`~manim.mobject.mobject.Mobject`
        The mobject the rectangle sweeps across.
    color : :class:`~manim.utils.color.core.ManimColor`, optional
        Fill colour of the sweep.  Defaults to ``RED``.
    buff : float, optional
        Extra width/height around *mobject*.  Defaults to ``0.05``.
    fill_opacity : float, optional
        Fill opacity of the sweep.  Defaults to ``0.6``.
    run_time : float, optional
        Duration in seconds.  Defaults to ``1.5``.
    **kwargs
        Additional keyword arguments forwarded to :class:`~manim.animation.animation.Animation`.

    Examples
    --------

    .. manim:: PassingRectangleDocExample

       from manim import *
       from manim_extensions import PassingRectangle

       class PassingRectangleDocExample(Scene):
           def construct(self):
               rect = SurroundingRectangle(Text("Hi").scale(2))
               self.add(rect)
               self.play(PassingRectangle(rect, run_time=2))
    """

    def __init__(
        self,
        mobject,
        color=RED,
        buff: float = 0.05,
        fill_opacity: float = 0.6,
        run_time: float = 1.5,
        **kwargs,
    ):
        self.mob_left = mobject.get_left() + buff * LEFT
        self.mob_right = mobject.get_right() + buff * RIGHT
        self.height = mobject.get_height() + 2 * buff
        self.color = color
        self.fill_opacity = fill_opacity
        rect = Rectangle(
            width=float(np.linalg.norm(self.mob_right - self.mob_left)),
            height=self.height,
            color=color,
            fill_opacity=fill_opacity,
        )
        rect.move_to((self.mob_left + self.mob_right) / 2)
        super().__init__(rect, run_time=run_time, rate_func=linear, **kwargs)

    def interpolate_mobject(self, alpha: float) -> None:
        """Slide and resize the sweep rectangle based on *alpha*."""
        a_left = rush_into(alpha)
        a_right = 1 - rush_into(1 - alpha)
        left = interpolate(self.mob_left, self.mob_right, a_left)
        right = interpolate(self.mob_left, self.mob_right, a_right)
        self.mobject.become(
            Rectangle(
                width=float(np.linalg.norm(right - left)),
                height=self.height,
                color=self.color,
                fill_opacity=self.fill_opacity,
            ).move_to((left + right) / 2)
        )


class LaggedCreation(Animation):
    """Create a mobject with a custom start/end partial-reveal lag.

    .. note::

        Adapted from `manim_sandbox
        <https://github.com/manim-kindergarten/manim_sandbox>`_ (``utils/animations/paperclip.py``).
        Original author: @鹤翔万里.

    Parameters
    ----------
    mobject : :class:`~manim.mobject.mobject.Mobject`
        The mobject to reveal.
    lag_ratio : float, optional
        Fraction of the mobject revealed per unit time.  Defaults to ``1.0``.
    start_ratio : float, optional
        Fraction of the mobject visible at the start.  Defaults to ``1/6``.
    run_time : float, optional
        Duration in seconds.  Defaults to ``1.5``.
    **kwargs
        Additional keyword arguments forwarded to :class:`~manim.animation.animation.Animation`.

    Examples
    --------


    .. manim:: LaggedCreationDocExample

       from manim import *
       from manim_extensions import LaggedCreation

       class LaggedCreationDocExample(Scene):
           def construct(self):
               mob = Text("Hello")
               self.play(LaggedCreation(mob, run_time=3))
               self.wait()
    """

    def __init__(
        self,
        mobject,
        lag_ratio: float = 1.0,
        start_ratio: float = 1 / 6,
        run_time: float = 1.5,
        **kwargs,
    ):
        self.lag_ratio = lag_ratio
        self.start_ratio = start_ratio
        super().__init__(mobject, run_time=run_time, rate_func=linear, **kwargs)

    def get_bounds(self, alpha: float):
        ratio = self.start_ratio
        a = interpolate((1 - ratio) / 4, 1 / 2 + ratio / 4, alpha)
        b = interpolate((1 - ratio) / 4, 3 / 2 + ratio / 4, alpha)
        return a, b

    def interpolate_submobject(self, submobject, starting_submobject, alpha: float) -> None:
        """Reveal *submobject* between the computed partial bounds."""
        a, b = self.get_bounds(alpha)
        submobject.pointwise_become_partial(starting_submobject, a, b)
        if b > 1:
            left_part = starting_submobject.copy().pointwise_become_partial(starting_submobject, 0, b - 1)
            submobject.append_points(left_part.get_points())


class HighLightWithLines(AnimationGroup):
    """Draw two horizontal lines and expand a rectangle around *mobject*.

    .. note::

        Adapted from `manim_sandbox
        <https://github.com/manim-kindergarten/manim_sandbox>`_ (``utils/animations/paperclip.py``).
        Original author: @鹤翔万里.

    Parameters
    ----------
    mobject : :class:`~manim.mobject.mobject.Mobject`
        The mobject to highlight.
    color : :class:`~manim.utils.color.core.ManimColor`, optional
        Colour of the lines and rectangle.  Defaults to ``RED``.
    buff : float, optional
        Distance of the lines / rectangle from *mobject*.  Defaults to ``0.05``.
    rec_opacity : float, optional
        Fill opacity of the rectangle.  Defaults to ``0.5``.
    run_time : float, optional
        Duration in seconds.  Defaults to ``1.0``.
    **kwargs
        Additional keyword arguments forwarded to :class:`~manim.animation.composition.AnimationGroup`.

    Examples
    --------


    .. manim:: HighLightWithLinesDocExample

       from manim import *
       from manim_extensions import HighLightWithLines

       class HighLightWithLinesDocExample(Scene):
           def construct(self):
               mob = Text("Hello", color=WHITE)
               self.add(mob)
               self.play(HighLightWithLines(mob, run_time=2))
               self.wait()
    """

    def __init__(
        self,
        mobject,
        color=RED,
        buff: float = 0.05,
        rec_opacity: float = 0.5,
        run_time: float = 1.0,
        **kwargs,
    ):
        line_up = Line(color=color, stroke_width=2).set_width(config.frame_width)
        line_up.next_to(mobject, UP, buff=buff)
        line_down = Line(color=color, stroke_width=2).set_width(config.frame_width)
        line_down.next_to(mobject, DOWN, buff=buff)
        self.lines = VGroup(line_up, line_down)

        rectangle = SurroundingRectangle(
            mobject, color=color, fill_opacity=rec_opacity, stroke_width=0, buff=buff
        )
        rectangle.save_state()
        rectangle.stretch(0, 0, about_edge=LEFT).set_fill(opacity=0)

        super().__init__(
            Create(self.lines, lag_ratio=0),
            Restore(rectangle),
            run_time=run_time,
            **kwargs,
        )


class UnHighLightWithLines(AnimationGroup):
    """Undo :class:`HighLightWithLines`: fade out the lines and rectangle.

    .. note::

        Adapted from `manim_sandbox
        <https://github.com/manim-kindergarten/manim_sandbox>`_ (``utils/animations/paperclip.py``).
        Original author: @鹤翔万里.

    Parameters
    ----------
    mobject : :class:`~manim.mobject.mobject.Mobject`
        The mobject whose highlight is removed.
    color : :class:`~manim.utils.color.core.ManimColor`, optional
        Colour used for the lines and rectangle.  Defaults to ``RED``.
    buff : float, optional
        Distance of the lines / rectangle from *mobject*.  Defaults to ``0.05``.
    rec_opacity : float, optional
        Fill opacity of the rectangle.  Defaults to ``0.5``.
    run_time : float, optional
        Duration in seconds.  Defaults to ``1.0``.
    **kwargs
        Additional keyword arguments forwarded to :class:`~manim.animation.composition.AnimationGroup`.

    Examples
    --------


    .. manim:: UnHighLightWithLinesDocExample

       from manim import *
       from manim_extensions import UnHighLightWithLines

       class UnHighLightWithLinesDocExample(Scene):
           def construct(self):
               mob = Text("Hello", color=WHITE)
               self.add(mob)
               self.play(UnHighLightWithLines(mob, run_time=2))
               self.wait()
    """

    def __init__(
        self,
        mobject,
        color=RED,
        buff: float = 0.05,
        rec_opacity: float = 0.5,
        run_time: float = 1.0,
        **kwargs,
    ):
        line_up = Line(color=color, stroke_width=2).set_width(config.frame_width)
        line_up.next_to(mobject, UP, buff=buff)
        line_down = Line(color=color, stroke_width=2).set_width(config.frame_width)
        line_down.next_to(mobject, DOWN, buff=buff)
        lines = VGroup(line_up, line_down)

        rectangle = SurroundingRectangle(
            mobject, color=color, fill_opacity=rec_opacity, stroke_width=0, buff=buff
        )

        super().__init__(
            Uncreate(lines, lag_ratio=0),
            FadeOut(rectangle),
            run_time=run_time,
            **kwargs,
        )

from manim import *
from .seq_actor import SeqActor
from .seq_object import SeqObject

class SeqAction(AnimationGroup):
    """Animation helper for sequence-diagram interactions between actors.

    Examples
    --------
    .. manim:: SeqActionExample
       :save_last_frame:

       from manim import *
       from manim_extensions.sequence_diagram.seq_actor import SeqActor
       from manim_extensions.sequence_diagram.seq_action import SeqAction

       class SeqActionExample(Scene):
           def construct(self):
               a1 = SeqActor("Alice").shift(LEFT * 2)
               a2 = SeqActor("Bob").shift(RIGHT * 2)
               self.add(a1, a2)
"""

    @classmethod
    def introduce_actors(
        cls,
        *actors: SeqActor
    ):
        """Fade in the provided actors as a grouped timeline.

    Parameters
    ----------
    actors : SeqActor
    Actors processed by this operation.
    """
        group = Group(*actors).move_to(ORIGIN).arrange(buff=0.25)
        animation = FadeIn(group, shift=DOWN, run_time=0.5)
        yield animation

    @classmethod
    def subject_gives_gift_to_target(
        cls,
        subject: SeqActor,
        gift: SeqObject,
        target: SeqActor
    ):
        """Animate an object moving from one actor to another in the diagram.

    Parameters
    ----------
    subject : SeqActor
        The actor sending the gift.
    gift : SeqObject
        The object being passed between actors.
    target : SeqActor
        The actor receiving the gift.

    Yields
    ------
    Animation
        A sequence of animations to be played by the scene.
    """
        if subject is target:
            # We don't use Succession here because
            # we need sub_arr to be different lines
            # than obj_arr, however, they wind up
            # going to the same place unless the anime
            # has already run, thus we just yield instead
            sub_arr, sub_ani = subject.time_elapse()
            yield sub_ani
            obj_arr, obj_ani = target.time_elapse()
            yield obj_ani
        else:
            sub_arr, sub_ani = subject.time_elapse()
            obj_arr, obj_ani = target.time_elapse()
            yield AnimationGroup(sub_ani, obj_ani)
        act_start = Dot(sub_arr.get_end(), radius=0.05)
        act_end = Dot(obj_arr.get_end(), radius=0.05)
        is_move_left = (obj_arr.get_end() - sub_arr.get_end())[0] > 0.0
        gift.move_to(act_start.get_center(), aligned_edge=(RIGHT if is_move_left else LEFT))

        if subject is target:
            iobj_planned_path = CurvedArrow(
                start_point=act_start.get_center(),
                end_point=act_end.get_center(),
                stroke_width=1
            )
        else:
            iobj_planned_path = Arrow(
                start=act_start.get_center(),
                end=act_end.get_center(),
                buff=0,
                stroke_width=1,
                max_tip_length_to_length_ratio=0.2
            )
        iobj_moved_path = TracedPath(gift.get_center)
        mid_point = utils.space_ops.midpoint(act_start.get_center(), act_end.get_center())
        post_move_gift_label = gift.create_obj_label(font_size=16).move_to(mid_point, aligned_edge=UP)

        yield Succession(
            FadeIn(gift),
            Transform(gift, act_start, run_time=0.4),
            Create(iobj_moved_path, run_time=0.1),
            MoveAlongPath(gift, iobj_planned_path),
            AnimationGroup(
                FadeIn(iobj_planned_path, run_time=0.2),
                FadeIn(post_move_gift_label)
            )
        )
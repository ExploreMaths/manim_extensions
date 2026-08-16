# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


from manim_extensions.sequence_diagram import SeqAction, SeqActor, SeqObject


def test_sequence_visuals():
    actor = SeqActor("Alice")
    obj = SeqObject("Order")
    assert actor.actor_name == "Alice"
    assert obj.obj_name == "Order"
    assert actor.latest_timedot is not None

    animation = list(SeqAction.introduce_actors(actor))
    assert len(animation) == 1

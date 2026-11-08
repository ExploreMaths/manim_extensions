# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the sequence-diagram gift transfer action."""

import pytest

from manim_extensions.sequence_diagram.seq_action import SeqAction
from manim_extensions.sequence_diagram.seq_actor import SeqActor
from manim_extensions.sequence_diagram.seq_object import SeqObject


@pytest.fixture()
def actors():
    return SeqActor(name="client"), SeqActor(name="server")


def test_introduce_actors_builds_animations(actors):
    animations = list(SeqAction.introduce_actors(*actors))

    assert len(animations) >= 1


def test_subject_gives_gift_to_target_builds_animations(actors):
    subject, target = actors

    animations = list(
        SeqAction.subject_gives_gift_to_target(
            subject, SeqObject(name="payload"), target
        )
    )

    assert len(animations) >= 1


def test_gift_transfer_between_same_actor_pairs_twice(actors):
    subject, target = actors

    SeqAction.subject_gives_gift_to_target(subject, SeqObject(name="one"), target)
    animations = list(
        SeqAction.subject_gives_gift_to_target(target, SeqObject(name="two"), subject)
    )

    assert len(animations) >= 1

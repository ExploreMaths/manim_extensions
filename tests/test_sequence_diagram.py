# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the sequence_diagram module."""

import pytest
from manim import VGroup, Animation, FadeIn

from manim_extensions.sequence_diagram import SeqActor, SeqObject, SeqAction


class TestSeqObject:
    def test_basic_construction(self):
        """SeqObject should be created with a name."""
        obj = SeqObject("Request")
        assert isinstance(obj, VGroup)
        assert obj.obj_name == "Request"

    def test_custom_font_size(self):
        """SeqObject should accept custom font_size."""
        obj = SeqObject("Data", font_size=24)
        assert isinstance(obj, VGroup)
        assert obj.obj_name == "Data"

    def test_create_obj_label(self):
        """SeqObject.create_obj_label should return a Text mobject."""
        from manim import Text
        obj = SeqObject("Test")
        label = obj.create_obj_label(font_size=20)
        assert isinstance(label, Text)


class TestSeqActor:
    def setup_method(self):
        """Reset the class-level all_actors list before each test."""
        SeqActor.all_actors = list()

    def test_basic_construction(self):
        """SeqActor should be created with a name."""
        actor = SeqActor("Alice")
        assert isinstance(actor, VGroup)
        assert actor.actor_name == "Alice"

    def test_latest_timedot_property(self):
        """SeqActor should expose its latest timedot."""
        actor = SeqActor("Bob")
        assert actor.latest_timedot is not None
        # Initially there is one timedot
        assert len(actor.actor_timedots) == 1

    def test_get_time_depth_initial(self):
        """SeqActor.get_time_depth should return 0 initially."""
        actor = SeqActor("Charlie")
        depth = actor.get_time_depth()
        assert isinstance(depth, int)
        assert depth == 0

    def test_all_actors_registration(self):
        """SeqActor should register itself in all_actors class list."""
        _ = SeqActor("Alice")
        _ = SeqActor("Bob")
        assert len(SeqActor.all_actors) == 2

    def test_get_deepest_actor(self):
        """SeqActor.get_deepest_actor should return the deepest actor."""
        alice = SeqActor("Alice")
        bob = SeqActor("Bob")
        deepest = SeqActor.get_deepest_actor()
        assert deepest is not None
        # Both start at same depth, should return one of them
        assert deepest in (alice, bob)


class TestSeqAction:
    def setup_method(self):
        """Reset the class-level all_actors list before each test."""
        SeqActor.all_actors = list()

    def test_introduce_actors_yields_animation(self):
        """SeqAction.introduce_actors should yield a FadeIn animation."""
        alice = SeqActor("Alice")
        bob = SeqActor("Bob")
        animations = list(SeqAction.introduce_actors(alice, bob))
        assert len(animations) == 1
        assert isinstance(animations[0], Animation)

    def test_introduce_single_actor(self):
        """SeqAction.introduce_actors should work with a single actor."""
        actor = SeqActor("Solo")
        animations = list(SeqAction.introduce_actors(actor))
        assert len(animations) == 1
        assert isinstance(animations[0], Animation)

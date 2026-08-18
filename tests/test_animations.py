# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT



from manim import *
from manim_extensions.animations import TypeWriter


class TestTypeWriter:
    def test_is_animation_subclass(self):
        text = Text("Hello")
        anim = TypeWriter(text, interval=0.5)
        assert isinstance(anim, Animation)

    def test_interval_storage(self):
        text = Text("ABC")
        anim = TypeWriter(text, interval=0.3)
        assert anim.interval == 0.3
        assert anim.char_count == len(text.submobjects)

    def test_run_time_auto_calculated(self):
        text = Text("ABCD")
        anim = TypeWriter(text, interval=0.5)
        expected_run_time = len(text.submobjects) * 0.5
        assert anim.run_time == expected_run_time


# --- Ported from manim-kindergarten/manim_sandbox -------------------

import pytest

from manim_extensions.animations import (
    easeInBounce,
    easeOutBounce,
    easeInOutBounce,
    easeOutElastic,
    WriteRandom,
    ReversedWrite,
    FadeInRandom,
    FadeOutRandom,
    GrowRandom,
    PassingRectangle,
    LaggedCreation,
    HighLightWithLines,
    UnHighLightWithLines,
)


class TestRateFunctions:
    def test_bounce_within_unit_range(self):
        for f in (easeInBounce, easeOutBounce, easeInOutBounce):
            for t in (0.0, 0.25, 0.5, 0.75, 1.0):
                v = f(t)
                assert 0.0 <= v <= 1.0

    def test_elastic_endpoints(self):
        assert easeOutElastic(0.0) == 0.0
        assert easeOutElastic(1.0) == 1.0

    def test_inverse_bounce(self):
        assert easeInBounce(0.5) == pytest.approx(1.0 - easeOutBounce(0.5))


_RANDOM_ANIMS = [WriteRandom, ReversedWrite, FadeInRandom, FadeOutRandom, GrowRandom]


class TestRandomAnimations:
    def test_are_animations(self):
        with tempconfig({"disable_caching": True}):
            text = Text("ABCD")
            for ctor in _RANDOM_ANIMS:
                assert isinstance(ctor(text), Animation)


class TestPassingRectangle:
    def test_is_animation(self):
        with tempconfig({"disable_caching": True}):
            anim = PassingRectangle(Square())
            assert isinstance(anim, Animation)


class TestLaggedCreation:
    def test_is_animation(self):
        with tempconfig({"disable_caching": True}):
            anim = LaggedCreation(Square())
            assert isinstance(anim, Animation)


class TestHighLightWithLines:
    def test_is_animation(self):
        with tempconfig({"disable_caching": True}):
            anim = HighLightWithLines(Text("Hi"))
            assert isinstance(anim, Animation)


class TestUnHighLightWithLines:
    def test_is_animation(self):
        with tempconfig({"disable_caching": True}):
            anim = UnHighLightWithLines(Text("Hi"))
            assert isinstance(anim, Animation)

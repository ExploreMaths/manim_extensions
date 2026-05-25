from manim import Text, Animation

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

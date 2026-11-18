from manim_extensions.pymunk.utils.tools_func import (
    get_moment_for_box,
    get_moment_for_circle,
    get_moment_for_line,
    get_moment_for_poly,
)


def test_moment_helpers_delegate_to_pymunk():
    assert get_moment_for_box(2.0, 1.0, 2.0) > 0
    assert get_moment_for_circle(2.0, 0.0, 1.0) > 0
    assert get_moment_for_poly(2.0, [(0, 0), (1, 0), (0, 1)]) > 0
    assert get_moment_for_line(2.0, (0, 0), (1, 0), 0.1) > 0

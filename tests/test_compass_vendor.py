import numpy as np
from manim import PI, RIGHT, WHITE, RED, YELLOW

from manim_extensions.compass import Compass


def test_compass_constructor_and_fields():
    compass = Compass()

    assert compass.span == 1.5
    assert compass.head_color == WHITE
    assert compass.niddle_color == RED
    assert compass.pen_color == YELLOW
    assert compass.leg_length == 3.1
    assert compass.leg_width == 0.12
    assert compass.r == 0.2
    assert hasattr(compass, "theta")
    assert compass.niddle_tip is not None
    assert compass.pen_tip is not None
    assert compass.head is not None
    assert compass.get_niddle_tip().shape == (3,)
    assert compass.get_pen_tip().shape == (3,)
    assert np.isfinite(compass.get_span())


def test_compass_mutation_helpers():
    compass = Compass()
    target = np.array([1.0, 2.0, 0.0])

    moved = compass.move_niddle_tip_to(target)
    assert moved is compass
    assert np.allclose(compass.get_niddle_tip(), target)

    rotated = compass.rotate_about_niddle_tip(PI / 4)
    assert rotated is compass
    assert compass.get_niddle_tip().shape == (3,)

    reversed_compass = compass.reverse_tip()
    assert reversed_compass is compass
    assert np.isfinite(compass.get_span())

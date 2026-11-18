import numpy as np
from manim import Circle, VMobject

from manim_extensions.mobject_svg.svg import (
    _transform_points_pre_display,
    create_svg_from_vmobject,
)


def test_nan_points_are_sanitized():
    points = np.array([[np.nan, 0.0, 0.0]])
    assert np.all(_transform_points_pre_display(points) == 0)


def test_empty_vmobject_and_default_filename():
    path = create_svg_from_vmobject(VMobject())
    assert path is not None
    path = create_svg_from_vmobject(Circle())
    assert path is not None

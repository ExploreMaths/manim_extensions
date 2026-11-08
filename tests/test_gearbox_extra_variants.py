# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Extra gear variants: undercut-prone pinions, inner teeth and cut-outs."""

import pytest

from manim_extensions.gearbox.gear_mobjects.gear_mobject import Gear


@pytest.mark.parametrize(
    "kwargs",
    [
        dict(num_of_teeth=10),
        dict(num_of_teeth=8, profile_shift=-1),
        dict(num_of_teeth=6, profile_shift=-2),
        dict(num_of_teeth=20, inner_teeth=True),
        dict(num_of_teeth=24, cutout_teeth_num=6),
        dict(num_of_teeth=20, inner_teeth=True, cutout_teeth_num=5),
    ],
)
def test_gear_variants_construct(kwargs):
    gear = Gear(**kwargs)
    gear.rotate(0.3)

    assert len(gear.submobjects) >= 1

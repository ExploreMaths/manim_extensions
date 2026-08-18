# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


from manim import *
import shutil

import numpy as np

from manim_extensions.physics.optics.lenses import Lens
from manim_extensions.physics.rigid_mechanics.pendulum import MultiPendulum, Pendulum
from manim_extensions.physics.wave import LinearWave, RadialWave, StandingWave
from manim_extensions.tikz import Tikz


def test_physics_objects():
    lens = Lens(f=1.0, d=0.4)
    assert lens.f > 0
    assert lens.d == 0.4

    radial = RadialWave(ORIGIN)
    linear = LinearWave()
    standing = StandingWave()
    assert radial.sources is not None
    assert linear.wavelength > 0
    assert standing.amplitude > 0

    pendulum = Pendulum(length=1.5)
    multi = MultiPendulum(np.array([0.0, -1.0, 0.0]), np.array([0.0, -2.0, 0.0]))
    assert pendulum.length == 1.5
    assert len(multi.bobs) >= 2


def test_tikz_object():
    if shutil.which("latex") is not None:
        tikz = Tikz(r"\draw (0,0) circle (1);")
        assert tikz is not None

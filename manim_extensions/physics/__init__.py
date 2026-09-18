# SPDX-FileCopyrightText: 2024 Matheart
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


"""Physics utilities for Manim scenes.

This package contains tools for optics, electromagnetism, rigid mechanics, and
wave visualisations, all designed to be used directly in scene code.

"""

from .electromagnetism.electrostatics import *
from .electromagnetism.magnetostatics import *
from .optics.lenses import *
from .optics.rays import *
from .rigid_mechanics.pendulum import *
from .rigid_mechanics.rigid_mechanics import *
from .wave import *

__all__ = [
    "Charge",
    "ElectricField",
    "Lens",
    "LinearWave",
    "MagneticField",
    "MultiPendulum",
    "Pendulum",
    "RadialWave",
    "Ray",
    "Space",
    "SpaceScene",
    "StandingWave",
    "Wire",
    "get_angle",
    "get_shape",
]

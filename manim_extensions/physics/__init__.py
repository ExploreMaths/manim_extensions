# SPDX-FileCopyrightText: 2024 Matheart
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


"""Physics utilities for Manim scenes.

This package contains tools for optics, electromagnetism, rigid mechanics, and
wave visualisations, all designed to be used directly in scene code.

"""

from manim import *

from .electromagnetism.electrostatics import *
from .electromagnetism.magnetostatics import *
from .optics.lenses import *
from .optics.rays import *
from .rigid_mechanics.pendulum import *
from .rigid_mechanics.rigid_mechanics import *
from .wave import *
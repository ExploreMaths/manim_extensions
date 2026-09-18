# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Pymunk physics integration for Manim.

This module provides physics simulation capabilities using Pymunk,
including rigid body dynamics, constraints, and custom mobjects.

"""

__version__ = "1.2.0"

from .custom_mobjects import *
from .constraints import *
from .space import *

__all__ = [
    "Apple",
    "Gear",
    "SpaceScene",
    "VConstraint",
    "VDampedRotarySpring",
    "VDampedSpring",
    "VGearJoint",
    "VGrooveJoint",
    "VPinJoint",
    "VPivotJoint",
    "VRatchetJoint",
    "VRotaryLimitJoint",
    "VSimpleMotor",
    "VSlideJoint",
    "VSpace",
    "VSpring",
]
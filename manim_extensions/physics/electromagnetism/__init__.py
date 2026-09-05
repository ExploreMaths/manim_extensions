# SPDX-FileCopyrightText: 2024 Matheart
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Electromagnetism visualizations for Manim.

This module provides electromagnetism visualizations including electric and magnetic fields.

"""

from .electrostatics import Charge, ElectricField
from .magnetostatics import Wire, MagneticField

__all__ = [
    "Charge",
    "ElectricField",
    "Wire",
    "MagneticField",
]
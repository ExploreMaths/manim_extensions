# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Economic diagrams for Manim.

This module provides economic diagram visualizations including
supply-demand, AD-AS, IS-LM models, and more.

"""

from .ad_as import ADASDiagram
from .base import EconDiagram
from .is_lm import ISLMDiagram
from .linked import LinkedISLM_ADAS
from .solow import SolowDiagram
from .supply_demand import SupplyDemandDiagram

__all__ = [
    "EconDiagram",
    "SupplyDemandDiagram",
    "ADASDiagram",
    "ISLMDiagram",
    "LinkedISLM_ADAS",
    "SolowDiagram",
]
__version__ = "0.1.0"
# SPDX-FileCopyrightText: 2023 Ralphie Raccoon
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


r"""TikZ integration helpers for Manim.

This package exposes the core TikZ mobject wrapper and templating support for
creating diagrammatic scenes based on TikZ input.

"""

from manim import *

from .tikz import Tikz
from .template import TikzTemplate
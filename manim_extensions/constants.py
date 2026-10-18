# SPDX-FileCopyrightText: 2026 ExploreMaths
#
# SPDX-License-Identifier: MIT

"""Constants that the official Manim documentation does not provide.

Import these names instead of expanding values by hand, e.g.
``Rectangle(color=WHITE)`` rather than ``color="#FFFFFF"``.

Colours
-------
``RUBIKS_*``
    The official Rubik's cube sticker palette.  Manim's own
    ``RED``/``GREEN``/``YELLOW``/``ORANGE``/``BLUE`` use different values,
    so the cube colours get their own names here.
``FIELD_LAYER_*``
    Blues used for the electrostatics field-layer arcs.
``DASHED_LINE_GREY``
    Grey used for the Solow-model dashed stem line.

Other
-----
``DEFAULT_CJK_FONT`` / ``DEFAULT_MONO_FONT``
    Font defaults (re-exported from :mod:`manim_extensions.mobjects`);
    Manim itself ships no CJK or monospace default.
``HALF_DOWN``
    ``DOWN / 1.5``, the vertical step used by sequence diagrams
    (re-exported from :mod:`manim_extensions.sequence_diagram.constants`).
"""

from .mobjects import DEFAULT_CJK_FONT, DEFAULT_MONO_FONT
from .sequence_diagram.constants import HALF_DOWN

# Rubik's cube official sticker colours.
RUBIKS_RED = "#B90000"
RUBIKS_GREEN = "#009B48"
RUBIKS_YELLOW = "#FFD500"
RUBIKS_ORANGE = "#FF5900"
RUBIKS_BLUE = "#0045AD"

# Electrostatics field-layer blues.
FIELD_LAYER_BLUE = "#3399FF"
FIELD_LAYER_LIGHT_BLUE = "#66B2FF"

# Solow-model dashed stem grey.
DASHED_LINE_GREY = "#888888"

__all__ = [
    "DEFAULT_CJK_FONT",
    "DEFAULT_MONO_FONT",
    "HALF_DOWN",
    "RUBIKS_RED",
    "RUBIKS_GREEN",
    "RUBIKS_YELLOW",
    "RUBIKS_ORANGE",
    "RUBIKS_BLUE",
    "FIELD_LAYER_BLUE",
    "FIELD_LAYER_LIGHT_BLUE",
    "DASHED_LINE_GREY",
]

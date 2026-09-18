# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


"""Public entry point for the Manim extensions package.

This package bundles small utility functions and reusable Manim mobjects for
common geometry, animation, and visualisation tasks.

"""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version(__name__)
except PackageNotFoundError:
    __version__ = "0.0.0"

from .mobjects import *
from .geometry import *
from .animations import *
from . import meshes
from . import physics
from . import rubikscube
from . import fontawesome
from . import chemistry
from . import economics
from . import qr_codes
from . import table
from . import weighted_line
from . import pymunk
from . import arabic
from . import machine_learning
from . import svg_animations

__all__ = [
    "ChineseMathTex",
    "ColorText",
    "CropImageMobject",
    "DEFAULT_CJK_FONT",
    "DEFAULT_MONO_FONT",
    "ExtendedLine",
    "FadeInRandom",
    "FadeOutRandom",
    "FileTree",
    "GrowRandom",
    "HighLightWithLines",
    "LabelDot",
    "LaggedCreation",
    "MathTexBrace",
    "MathTexDoublearrow",
    "MathTexLine",
    "ObjectBorder",
    "PassingRectangle",
    "PerpendicularLine",
    "PerpendicularSign",
    "ReversedWrite",
    "ShadowAround",
    "ShortenedLine",
    "TangentPoint",
    "ThreeDVector",
    "Trail",
    "TreeDiagram",
    "TypeWriter",
    "UnHighLightWithLines",
    "VMobjectInt",
    "VideoMobject",
    "WriteRandom",
    "arabic",
    "chemistry",
    "easeInBounce",
    "easeInOutBounce",
    "easeOutBounce",
    "easeOutElastic",
    "economics",
    "fontawesome",
    "machine_learning",
    "meshes",
    "physics",
    "pymunk",
    "qr_codes",
    "rubikscube",
    "svg_animations",
    "table",
    "weighted_line",
]

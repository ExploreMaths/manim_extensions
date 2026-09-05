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

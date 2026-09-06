# SPDX-FileCopyrightText: 2025 Mr-FuzzyPenguin
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


"""Circuit drawing utilities.

This package exposes helper mobjects and utilities for circuit-style diagrams
in Manim scenes.

"""

from .mobjects import *
from .utils import *

# ``from manim import *`` (via the modules above) leaks manim's own ``utils``
# module into this namespace, shadowing the real ``utils`` submodule.
# Re-bind the actual submodule so attribute access and dotted import
# resolution see the right object.
from importlib import import_module as _import_module

utils = _import_module(__name__ + ".utils")
del _import_module

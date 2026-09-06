# SPDX-FileCopyrightText: 2024 sinianluoye
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


"""Algorithm visualisation helpers.

This package provides structural helpers for visualising algorithmic concepts,
including nodes, arrays, queues, and code-like blocks in Manim scenes.

"""

from .node import *
from .array import *
from .queue import *

# ``from manim import *`` (via the nodes above) leaks manim's own ``utils``
# module into this namespace, shadowing the real ``utils`` subpackage.
# Re-bind the actual subpackage so attribute access and dotted import
# resolution see the right object.
from importlib import import_module as _import_module

utils = _import_module(__name__ + ".utils")
del _import_module

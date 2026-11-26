# SPDX-FileCopyrightText: 2022 bmmtstb, 99Vicky
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
# patched: document module-level constants

"""custom type hints for all the models."""

# python imports

# third-party imports
from manim.typing import Point3D, Point3D_Array, VectorND

#: List of possibly differently sized point arrays; a nested numpy array cannot
#: be used because the sizes may differ.
VarArray = list[Point3D_Array]

#: A vertex given either as a point or as an iterable of coordinates.
Vertex = Point3D | list[int | float] | tuple[int | float, ...]
#: A two-dimensional point array holding all vertices.
Vertices = Point3D_Array

#: A face referencing vertices by id.
Face = VectorND | list[int] | tuple[int, ...]
#: A list of faces.
Faces = VarArray

#: A part referencing faces by id.
Part = VectorND | list[int] | tuple[int, ...]
#: A list of parts.
Parts = VarArray

#: An edge given by the ids of its two vertices.
Edge = tuple[int, int]
#: A list of edges.
Edges = list[Edge]

#: Keyword parameters forwarded to the plotting libraries.
Parameters = dict[str, object]
#: Default parameters, mapping a name to its type and default value.
DefaultParameters = dict[str, tuple[type, object]]

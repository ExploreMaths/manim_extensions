# SPDX-FileCopyrightText: 2022 bmmtstb, 99Vicky
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


"""
custom type hints for all the models.
"""

# python imports
from typing import List, Dict, Any

# third-party imports
from manim.typing import Point3D, Point3D_Array, VectorND

# VarArrays are Lists of possibly different sized np.ndarrays
# due to the possible different sizes, a nested numpy array can not be used
VarArray = List[Point3D_Array]

# vertex can be an array or an iterable of ints or floats
Vertex = Point3D | List[int | float] | tuple[int | float, ...]
# vertices has to be a two-dimensional np.ndarray
Vertices = Point3D_Array

# all faces reference vertices by id and therefore have to be integers
Face = VectorND | List[int] | tuple[int, ...]
Faces = VarArray

# all parts reference faces by id and therefore have to be integers
Part = VectorND | List[int] | tuple[int, ...]
Parts = VarArray

# an edge is a line from one vertex_id to another
Edge = tuple[int, int]
Edges = List[Edge]

Parameters = Dict[str, Any]
DefaultParameters = Dict[str, tuple[type, Any]]

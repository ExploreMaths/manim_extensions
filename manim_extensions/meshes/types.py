# SPDX-FileCopyrightText: 2022 bmmtstb, 99Vicky
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


"""
custom type hints for all the models.
"""

# python imports
from typing import List, Union, Tuple, Dict, Any

# third-party imports
import numpy as np

# VarArrays are Lists of possibly different sized np.ndarrays
# due to the possible different sizes, a nested numpy array can not be used
VarArray = List[np.ndarray]

# vertex can be an array or an iterable of ints or floats
Vertex = Union[np.ndarray, List[Union[int, float]], tuple[Union[int, float], ...]]
# vertices has to be a two-dimensional np.ndarray
Vertices = np.ndarray

# all faces reference vertices by id and therefore have to be integers
Face = Union[np.ndarray, List[int], tuple[int, ...]]
Faces = VarArray

# all parts reference faces by id and therefore have to be integers
Part = Union[np.ndarray, List[int], tuple[int, ...]]
Parts = VarArray

# an edge is a line from one vertex_id to another
Edge = tuple[int, int]
Edges = List[Edge]

Parameters = Dict[str, Any]
DefaultParameters = Dict[str, tuple[type, Any]]

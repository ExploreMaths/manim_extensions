# SPDX-FileCopyrightText: 2022 bmmtstb, 99Vicky
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


"""
some basic helpers for our models.
"""

# python imports
from typing import Dict, List, Tuple, Union

# third-party imports
import numpy as np

from .types import Edges, VarArray


def is_in_vararray(array: VarArray, item: np.ndarray, rolling: bool = True) -> bool:
    """Check whether *item* exists in *array*.

    With *rolling* enabled, cyclic permutations are considered equal
    (e.g. ``[1, 2, 3]`` matches ``[2, 3, 1]`` but not ``[1, 3, 2]``).

    Parameters
    ----------
    array
        The list of arrays to search.
    item
        The array to look for.
    rolling
        When ``True``, compare up to cyclic rotations of *item*.

    Returns
    -------
        ``True`` if *item* (or a rotation of it) is found in *array*.
    """
    if rolling:
        alternatives = [np.roll(item, i) for i in range(len(item))]
        return any(any(np.array_equal(alt, a) for a in array) for alt in alternatives)
    # non rolling
    return any(np.array_equal(item, a) for a in array)


def find_in_vararray(
    array: VarArray, item: np.ndarray, rolling: bool = True, start: int = 0
) -> List[int]:
    """Find all indices where *item* appears in *array*.

    Parameters
    ----------
    array
        The list of arrays to search.
    item
        The array to look for.
    rolling
        When ``True``, compare up to cyclic rotations of *item*.
    start
        Index at which to begin the search (useful to skip self-references).

    Returns
    -------
        Indices of every matching entry.
    """
    if rolling:
        alternatives = [np.roll(item, i) for i in range(len(item))]
        return [
            idx
            for idx, curr_item in enumerate(array[start:], start=start)
            if any(np.array_equal(a, curr_item) for a in alternatives)
        ]
    # non rolling
    return [
        idx
        for idx, curr_item in enumerate(array[start:], start=start)
        if np.array_equal(curr_item, item)
    ]


def is_vararray_equal(array1: VarArray, array2: VarArray, rolling: bool = True) -> bool:
    """Check whether two VarArrays contain the same elements (order-agnostic).

    Parameters
    ----------
    array1
        First array collection.
    array2
        Second array collection.
    rolling
        When ``True``, compare up to cyclic rotations.

    Returns
    -------
        ``True`` if both collections contain the same elements.
    """
    return all(
        is_in_vararray(array=array1, item=value2, rolling=rolling) for value2 in array2
    ) and all(
        is_in_vararray(array=array2, item=value1, rolling=rolling) for value1 in array1
    )


def is_twice_nested_iterable(obj: object, min_lens: Tuple[int, int] = (1, 3)) -> bool:
    """Check whether *obj* is a 2-D array-like structure.

    Examples of valid structures include 2-D NumPy arrays,
    ``List[List[int|float]]``, and similar.

    Parameters
    ----------
    obj
        The object to inspect.
    min_lens
        Minimum lengths for the outer and inner layers.

    Returns
    -------
        ``True`` if *obj* is a twice-nested iterable meeting the size
        requirements.
    """
    # easy case np.ndarray with correct specs
    if isinstance(obj, np.ndarray) and len(obj.shape) == 2:
        return bool(obj.shape[0] >= min_lens[0] and obj.shape[1] >= min_lens[1])
    if isinstance(obj, (list, tuple)) and len(obj) == 0:
        return True

    if isinstance(obj, (list, tuple, np.ndarray)) and len(obj) >= min_lens[0]:
        # obj is iterable
        return all(
            # either list / tuple with values inside
            # or np.ndarray with shape length 1
            (
                (
                    isinstance(sub_obj, (list, tuple))
                    and all(isinstance(v, (int, float)) for v in sub_obj)
                )
                or (isinstance(sub_obj, np.ndarray) and len(sub_obj.shape) == 1)
            )
            and len(sub_obj) >= min_lens[1]
            for sub_obj in obj
        )

    return False


def are_edges_equal(edges1: Edges, edges2: Edges) -> bool:
    """Check whether two edge lists contain the same (unordered) edges.

    Parameters
    ----------
    edges1
        First list of edges.
    edges2
        Second list of edges.

    Returns
    -------
        ``True`` if both lists contain the same edges regardless of order.
    """
    return all(e1 in edges2 for e1 in edges1) and all(e2 in edges1 for e2 in edges2)


def fix_references(
    original: VarArray, indices: Union[np.ndarray, List[int]]
) -> List[int]:
    """Remove references to *indices* from *original* and adjust remaining indices.

    Both *original* and *indices* are mutated in place for performance.

    Parameters
    ----------
    original
        The collection of sub-arrays to clean up.
    indices
        Indices whose references should be removed.

    Returns
    -------
        Indices in *original* where entries were removed.
    """
    # reverse sort indices in place to delete back to front and change given indices accordingly
    indices[:] = sorted(set(indices), reverse=True)

    # get list of indices where original references removed indices
    sub_removed = []
    for i, part in enumerate(original):
        if any(idx in part for idx in indices):
            sub_removed.append(i)

    # delete all parts that contain at least one of the indices using the precomputed list
    # make sure to delete back to front
    sub_removed.sort(reverse=True)
    for s_r_index in sub_removed:
        del original[s_r_index]

    # change indices of all sub_objects due to parent-deletions in place!
    # (indices is reversely sorted)
    for idx in indices:
        new_original = []
        for arr in original:
            new_original.append(np.where(arr > idx, arr - 1, arr))
        original[:] = new_original

    return sorted(sub_removed)


def remove_keys_from_dict(d: Dict[str, object], keys: List[str]) -> Dict[str, object]:
    """Remove *keys* from dictionary *d* without raising ``KeyError``.

    Parameters
    ----------
    d
        The dictionary to mutate.
    keys
        Keys to remove.

    Returns
    -------
        The (potentially empty) mutated dictionary.
    """
    if d is None:
        return {}
    for key in keys:
        try:
            del d[key]
        except KeyError:
            pass
    return d

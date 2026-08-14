"""
some basic helpers for our models
"""
# python imports
from typing import Any, Dict, List, Tuple, Union
# third-party imports
import numpy as np

from manim_extensions.meshes.types import Edges, VarArray


def is_in_vararray(array: VarArray, item: np.ndarray, rolling: bool = True) -> bool:
    """Check whether *item* exists in *array*.

    With *rolling* enabled, cyclic permutations are considered equal
    (e.g. ``[1, 2, 3]`` matches ``[2, 3, 1]`` but not ``[1, 3, 2]``).

    Parameters
    ----------
    array : VarArray
        The list of arrays to search.
    item : np.ndarray
        The array to look for.
    rolling : bool
        When ``True``, compare up to cyclic rotations of *item*.

    Returns
    -------
    bool
        ``True`` if *item* (or a rotation of it) is found in *array*.
    """
    if rolling:
        alternatives = [np.roll(item, i) for i in range(len(item))]
        return any(any(np.array_equal(alt, a) for a in array) for alt in alternatives)
    # non rolling
    return any(np.array_equal(item, a) for a in array)


def find_in_vararray(array: VarArray, item: np.ndarray, rolling: bool = True, start: int = 0) -> List[int]:
    """Find all indices where *item* appears in *array*.

    Parameters
    ----------
    array : VarArray
        The list of arrays to search.
    item : np.ndarray
        The array to look for.
    rolling : bool
        When ``True``, compare up to cyclic rotations of *item*.
    start : int
        Index at which to begin the search (useful to skip self-references).

    Returns
    -------
    List[int]
        Indices of every matching entry.
    """
    if rolling:
        alternatives = [np.roll(item, i) for i in range(len(item))]
        return [idx for idx, curr_item in enumerate(array[start:], start=start)
                if any(np.array_equal(a, curr_item) for a in alternatives)]
    # non rolling
    return [idx for idx, curr_item in enumerate(array[start:], start=start) if np.array_equal(curr_item, item)]


def is_vararray_equal(array1: VarArray, array2: VarArray, rolling: bool = True) -> bool:
    """Check whether two VarArrays contain the same elements (order-agnostic).

    Parameters
    ----------
    array1 : VarArray
        First array collection.
    array2 : VarArray
        Second array collection.
    rolling : bool
        When ``True``, compare up to cyclic rotations.

    Returns
    -------
    bool
        ``True`` if both collections contain the same elements.
    """
    return all(is_in_vararray(array=array1, item=value2, rolling=rolling) for value2 in array2) and \
           all(is_in_vararray(array=array2, item=value1, rolling=rolling) for value1 in array1)


def is_twice_nested_iterable(obj: Any, min_lens: Tuple[int, int] = (1, 3)) -> bool:
    """Check whether *obj* is a 2-D array-like structure.

    Examples of valid structures include 2-D NumPy arrays,
    ``List[List[int|float]]``, and similar.

    Parameters
    ----------
    obj : Any
        The object to inspect.
    min_lens : Tuple[int, int]
        Minimum lengths for the outer and inner layers.

    Returns
    -------
    bool
        ``True`` if *obj* is a twice-nested iterable meeting the size
        requirements.
    """
    # easy case np.ndarray with correct specs
    if isinstance(obj, np.ndarray) and len(obj.shape) == 2:
        return obj.shape[0] >= min_lens[0] and obj.shape[1] >= min_lens[1]
    if isinstance(obj, (list, tuple)) and len(obj) == 0:
        return True

    if isinstance(obj, (list, tuple, np.ndarray)) and \
            len(obj) >= min_lens[0]:
        # obj is iterable
        return all(
            # either list / tuple with values inside
            # or np.ndarray with shape length 1
            ((isinstance(sub_obj, (list, tuple)) and all(isinstance(v, (int, float)) for v in sub_obj)) or
             (isinstance(sub_obj, np.ndarray) and len(sub_obj.shape) == 1)) and \
            len(sub_obj) >= min_lens[1] for sub_obj in obj
        )

    return False


def are_edges_equal(edges1: Edges, edges2: Edges) -> bool:
    """Check whether two edge lists contain the same (unordered) edges.

    Parameters
    ----------
    edges1 : Edges
        First list of edges.
    edges2 : Edges
        Second list of edges.

    Returns
    -------
    bool
        ``True`` if both lists contain the same edges regardless of order.
    """
    return all(e1 in edges2 for e1 in edges1) and all(e2 in edges1 for e2 in edges2)


def fix_references(original: VarArray, indices: Union[np.ndarray, List[int]]) -> List[int]:
    """Remove references to *indices* from *original* and adjust remaining indices.

    Both *original* and *indices* are mutated in place for performance.

    Parameters
    ----------
    original : VarArray
        The collection of sub-arrays to clean up.
    indices : Union[np.ndarray, List[int]]
        Indices whose references should be removed.

    Returns
    -------
    List[int]
        Indices in *original* where entries were removed.
    """
    # reverse sort indices in place to delete back to front and change given indices accordingly
    indices[:] = list(set(indices))
    indices.sort(reverse=True)

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


def remove_keys_from_dict(d: dict, keys: List[str]) -> Dict[str, Any]:
    """Remove *keys* from dictionary *d* without raising ``KeyError``.

    Parameters
    ----------
    d : dict
        The dictionary to mutate.
    keys : List[str]
        Keys to remove.

    Returns
    -------
    Dict[str, Any]
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
# SPDX-FileCopyrightText: 2026 MathItYT
#
# SPDX-License-Identifier: MIT

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Helper functions for decision tree visualization."""

from typing import Protocol

from numpy.typing import NDArray


class SklearnTree(Protocol):
    """Structural type for ``sklearn.tree.DecisionTreeClassifier.tree_``."""

    node_count: int
    children_left: NDArray
    children_right: NDArray


def compute_node_depths(tree: SklearnTree) -> list[int]:
    """Computes the depths of nodes for level order traversal.

    Parameters
    ----------
    tree : SklearnTree
        The sklearn decision tree structure (``tree_`` attribute of a fitted
        :class:`~sklearn.tree.DecisionTreeClassifier`).

    Returns
    -------
    list[int]
        The depth of each node, indexed by node index. Leaf nodes that are
        never reached get a depth of ``-1``.
    """

    def depth(node_index: int, current_node_index: int = 0) -> int:
        """Compute the height of a node"""
        if current_node_index == node_index:
            return 0
        elif (
            tree.children_left[current_node_index]
            == tree.children_right[current_node_index]
        ):
            return -1
        else:
            # Compute the height of each subtree
            l_depth = depth(node_index, tree.children_left[current_node_index])
            r_depth = depth(node_index, tree.children_right[current_node_index])
            # The index is only in one of them
            if l_depth != -1:
                return l_depth + 1
            elif r_depth != -1:
                return r_depth + 1
            else:
                return -1

    node_depths = [depth(index) for index in range(tree.node_count)]

    return node_depths


def compute_level_order_traversal(tree: SklearnTree) -> list[int]:
    """Computes level order traversal of a sklearn tree.

    Parameters
    ----------
    tree : SklearnTree
        The sklearn decision tree structure (``tree_`` attribute of a fitted
        :class:`~sklearn.tree.DecisionTreeClassifier`).

    Returns
    -------
    list[int]
        Node indices sorted by ascending depth, i.e. in level order.
    """

    def depth(node_index: int, current_node_index: int = 0) -> int:
        """Compute the height of a node"""
        if current_node_index == node_index:
            return 0
        elif (
            tree.children_left[current_node_index]
            == tree.children_right[current_node_index]
        ):
            return -1
        else:
            # Compute the height of each subtree
            l_depth = depth(node_index, tree.children_left[current_node_index])
            r_depth = depth(node_index, tree.children_right[current_node_index])
            # The index is only in one of them
            if l_depth != -1:
                return l_depth + 1
            elif r_depth != -1:
                return r_depth + 1
            else:
                return -1

    node_depths = [(index, depth(index)) for index in range(tree.node_count)]
    sorted_depths = sorted(node_depths, key=lambda x: x[1])
    sorted_inds = [node_depth[0] for node_depth in sorted_depths]

    return sorted_inds


def compute_bfs_traversal(tree: SklearnTree) -> list[int]:
    """Traverses the tree in BFS order and returns the nodes in order.

    Parameters
    ----------
    tree : SklearnTree
        The sklearn decision tree structure (``tree_`` attribute of a fitted
        :class:`~sklearn.tree.DecisionTreeClassifier`).

    Returns
    -------
    list[int]
        Node indices in breadth-first order, starting from the root.
    """
    traversal_order = []
    tree_root_index = 0
    queue = [tree_root_index]
    while len(queue) > 0:
        current_index = queue.pop(0)
        traversal_order.append(current_index)
        left_child_index = tree.children_left[current_index]
        right_child_index = tree.children_right[current_index]
        is_leaf_node = left_child_index == right_child_index
        if not is_leaf_node:
            queue.append(left_child_index)
            queue.append(right_child_index)

    return traversal_order


def compute_best_first_traversal(tree: SklearnTree) -> None:
    """Traverses the tree according to the best split first order.

    Parameters
    ----------
    tree : SklearnTree
        The sklearn decision tree structure (``tree_`` attribute of a fitted
        :class:`~sklearn.tree.DecisionTreeClassifier`).

    Notes
    -----
    Not implemented yet; currently a no-op.
    """
    pass


def compute_node_to_parent_mapping(tree: SklearnTree) -> dict[int, int]:
    """Returns a hashmap mapping node indices to their parent indices.

    Parameters
    ----------
    tree : SklearnTree
        The sklearn decision tree structure (``tree_`` attribute of a fitted
        :class:`~sklearn.tree.DecisionTreeClassifier`).

    Returns
    -------
    dict[int, int]
        Mapping from each node index to its parent node index. The root (0)
        maps to ``-1``.
    """
    node_to_parent = {0: -1}  # Root has no parent
    num_nodes = tree.node_count
    for node_index in range(num_nodes):
        # Explore left children
        left_child_node_index = tree.children_left[node_index]
        if left_child_node_index != -1:
            node_to_parent[left_child_node_index] = node_index
        # Explore right children
        right_child_node_index = tree.children_right[node_index]
        if right_child_node_index != -1:
            node_to_parent[right_child_node_index] = node_index

    return node_to_parent

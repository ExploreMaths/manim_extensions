# SPDX-FileCopyrightText: 2026 MathItYT
#
# SPDX-License-Identifier: MIT

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""List group utility for neural network visualization."""

from typing import Iterator

from manim import Mobject


class ListGroup(Mobject):
    """Indexable Group with traditional list operations.

    Parameters
    ----------
    layers
        Initial items stored in the group.

    Examples
    --------
    .. manim:: ListGroupExample
       :save_last_frame:

       from manim import *
       from manim_extensions.machine_learning.utils.mobjects.list_group import ListGroup

       class ListGroupExample(Scene):
           def construct(self):
               self.add(ListGroup(Circle(radius=0.3), Square(side_length=0.6),
                                  Triangle()).scale(3))
    """

    def __init__(self, *layers: Mobject):
        """Initialize the group with the given items."""
        super().__init__()
        self.items: list[Mobject] = [*layers]
        # Add the items as submobjects so the group is visible when rendered
        # (Mobject.add bypasses ListGroup's list-semantics `add` override).
        Mobject.add(self, *layers)

    def __getitem__(  # type: ignore[override] # list indexing may return a single item or a slice
        self, indices: int | slice
    ) -> Mobject | list[Mobject]:
        """Traditional list indexing."""
        return self.items[indices]

    def insert(  # type: ignore[override] # intentionally returns None instead of the group
        self, index: int, item: Mobject
    ):
        """Inserts item at index.

        Parameters
        ----------
        index
            Index at which to insert the item.
        item
            Item to insert into the group.
        """
        self.items.insert(index, item)
        self.submobjects = self.items

    def remove_at_index(self, index: int) -> Mobject:
        """Removes item at index.

        Parameters
        ----------
        index
            Index of the item to remove.

        Returns
        -------
            The removed item.

        Raises
        ------
        Exception
            Raised when ``index`` is out of range.
        """
        if index > len(self.items):
            raise Exception(f"ListGroup index out of range: {index}")
        item = self.items[index]
        del self.items[index]
        self.submobjects = self.items

        return item

    def remove_at_indices(self, indices: list[int]) -> list[Mobject]:
        """Removes items at indices.

        Parameters
        ----------
        indices
            Indices of the items to remove.

        Returns
        -------
            The removed items, in the order of the given indices.
        """
        items = []
        for index in indices:
            item = self.remove_at_index(index)
            items.append(item)

        return items

    def remove(self, item: Mobject) -> Mobject:  # type: ignore[override] # intentionally shadows Mobject.remove with list semantics
        """Removes first instance of item.

        Parameters
        ----------
        item
            Item to remove from the group.

        Returns
        -------
            The removed item.
        """
        self.items.remove(item)
        self.submobjects = self.items

        return item

    def get(self, index: int) -> Mobject:
        """Gets item at index.

        Parameters
        ----------
        index
            Index of the item to retrieve.

        Returns
        -------
            The item stored at the given index.
        """
        return self.items[index]

    def add(self, item: Mobject):  # type: ignore[override] # intentionally shadows Mobject.add with list semantics
        """Adds to end.

        Parameters
        ----------
        item
            Item to append to the end of the group.
        """
        self.items.append(item)
        self.submobjects = self.items

    def replace(self, index: int, item: Mobject):  # type: ignore[override] # intentionally shadows Mobject.replace with list semantics
        """Replaces item at index.

        Parameters
        ----------
        index
            Index of the item to replace.
        item
            Item to store at the given index.
        """
        self.items[index] = item
        self.submobjects = self.items

    def index_of(self, item: Mobject) -> int:
        """

        Parameters
        ----------
        item
            Item to look up in the group.

        Returns
        -------
            Index of the item, or -1 if it is not in the group.
        """
        for index, obj in enumerate(self.items):
            if item is obj:
                return index
        return -1

    def __len__(self) -> int:
        """Length of items."""
        return len(self.items)

    def set_z_index(  # type: ignore[override] # intentionally returns None instead of the group
        self, z_index_value: int, family: bool = True
    ):
        """Sets z index of all values in ListGroup.

        Parameters
        ----------
        z_index_value
            Z-index to apply to all items in the group.
        family
            Whether to also set the z-index of submobjects, by default True.
        """
        for item in self.items:
            item.set_z_index(z_index_value, family=True)

    def __iter__(self) -> Iterator[Mobject]:
        self.current_index = -1
        return self

    def __next__(self) -> Mobject:
        self.current_index += 1
        if self.current_index < len(self.items):
            return self.items[self.current_index]
        raise StopIteration

    def __repr__(self) -> str:
        return f"ListGroup({self.items})"



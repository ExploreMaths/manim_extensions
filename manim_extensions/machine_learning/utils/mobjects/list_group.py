# SPDX-FileCopyrightText: 2026 MathItYT
#
# SPDX-License-Identifier: MIT

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""List group utility for neural network visualization."""

from typing import Any, Iterator

from manim import Mobject


class ListGroup(Mobject):
    """Indexable Group with traditional list operations

    Parameters
    ----------
    layers : Mobject
        Initial items stored in the group.
    """

    def __init__(self, *layers: Mobject) -> None:
        super().__init__()
        self.items: list[Mobject] = [*layers]

    def __getitem__(  # type: ignore[override] # list indexing may return a single item or a slice
        self, indices: int | slice
    ) -> Mobject | list[Mobject]:
        """Traditional list indexing"""
        return self.items[indices]

    def insert(  # type: ignore[override] # intentionally returns None instead of the group
        self, index: int, item: Mobject
    ) -> None:
        """Inserts item at index"""
        self.items.insert(index, item)
        self.submobjects = self.items

    def remove_at_index(self, index: int) -> Mobject:
        """Removes item at index"""
        if index > len(self.items):
            raise Exception(f"ListGroup index out of range: {index}")
        item = self.items[index]
        del self.items[index]
        self.submobjects = self.items

        return item

    def remove_at_indices(self, indices: list[int]) -> list[Mobject]:
        """Removes items at indices"""
        items = []
        for index in indices:
            item = self.remove_at_index(index)
            items.append(item)

        return items

    def remove(self, item: Mobject) -> Mobject:  # type: ignore[override] # intentionally shadows Mobject.remove with list semantics
        """Removes first instance of item"""
        self.items.remove(item)
        self.submobjects = self.items

        return item

    def get(self, index: int) -> Mobject:
        """Gets item at index"""
        return self.items[index]

    def add(self, item: Mobject) -> None:  # type: ignore[override] # intentionally shadows Mobject.add with list semantics
        """Adds to end"""
        self.items.append(item)
        self.submobjects = self.items

    def replace(self, index: int, item: Mobject) -> None:  # type: ignore[override] # intentionally shadows Mobject.replace with list semantics
        """Replaces item at index"""
        self.items[index] = item
        self.submobjects = self.items

    def index_of(self, item: Mobject) -> int:
        """Returns index of item if it exists"""
        for index, obj in enumerate(self.items):
            if item is obj:
                return index
        return -1

    def __len__(self) -> int:
        """Length of items"""
        return len(self.items)

    def set_z_index(  # type: ignore[override] # intentionally returns None instead of the group
        self, z_index_value: int, family: bool = True
    ) -> None:
        """Sets z index of all values in ListGroup"""
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

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

""":class:`~manim_extensions.table.row.Row` class for Manim tables.

This module provides the :class:`~manim_extensions.table.row.Row` class for table visualizations.

"""

from collections.abc import Iterator
from typing import Any, overload

from manim import RIGHT, VGroup
from .cell import Cell


class Row(VGroup):
    """
    A row of cells in a table.

    Parameters
    ----------
    values
        List of string values for each cell.
    cell_widths
        Either a single width for all cells, or a list of widths per column.

    cell_height
        Height of each cell.
    font_size
        Font size for cell text.
    is_header
        If True, renders cells as header cells (bold, thicker border).
    show_border
        If True, cells have visible borders.
    index
        :class:`~manim_extensions.table.row.Row` index in the parent table (useful for animations).
    **kwargs
        Additional arguments passed to
        :class:`~manim.mobject.types.vectorized_mobject.VGroup`.

    Examples
    --------
    .. manim:: RowScene
       :save_last_frame:

       from manim import *
       from manim_extensions.table import Row

       class RowScene(Scene):
           def construct(self):
               row = Row(["Alice", "25", "Paris"])
               row[1].set_font_color(RED)
               row.scale(2.0)
               self.add(row)
    """

    def __init__(
        self,
        values: list[str],
        cell_widths: float | list[float] = 1.5,
        cell_height: float = 0.5,
        font_size: int = 20,
        is_header: bool = False,
        show_border: bool = True,
        index: int = 0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)

        self.values = values
        # Convert single width to list
        if isinstance(cell_widths, (int, float)):
            self.cell_widths = [float(cell_widths)] * len(values)
        else:
            self.cell_widths = list(cell_widths)
        self.cell_height = cell_height
        self.font_size = font_size
        self.is_header = is_header
        self.show_border = show_border
        self.index = index

        self.cells: list[Cell] = []
        self.create_cells()

    def create_cells(self) -> Any:
        """Create and position all cells in this row.

        Returns
        -------
            The resulting value.
        """
        for i, value in enumerate(self.values):
            cell = Cell(
                value=value,
                width=self.cell_widths[i],
                height=self.cell_height,
                font_size=self.font_size,
                is_header=self.is_header,
                show_border=self.show_border,
            )

            # Position cells horizontally
            if i > 0:
                cell.next_to(self.cells[i - 1], RIGHT, buff=0)

            self.cells.append(cell)
            self.add(cell)

    @overload  # type: ignore[override]
    def __getitem__(self, index: int) -> Cell:
        """Return the cell at the given index.

        Parameters
        ----------
        index
            The cell index.

        Returns
        -------
            The selected cell.
        """
        ...

    @overload
    def __getitem__(self, index: slice) -> list[Cell]:
        """Return the cells selected by the slice.

        Parameters
        ----------
        index
            The cell slice.

        Returns
        -------
            The selected cells.
        """
        ...

    def __getitem__(self, index: int | slice) -> Cell | list[Cell]:
        """Return a cell or a slice of cells.

        Parameters
        ----------
        index
            The cell index or slice.

        Returns
        -------
            The selected cell or list of cells.
        """
        return self.cells[index]

    def __len__(self) -> int:
        """Return the number of cells in this row.

        Returns
        -------
            The cell count.
        """
        return len(self.cells)

    def __iter__(self) -> Iterator[Cell]:
        """Iterate over the cells.

        Returns
        -------
            An iterator over the cells.
        """
        return iter(self.cells)

    def get_cell(self, index: int) -> Cell:
        """Get a cell by index.

        Parameters
        ----------
        index
            Index of the cell within the row (0-indexed).

        Returns
        -------
            The cell at the given index.
        """
        return self.cells[index]

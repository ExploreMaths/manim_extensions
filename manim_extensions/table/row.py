# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Row class for Manim tables.

This module provides the Row class for table visualizations.

"""

from manim import *
from .cell import Cell
from typing import List, Union


class Row(VGroup):
    """
    A row of cells in a table.
    
    Args:
        values: List of string values for each cell
        cell_widths: Either a single width for all cells, or a list of widths per column
        cell_height: Height of each cell
        font_size: Font size for cell text
        is_header: If True, renders cells as header cells (bold, thicker border)
        show_border: If True, cells have visible borders
        index: Row index in the parent table (useful for animations)
        **kwargs: Additional arguments passed to VGroup
    """
    
    def __init__(
        self,
        values: List[str],
        cell_widths: Union[float, List[float]] = 1.5,
        cell_height: float = 0.5,
        font_size: int = 20,
        is_header: bool = False,
        show_border: bool = True,
        index: int = 0,
        **kwargs
    ):
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
        
        self.cells: List[Cell] = []
        self.create_cells()
    
    def create_cells(self):
        """Create and position all cells in this row."""
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
    
    def __getitem__(self, index: int) -> Cell:
        """Get a cell by index."""
        return self.cells[index]
    
    def __len__(self) -> int:
        """Return number of cells in this row."""
        return len(self.cells)
    
    def __iter__(self):
        """Iterate over cells."""
        return iter(self.cells)
    
    def get_cell(self, index: int) -> Cell:
        """Get a cell by index."""
        return self.cells[index]
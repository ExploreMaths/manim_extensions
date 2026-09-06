# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""
Table - The main database table component.
"""

from manim import *
import numpy as np
from .row import Row
from .cell import Cell
from typing import List, Optional, Tuple


class Table(VGroup):
    """
    A database table visualization for Manim Community Edition (manim CE).
    
    The table can be created in two ways:

    1. With a single data list where the first row is treated as the header:
       Table([["col1", "col2"], ["val1", "val2"]])
    
    2. With explicit header and rows:
       Table(header=["col1", "col2"], rows=[["val1", "val2"]])

    Parameters
    ----------
    data : Optional[List[List[str]]], optional
        List of rows where the first row is treated as the header. Ignored if
        ``header`` is provided.
    header : Optional[List[str]], optional
        Explicit header row (list of column names). Requires ``rows``.
    rows : Optional[List[List[str]]], optional
        Data rows (list of lists). Required if ``header`` is provided.
    cell_width : float, optional
        Default cell width, used only when ``auto_fit=False``. Defaults to ``1.5``.
    cell_height : float, optional
        Height of each cell. Defaults to ``0.5``.
    font_size : int, optional
        Font size for cell text. Defaults to ``20``.
    show_border : bool, optional
        If True, cells have visible borders.
    auto_fit : bool, optional
        If True, column widths auto-fit to the longest content. Defaults to True.
    padding : float, optional
        Extra padding around text when ``auto_fit=True``. Defaults to ``0.3``.
    **kwargs
        Additional arguments passed to
        :class:`~manim.mobject.types.vectorized_mobject.VGroup`.

    Examples
    --------
    Create a table from a data list (the first row is the header) and
    animate it with :class:`~manim.animation.creation.Write`.  Individual
    cells, rows and columns can be accessed for highlighting, and rows and
    columns can be added and deleted again with animations.  Styling can
    be applied per header, per column or per cell.

    .. manim:: TableDocExample

       from manim import *
       from manim_extensions.table import Table

       class TableDocExample(Scene):
           def construct(self):
               data = [
                   ["Name", "Age", "City"],
                   ["Alice", "25", "New York"],
                   ["Bob", "30", "Paris"],
               ]
               table = Table(data)
               self.play(Write(table))
               # row 0 is the header, row 1 the first data row
               self.play(Circumscribe(table.get_cell(1, 1)))
               self.play(Circumscribe(table.get_column_by_name("Age")))
               self.wait()

    .. manim:: TableRowOpsDocExample

       from manim import *
       from manim_extensions.table import Table

       class TableRowOpsDocExample(Scene):
           def construct(self):
               table = Table([
                   ["Name", "Age", "City"],
                   ["Alice", "25", "New York"],
                   ["Bob", "30", "Paris"],
               ])
               self.add(table)
               # add a new row at the bottom; the mutation methods return
               # the affected row together with the animations to play
               new_row, anims = table.add_row(["Charlie", "35", "London"])
               self.play(AnimationGroup(*anims, lag_ratio=0.05))
               # delete a data row (index 1 is the first data row, header is 0)
               deleted_row, anims = table.delete_row(1)
               self.play(AnimationGroup(*anims, lag_ratio=0.05))
               self.wait()

    .. manim:: TableColumnOpsDocExample

       from manim import *
       from manim_extensions.table import Table

       class TableColumnOpsDocExample(Scene):
           def construct(self):
               table = Table([
                   ["ID", "Name"],
                   ["1", "Alice"],
                   ["2", "Bob"],
               ])
               self.add(table)
               # append a column at the end (nothing to shift, only FadeIn anims)
               new_col, shift_anims, appear_anims = table.add_column(
                   header="Score", values=["85", "92"]
               )
               if shift_anims:
                   self.play(AnimationGroup(*shift_anims, lag_ratio=0.1))
               self.play(AnimationGroup(*appear_anims, lag_ratio=0.1))
               # insert a column in the middle (index 1)
               new_col, shift_anims, appear_anims = table.add_column(
                   header="Role", values=["Dev", "Manager"], index=1
               )
               if shift_anims:
                   self.play(AnimationGroup(*shift_anims, lag_ratio=0.1))
               self.play(AnimationGroup(*appear_anims, lag_ratio=0.1))
               # delete a column by index
               deleted_col, shift_anims = table.delete_column(0)
               self.play(FadeOut(deleted_col))
               if shift_anims:
                   self.play(AnimationGroup(*shift_anims, lag_ratio=0.1))
               self.wait()

    .. manim:: TableStylingDocExample
       :save_last_frame:

       from manim import *
       from manim_extensions.table import Table

       class TableStylingDocExample(Scene):
           def construct(self):
               table = Table([
                   ["Product", "Category", "Price"],
                   ["Apple", "Fruit", "$1.50"],
                   ["Banana", "Fruit", "$0.75"],
                   ["Milk", "Dairy", "$2.00"],
               ])
               # style the header
               table.set_header_background_color(BLUE, opacity=0.3)
               table.set_header_font_color(WHITE)
               # style a whole column (column index 2 = Price)
               table.set_column_font_color(2, GREEN)
               # style a single cell (row 3, column 2)
               table.get_cell(3, 2).set_font_color(RED)
               table.get_cell(3, 2).set_background_color(RED, opacity=0.2)
               self.add(table)
    """
    
    def __init__(
        self,
        data: Optional[List[List[str]]] = None,
        header: Optional[List[str]] = None,
        rows: Optional[List[List[str]]] = None,
        cell_width: float = 1.5,
        cell_height: float = 0.5,
        font_size: int = 20,
        show_border: bool = True,
        auto_fit: bool = True,
        padding: float = 0.3,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        # Parse input
        if header is not None:
            self.header_values = header
            self.row_values = rows if rows is not None else []
        elif data is not None and len(data) > 0:
            self.header_values = data[0]
            self.row_values = data[1:] if len(data) > 1 else []
        else:
            raise ValueError("Must provide either 'data' or 'header' argument")
        
        self.cell_height = cell_height
        self.font_size = font_size
        self.show_border = show_border
        self.auto_fit = auto_fit
        self.padding = padding
        
        # Calculate column widths
        if auto_fit:
            self.column_widths = self.calculate_column_widths()
        else:
            self.column_widths = [cell_width] * len(self.header_values)
        
        # Store a single cell_width for add_row (use max column width)
        self.cell_width = max(self.column_widths) if self.column_widths else cell_width
        
        # Create header row
        self.header_row: Row = Row(
            values=self.header_values,
            cell_widths=self.column_widths,
            cell_height=cell_height,
            font_size=font_size,
            is_header=True,
            show_border=show_border,
            index=0,
        )
        self.add(self.header_row)
        
        # Create data rows
        self.rows: List[Row] = []
        for i, row_values in enumerate(self.row_values):
            row = Row(
                values=row_values,
                cell_widths=self.column_widths,
                cell_height=cell_height,
                font_size=font_size,
                is_header=False,
                show_border=show_border,
                index=i + 1,
            )
            # Position below previous row
            if i == 0:
                row.next_to(self.header_row, DOWN, buff=0)
            else:
                row.next_to(self.rows[i - 1], DOWN, buff=0)
            
            self.rows.append(row)
            self.add(row)
    
    def calculate_column_widths(self) -> List[float]:
        """
        Calculate the width of each column based on the longest text content.
        """
        num_cols = len(self.header_values)
        widths = [0.0] * num_cols
        
        # Combine header and all rows for measurement
        all_rows = [self.header_values] + self.row_values
        
        for row_data in all_rows:
            for col_idx, value in enumerate(row_data):
                if col_idx >= num_cols:
                    continue
                # Create temporary text to measure
                text = Text(value, font_size=self.font_size)
                text_width = text.get_width() + self.padding
                widths[col_idx] = max(widths[col_idx], text_width)
        
        return widths
    
    # -------------------------------------------------------------------------
    # Accessors
    # -------------------------------------------------------------------------
    
    def get_cell(self, row: int, col: int) -> Cell:
        """
        Get a specific cell by row and column index.
        Row 0 is the header row.
        """
        if row == 0:
            return self.header_row[col]
        return self.rows[row - 1][col]
    
    def get_row(self, index: int) -> Row:
        """
        Get a row by index. Index 0 returns the header row.
        """
        if index == 0:
            return self.header_row
        return self.rows[index - 1]
    
    def get_column(self, index: int) -> VGroup:
        """
        Get all cells in a column as a VGroup.
        Includes the header cell.
        """
        cells = [self.header_row[index]]
        for row in self.rows:
            cells.append(row[index])
        return VGroup(*cells)
    
    def get_column_by_name(self, name: str) -> VGroup:
        """
        Get a column by its header name.
        """
        try:
            index = self.header_values.index(name)
            return self.get_column(index)
        except ValueError:
            raise ValueError(f"Column '{name}' not found in header")
    
    def get_header_names(self) -> List[str]:
        """Return list of column names."""
        return list(self.header_values)
    
    def __len__(self) -> int:
        """Return number of data rows (not including header)."""
        return len(self.rows)
    
    def __getitem__(self, index: int) -> Row:
        """Get a data row by index (0-indexed, not including header)."""
        return self.rows[index]
    
    # -------------------------------------------------------------------------
    # Styling methods
    # -------------------------------------------------------------------------
    
    def set_column_font_color(self, col: int, color, include_header: bool = False):
        """
        Set the font color for all cells in a column.
        
        Args:
            col: Column index (0-indexed)
            color: A Manim color
            include_header: If True, also colors the header cell
        """
        if include_header:
            self.header_row[col].set_font_color(color)
        for row in self.rows:
            row[col].set_font_color(color)
        return self
    
    def set_column_background_color(self, col: int, color, opacity: float = 0.5, include_header: bool = False):
        """
        Set the background color for all cells in a column.
        
        Args:
            col: Column index (0-indexed)
            color: A Manim color
            opacity: Background opacity (0 to 1)
            include_header: If True, also colors the header cell
        """
        if include_header:
            self.header_row[col].set_background_color(color, opacity)
        for row in self.rows:
            row[col].set_background_color(color, opacity)
        return self
    
    def set_column_border_color(self, col: int, color, include_header: bool = True):
        """
        Set the border color for all cells in a column.
        
        Args:
            col: Column index (0-indexed)
            color: A Manim color
            include_header: If True, also colors the header cell
        """
        if include_header:
            self.header_row[col].set_border_color(color)
        for row in self.rows:
            row[col].set_border_color(color)
        return self
    
    def set_header_background_color(self, color, opacity: float = 0.5):
        """
        Set the background color for all header cells.
        
        Args:
            color: A Manim color
            opacity: Background opacity (0 to 1)
        """
        for cell in self.header_row:
            cell.set_background_color(color, opacity)
        return self
    
    def set_header_font_color(self, color):
        """
        Set the font color for all header cells.
        
        Args:
            color: A Manim color
        """
        for cell in self.header_row:
            cell.set_font_color(color)
        return self
    
    # -------------------------------------------------------------------------
    # Mutations (return animations)
    # -------------------------------------------------------------------------
    
    def add_row(
        self, 
        values: List[str]
    ) -> Tuple[Row, List]:
        """
        Add a new row to the bottom of the table.
        
        Returns:
            Tuple of (new_row, animations) where animations includes both:
            - Resize transforms for existing cells (if column widths change)
            - FadeIn for the new row cells
            
            All animations can be played together with AnimationGroup.
        
        Example:
            new_row, anims = table.add_row(["Alice", "Smith", "30"])
            self.play(AnimationGroup(*anims, lag_ratio=0.05))
        """
        # First, add the new row values to internal tracking
        self.row_values.append(values)
        
        # Calculate scale factor using HEIGHT (stable during width resize)
        # Width-based calculation fails after Transform morphs cells
        first_header_cell = self.header_row[0]
        scale_factor = first_header_cell.get_height() / self.cell_height if self.cell_height > 0 else 1.0
        
        # Check if we need to resize columns (before creating the row)
        resize_animations = []
        new_widths = self.column_widths  # Default to current widths
        
        if self.auto_fit:
            new_widths = self.calculate_column_widths()
            
            # Check if any column width changed
            width_changed = any(
                abs(old_w - new_w) > 0.01 
                for old_w, new_w in zip(self.column_widths, new_widths)
            )
            
            if width_changed:
                # Build resize animations for all existing rows
                table_left = self.header_row.get_left()[0]
                
                # Create target cells for header
                x_offset = table_left
                for col_idx, new_w in enumerate(new_widths):
                    header_cell = self.header_row[col_idx]
                    target_header = header_cell.get_resized_copy(new_w)
                    
                    # Use scaled width for positioning
                    scaled_w = target_header.get_width()
                    target_x = x_offset + scaled_w / 2
                    target_header.move_to([target_x, header_cell.get_center()[1], 0])
                    resize_animations.append(Transform(header_cell, target_header))
                    
                    # Update cell's internal width to match new width
                    header_cell.cell_width = new_w
                    
                    x_offset += scaled_w
                
                # Update header row's cell_widths list
                self.header_row.cell_widths = list(new_widths)
                
                # Create target cells for existing data rows
                for row in self.rows:
                    x_offset = table_left
                    for col_idx, new_w in enumerate(new_widths):
                        cell = row[col_idx]
                        target_cell = cell.get_resized_copy(new_w)
                        
                        # Use scaled width for positioning
                        scaled_w = target_cell.get_width()
                        target_x = x_offset + scaled_w / 2
                        target_cell.move_to([target_x, cell.get_center()[1], 0])
                        resize_animations.append(Transform(cell, target_cell))
                        
                        # Update cell's internal width to match new width
                        cell.cell_width = new_w
                        
                        x_offset += scaled_w
                    
                    # Update row's cell_widths list
                    row.cell_widths = list(new_widths)
                
                # Update stored widths
                self.column_widths = new_widths
        
        # Now create the new row with the updated column widths
        index = len(self.rows) + 1
        new_row = Row(
            values=values,
            cell_widths=self.column_widths,
            cell_height=self.cell_height,
            font_size=self.font_size,
            is_header=False,
            show_border=self.show_border,
            index=index,
        )
        
        # Scale the new row to match the table's current scale
        if abs(scale_factor - 1.0) > 0.001:
            new_row.scale(scale_factor)
        
        # Position the new row cells at correct positions using actual rendered dimensions
        table_left = self.header_row.get_left()[0]
        
        # Calculate y position using actual rendered height
        if len(self.rows) > 0:
            actual_height = self.rows[-1].get_height()
            y_pos = self.rows[-1].get_bottom()[1] - actual_height / 2
        else:
            actual_height = self.header_row.get_height()
            y_pos = self.header_row.get_bottom()[1] - actual_height / 2
        
        # Position each cell at the correct x based on actual rendered widths
        x_offset = table_left
        for col_idx in range(len(self.column_widths)):
            cell = new_row.cells[col_idx]
            # Use actual rendered width of the cell
            cell_width = cell.get_width()
            target_x = x_offset + cell_width / 2
            cell.move_to([target_x, y_pos, 0])
            x_offset += cell_width
        
        # Add to table structure
        self.rows.append(new_row)
        self.add(new_row)
        
        # Combine all animations: resize first, then fade in new row
        appear_animations = [FadeIn(cell) for cell in new_row.cells]
        all_animations = resize_animations + appear_animations
        
        return new_row, all_animations
    
    def delete_row(
        self, 
        index: int
    ) -> Tuple[Row, List]:
        """
        Delete a row from the table.
        
        Args:
            index: Row index (1-indexed, i.e., header is 0, first data row is 1)
        
        Returns:
            Tuple of (deleted_row, animations) where animations includes:
            - FadeOut for the deleted row
            - Shift animations for remaining rows
            - Resize animations if column widths change
            
            All animations can be played together with AnimationGroup.
        
        Example:
            deleted, anims = table.delete_row(1)
            self.play(AnimationGroup(*anims, lag_ratio=0.05))
        """
        if index == 0:
            raise ValueError("Cannot delete header row")
        
        data_index = index - 1
        if data_index < 0 or data_index >= len(self.rows):
            raise IndexError(f"Row index {index} out of range")
        
        # Remove the row from internal lists
        deleted_row = self.rows.pop(data_index)
        self.row_values.pop(data_index)
        
        # Remove from VGroup so it doesn't move with the table
        self.remove(deleted_row)
        
        # Track which rows will be shifted (rows at and after the deleted index)
        rows_to_shift = set(self.rows[data_index:])
        
        # Calculate actual rendered height (accounts for table scaling)
        actual_height = deleted_row.get_height()
        
        # Start with FadeOut for deleted row
        all_animations = [FadeOut(deleted_row)]
        
        # Create shift-up animations for remaining rows
        for row in rows_to_shift:
            all_animations.append(
                row.animate.shift([0, actual_height, 0])
            )
            row.index -= 1
        
        # Recalculate column widths if auto_fit is enabled
        if self.auto_fit:
            new_widths = self.calculate_column_widths()
            
            # Check if any column width changed
            width_changed = any(
                abs(old_w - new_w) > 0.01 
                for old_w, new_w in zip(self.column_widths, new_widths)
            )
            
            if width_changed:
                # Build target table structure with new widths
                # Target positions start from the header's current left edge
                table_left = self.header_row.get_left()[0]
                
                # Calculate actual rendered height (accounts for scale)
                actual_row_height = self.header_row.get_height()
                
                # Create target cells for header
                x_offset = table_left
                for col_idx, new_w in enumerate(new_widths):
                    header_cell = self.header_row[col_idx]
                    target_header = header_cell.get_resized_copy(new_w)
                    
                    # Use scaled width for positioning
                    scaled_w = target_header.get_width()
                    target_x = x_offset + scaled_w / 2
                    target_header.move_to([target_x, header_cell.get_center()[1], 0])
                    all_animations.append(Transform(header_cell, target_header))
                    
                    # Update cell's internal width to match new width
                    header_cell.cell_width = new_w
                    
                    x_offset += scaled_w
                
                # Update header row's cell_widths list
                self.header_row.cell_widths = list(new_widths)
                
                # Create target cells for data rows
                for row in self.rows:
                    x_offset = table_left
                    # Calculate the y-offset: if this row was shifted, use shifted position
                    # Use actual rendered height instead of stored unscaled cell_height
                    y_shift = actual_height if row in rows_to_shift else 0
                    
                    for col_idx, new_w in enumerate(new_widths):
                        cell = row[col_idx]
                        target_cell = cell.get_resized_copy(new_w)
                        
                        # Use scaled width for positioning
                        scaled_w = target_cell.get_width()
                        target_x = x_offset + scaled_w / 2
                        
                        # Use the y position AFTER shift would complete
                        target_y = cell.get_center()[1] + y_shift
                        target_cell.move_to([target_x, target_y, 0])
                        all_animations.append(Transform(cell, target_cell))
                        
                        # Update cell's internal width to match new width
                        cell.cell_width = new_w
                        
                        x_offset += scaled_w
                    
                    # Update row's cell_widths list
                    row.cell_widths = list(new_widths)
                
                # Update stored widths
                self.column_widths = new_widths
        
        return deleted_row, all_animations
    
    def add_column(
        self,
        header: str,
        values: List[str],
        index: Optional[int] = None
    ) -> Tuple[VGroup, List, List]:
        """
        Add a new column to the table.
        
        Args:
            header: Header text for the new column
            values: List of values for the data rows
            index: Insert index (0-indexed). Defaults to end of table.
            
        Returns:
            Tuple of (new_column_group, shift_animations, appear_animations)
        """
        if len(values) != len(self.rows):
            raise ValueError(f"Values length ({len(values)}) must match number of rows ({len(self.rows)})")
        
        if index is None:
            index = len(self.header_values)
        if index < 0:
            index = len(self.header_values) + index + 1
            
        # Update metadata
        self.header_values.insert(index, header)
        for i, row_vals in enumerate(self.row_values):
            row_vals.insert(index, values[i])
            
        # Calculate new column width
        new_width = self.cell_width # Default
        if self.auto_fit:
            # Measure max width of new data
            all_text = [header] + values
            max_text_width = 0
            for text_str in all_text:
                t = Text(text_str, font_size=self.font_size)
                max_text_width = max(max_text_width, t.get_width() + self.padding)
            new_width = max_text_width
            
        self.column_widths.insert(index, new_width)
        
        # Prepare for updates
        new_cells = []
        shift_animations = []
        
        # 1. Update Header
        header_cell = Cell(
            value=header,
            width=new_width,
            height=self.cell_height,
            font_size=self.font_size,
            is_header=True,
            show_border=self.show_border,
        )
        
        # Calculate position
        if index == 0:
            # Place at left of first cell
            target_pos = self.header_row[0].get_left() - np.array([new_width/2, 0, 0])
        else:
            # Place at right of previous cell
            prev_cell = self.header_row[index-1]
            target_pos = prev_cell.get_right() + np.array([new_width/2, 0, 0])
            
        header_cell.move_to(target_pos)
        
        # Shift cells to the right
        cells_to_shift = self.header_row.cells[index:]
        for cell in cells_to_shift:
            shift_animations.append(cell.animate.shift(RIGHT * new_width))
            
        # Insert into row structure
        self.header_row.cells.insert(index, header_cell)
        self.header_row.add(header_cell)
        new_cells.append(header_cell)
        
        # 2. Update Data Rows
        for i, row in enumerate(self.rows):
            cell = Cell(
                value=values[i],
                width=new_width,
                height=self.cell_height,
                font_size=self.font_size,
                is_header=False,
                show_border=self.show_border,
            )
            
            # Position: Align x with header, y with row
            cell.move_to([header_cell.get_center()[0], row.get_center()[1], 0])
            
            # Shift existing cells
            cells_shift = row.cells[index:]
            for c in cells_shift:
                shift_animations.append(c.animate.shift(RIGHT * new_width))
                
            row.cells.insert(index, cell)
            row.add(cell)
            new_cells.append(cell)

        new_column_group = VGroup(*new_cells)
        appear_animations = [FadeIn(cell) for cell in new_cells]
        
        return new_column_group, shift_animations, appear_animations

    def delete_column(
        self,
        index: int
    ) -> Tuple[VGroup, List]:
        """
        Delete a column from the table.
        
        Args:
            index: Column index to delete (0-indexed)
            
        Returns:
            Tuple of (deleted_column_group, shift_animations)
        """
        if index < 0 or index >= len(self.header_values):
            raise IndexError(f"Column index {index} out of range")
            
        # Get width to shift back
        col_width = self.column_widths[index]
        
        # Update metadata
        self.header_values.pop(index)
        for row_vals in self.row_values:
            row_vals.pop(index)
        self.column_widths.pop(index)
        
        deleted_cells = []
        shift_animations = []
        
        # 1. Header
        header_cell = self.header_row.cells.pop(index)
        self.header_row.remove(header_cell) # Remove from VGroup
        deleted_cells.append(header_cell)
        
        # Calculate actual rendered width (accounts for table scaling)
        actual_width = header_cell.get_width()
        
        # Shift remaining cells left
        for cell in self.header_row.cells[index:]:
            shift_animations.append(cell.animate.shift(LEFT * actual_width))
            
        # 2. Data Rows
        for row in self.rows:
            cell = row.cells.pop(index)
            row.remove(cell)
            deleted_cells.append(cell)
            
            for c in row.cells[index:]:
                shift_animations.append(c.animate.shift(LEFT * actual_width))
                
        deleted_group = VGroup(*deleted_cells)
        
        return deleted_group, shift_animations

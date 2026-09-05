# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Cell class for Manim tables.

This module provides the Cell class for table visualizations.

"""

"""
Cell - A single table cell with optional border.
"""

# Manim Community Edition (manim CE) wildcard import for mobjects and constants
from manim import *
import numpy as np


class Cell(VGroup):
    """
    A single cell in a table, containing text and optional border lines.
    
    Args:
        value: The text content of the cell
        width: Width of the cell
        height: Height of the cell
        font_size: Font size for the text
        is_header: If True, renders text in bold with thicker border
        show_border: If True, draws border lines around the cell
        **kwargs: Additional arguments passed to VGroup
    """
    
    def __init__(
        self,
        value: str,
        width: float = 1.5,
        height: float = 0.5,
        font_size: int = 20,
        is_header: bool = False,
        show_border: bool = True,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.value = value
        self.cell_width = width
        self.cell_height = height
        self.font_size = font_size
        self.is_header = is_header
        self.show_border = show_border
        
        # Store color properties for copying
        self._font_color = None
        self._background_color = None
        self._background_opacity = 0.0
        self._border_color = None
        
        # Create invisible bounding box to enforce dimensions
        self.invisible_box = Rectangle(
            width=width,
            height=height,
            stroke_width=0,
            fill_opacity=0,
        )
        self.add(self.invisible_box)
        
        # Create text
        stroke_width = 2 if is_header else 0.5
        if is_header:
            self.text = Text(value, font_size=font_size, weight=BOLD)
        else:
            self.text = Text(value, font_size=font_size)
        self.add(self.text)
        
        # Create border if requested
        if show_border:
            self.border = self.create_border(stroke_width)
            self.add(self.border)
        else:
            self.border = None
    
    def create_border(self, stroke_width: float) -> VGroup:
        """Create the four border lines of the cell."""
        # Calculate corners relative to center
        half_w = self.cell_width / 2
        half_h = self.cell_height / 2
        
        top_left = np.array([-half_w, half_h, 0])
        top_right = np.array([half_w, half_h, 0])
        bottom_left = np.array([-half_w, -half_h, 0])
        bottom_right = np.array([half_w, -half_h, 0])
        
        border = VGroup(
            Line(start=top_left, end=top_right, stroke_width=stroke_width),
            Line(start=top_right, end=bottom_right, stroke_width=stroke_width),
            Line(start=bottom_right, end=bottom_left, stroke_width=stroke_width),
            Line(start=bottom_left, end=top_left, stroke_width=stroke_width),
        )
        return border
    
    def get_value(self) -> str:
        """Return the text value of this cell."""
        return self.value
    
    def set_value(self, new_value: str) -> Text:
        """
        Change the text value of this cell.
        
        Args:
            new_value: The new text content
            
        Returns:
            The new Text mobject (useful for animations like Transform)
        
        Example:
            # Instant change
            cell.set_value("new text")
            
            # Animated change
            old_text = cell.text.copy()
            new_text = cell.set_value("new text")
            self.play(Transform(old_text, new_text))
        """
        self.value = new_value
        
        # Store the old position
        old_position = self.text.get_center()
        
        # Remove old text
        self.remove(self.text)
        
        # Create new text with same styling
        if self.is_header:
            self.text = Text(new_value, font_size=self.font_size, weight=BOLD)
        else:
            self.text = Text(new_value, font_size=self.font_size)
        
        # Position at the same location as the old text
        self.text.move_to(old_position)
        
        self.add(self.text)
        return self.text
    
    def get_resized_copy(self, new_width: float) -> "Cell":
        """
        Create a copy of this cell with a new width.
        The copy is positioned at the same center as this cell.
        Preserves font color, background color, border color, and current scale.
        Useful for animating width changes with Transform.
        
        Args:
            new_width: The new width for the cell (in unscaled units)
            
        Returns:
            A new Cell with the same value and styling but different width,
            scaled to match the current cell's scale
        """
        # Calculate current scale factor using HEIGHT (stable during width resize)
        # Width-based calculation fails after Transform morphs the cell
        scale_factor = self.get_height() / self.cell_height if self.cell_height > 0 else 1.0
        
        new_cell = Cell(
            value=self.value,
            width=new_width,
            height=self.cell_height,
            font_size=self.font_size,
            is_header=self.is_header,
            show_border=self.show_border,
        )
        
        # Copy styling colors BEFORE scaling so they get scaled too
        if self._font_color is not None:
            new_cell.set_font_color(self._font_color)
        if self._background_color is not None:
            new_cell.set_background_color(self._background_color, self._background_opacity)
        if self._border_color is not None:
            new_cell.set_border_color(self._border_color)
        
        # Apply the same scale to match the current cell's scale
        if abs(scale_factor - 1.0) > 0.001:
            new_cell.scale(scale_factor)
        
        new_cell.move_to(self.get_center())
        
        return new_cell
    
    def resize_width(self, new_width: float):
        """
        Resize this cell to a new width (instant, no animation).
        Updates border lines in place.
        
        Args:
            new_width: The new width
        """
        self.cell_width = new_width
        
        # Resize invisible box
        if hasattr(self, 'invisible_box'):
            self.remove(self.invisible_box)
            self.invisible_box = Rectangle(
                width=new_width,
                height=self.cell_height,
                stroke_width=0,
                fill_opacity=0,
            )
            self.add_to_back(self.invisible_box)
        
        # Recreate border with new dimensions
        if self.border is not None:
            self.remove(self.border)
            stroke_width = 2 if self.is_header else 0.5
            self.border = self.create_border(stroke_width)
            self.add(self.border)
    
    def set_font_color(self, color):
        """
        Set the font/text color of this cell.
        
        Args:
            color: A Manim color (e.g., RED, BLUE, "#FF0000")
        """
        self._font_color = color  # Store for copying
        self.text.set_color(color)
        return self
    
    def set_border_color(self, color):
        """
        Set the border line color of this cell.
        
        Args:
            color: A Manim color (e.g., RED, BLUE, "#FF0000")
        """
        self._border_color = color  # Store for copying
        if self.border is not None:
            for line in self.border:
                line.set_color(color)
        return self
    
    def set_background_color(self, color, opacity: float = 0.5):
        """
        Set a background fill color for this cell.
        Creates a filled rectangle behind the text.
        
        Args:
            color: A Manim color (e.g., RED, BLUE, "#FF0000")
        opacity: Opacity of the background (0 to 1)
        """
        # Store for copying
        self._background_color = color
        self._background_opacity = opacity
        
        # Remove existing background if any
        if hasattr(self, 'background') and self.background is not None:
            self.remove(self.background)
        
        # Create background rectangle
        half_w = self.cell_width / 2
        half_h = self.cell_height / 2
        
        self.background = Rectangle(
            width=self.cell_width,
            height=self.cell_height,
            fill_color=color,
            fill_opacity=opacity,
            stroke_width=0,
        )
        self.background.move_to(self.get_center())
        
        # Add behind everything else
        self.add_to_back(self.background)
        return self
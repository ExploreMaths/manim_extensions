# SPDX-FileCopyrightText: 2026 MathItYT
#
# SPDX-License-Identifier: MIT

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Image mobject utilities for neural network visualization."""

from manim import *
import numpy as np
from PIL import Image

class GrayscaleImageMobject(Group):
    """Mobject for creating images in Manim from numpy arrays

    Parameters
    ----------
    numpy_image : np.ndarray
        2D grayscale image data.
    height : float, optional
        Height of the rendered image, by default 2.3.
    """

    def __init__(self, numpy_image, height=2.3):
        super().__init__()
        self.numpy_image = numpy_image
        assert len(np.shape(self.numpy_image)) == 2

        input_image = self.numpy_image[None, :, :]
        # Convert grayscale to rgb version of grayscale
        input_image = np.repeat(input_image, 3, axis=0)
        input_image = np.rollaxis(input_image, 0, start=3)
        self.image_mobject = ImageMobject(
            input_image, 
            image_mode="RBG",
        )
        self.add(self.image_mobject)
        self.image_mobject.set_resampling_algorithm(
            RESAMPLING_ALGORITHMS["nearest"]
        )
        self.image_mobject.scale_to_fit_height(height)

    @classmethod
    def from_path(cls, path, height=2.3):
        """Loads image from path"""
        image = Image.open(path)
        numpy_image = np.asarray(image)

        return cls(numpy_image, height=height)

    @override_animation(Create)
    def create(self, run_time=2):
        return FadeIn(self)

    def scale(self, scale_factor, **kwargs):
        """Scales the image mobject"""
        # super().scale(scale_factor)
        # height = self.height
        self.image_mobject.scale(scale_factor)
        # self.scale_to_fit_height(2)
        # self.apply_points_function_about_point(
        #     lambda points: scale_factor * points, **kwargs
        # )

    def set_opacity(self, opacity):
        """Set the opacity"""
        self.image_mobject.set_opacity(opacity)


class LabeledColorImage(Group):
    """Labeled Color Image

    Parameters
    ----------
    image : Mobject
        The image to label.
    color : ManimColor, optional
        Color of the surrounding rectangle, by default RED.
    label : str, optional
        Text displayed above the image, by default "Positive".
    stroke_width : float, optional
        Stroke width of the surrounding rectangle, by default 5.
    font_size : float, optional
        Font size of the label, by default 24.
    buff : float, optional
        Buffer between the image and the label, by default 0.2.
    """

    def __init__(
        self, image, color=RED, label="Positive", stroke_width=5, font_size=24, buff=0.2
    ):
        super().__init__()
        self.image = image
        self.color = color
        self.label = label
        self.stroke_width = stroke_width
        self.font_size = font_size

        text = Text(label, font_size=self.font_size)
        text.next_to(self.image, UP, buff=buff)
        rectangle = SurroundingRectangle(
            self.image, color=color, buff=0.0, stroke_width=self.stroke_width
        )

        self.add(text)
        self.add(rectangle)
        self.add(self.image)
# SPDX-FileCopyrightText: 2026 MathItYT
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Image mobject utilities for neural network visualization."""

from typing import Any

import numpy as np
from manim import (
    Create,
    FadeIn,
    Group,
    ImageMobject,
    Animation,
    ManimColor,
    RED,
    RESAMPLING_ALGORITHMS,
    SurroundingRectangle,
    Text,
    UP,
    override_animation,
)
from PIL import Image
from manim.typing import PixelArray


def _as_uint8_image(numpy_image: PixelArray) -> PixelArray:
    """Return image data as a ``uint8`` array suitable for Pillow.

    Floating point images are commonly normalized to ``[0, 1]``; those are
    rescaled to ``[0, 255]`` before conversion. Integer images are clipped to
    the valid byte range.

    Parameters
    ----------
    numpy_image
        Image data in grayscale or RGB layout.

    Returns
    -------
        The image data as a ``uint8`` array.
    """
    array = np.asarray(numpy_image)
    if array.dtype == np.uint8:
        return array
    values = np.asarray(numpy_image, dtype=np.float64)
    if np.issubdtype(array.dtype, np.floating) and array.size:
        peak = float(np.nanmax(values))
        if peak <= 1.0:
            values = values * 255.0
    return np.clip(values, 0, 255).astype(np.uint8)


class GrayscaleImageMobject(Group):
    """Mobject for creating images in Manim from numpy arrays.

    Parameters
    ----------
    numpy_image
        2D grayscale image data.
    height
        Height of the rendered image.

    Examples
    --------
    .. manim:: GrayscaleImageMobjectScene
       :save_last_frame:

       import numpy as np
       from manim import *
       from manim_extensions.machine_learning.utils.mobjects.image import GrayscaleImageMobject

       class GrayscaleImageMobjectScene(Scene):
           def construct(self):
               gradient = np.linspace(0, 255, 256).reshape(16, 16).astype(np.uint8)
               self.add(GrayscaleImageMobject(gradient))
    .. doc-example-covers: create, from_path
    """

    def __init__(self, numpy_image: PixelArray, height: float = 2.3) -> None:
        super().__init__()
        self.numpy_image = numpy_image
        assert len(np.shape(self.numpy_image)) == 2

        input_image = _as_uint8_image(self.numpy_image)[None, :, :]
        # Convert grayscale to rgb version of grayscale
        input_image = np.repeat(input_image, 3, axis=0)
        input_image = np.rollaxis(input_image, 0, start=3)
        self.image_mobject = ImageMobject(
            input_image,
            image_mode="RGB",
        )
        self.add(self.image_mobject)
        self.image_mobject.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
        self.image_mobject.scale_to_fit_height(height)

    @classmethod
    def from_path(cls, path: str, height: float = 2.3) -> "GrayscaleImageMobject":
        """Loads image from path.

        Parameters
        ----------
        path
            Path to the image file to load.
        height
            Height of the rendered image.

        Returns
        -------
            Grayscale image mobject built from the loaded image.
        """
        image = Image.open(path)
        numpy_image = np.asarray(image)

        return cls(numpy_image, height=height)

    @override_animation(Create)
    def create(self, run_time: float = 2) -> Animation:
        """Create the image mobject by fading it in.

        Parameters
        ----------
        run_time
            Duration of the fade-in animation.

        Returns
        -------
            Fade-in animation of the image mobject.
        """
        return FadeIn(self)

    def scale(  # intentionally returns None instead of the group
        self, scale_factor: float, **kwargs: Any
    ) -> Any:
        """Scales the image mobject.



        scale_factor
            Factor by which to scale the image mobject.
        **kwargs
            Additional keyword arguments for scaling.




            The resulting value.
        """
        # super().scale(scale_factor)
        # height = self.height
        self.image_mobject.scale(scale_factor)
        # self.scale_to_fit_height(2)
        # self.apply_points_function_about_point(
        #     lambda points: scale_factor * points, **kwargs
        # )

    def set_opacity(self, opacity: float) -> Any:
        """Set the opacity.



        opacity
            Opacity to apply to the image mobject.




            The resulting value.
        """
        self.image_mobject.set_opacity(opacity)


class LabeledColorImage(Group):
    """An image with a colored frame and a text label above it.

    The frame and label are grouped with the image so the whole card can be
    positioned, scaled or animated as one mobject.

    Parameters
    ----------
    image
        The image to label.
    color
        Color of the surrounding rectangle.
    label
        Text displayed above the image.
    stroke_width
        Stroke width of the surrounding rectangle.
    font_size
        Font size of the label.
    buff
        Buffer between the image and the label.

    Examples
    --------
    .. manim:: LabeledColorImageScene
       :save_last_frame:

       import numpy as np
       from manim import *
       from manim_extensions.machine_learning.utils.mobjects.image import LabeledColorImage

       class LabeledColorImageScene(Scene):
           def construct(self):
               image = ImageMobject(np.zeros((48, 48, 3), dtype=np.uint8)).scale(2.5)
               labeled = LabeledColorImage(image, color=GREEN, label="Cat")
               labeled.scale(6)
               self.add(labeled)
    """

    def __init__(
        self,
        image: ImageMobject,
        color: ManimColor = RED,
        label: str = "Positive",
        stroke_width: float = 5,
        font_size: float = 24,
        buff: float = 0.2,
    ) -> None:
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

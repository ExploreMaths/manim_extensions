# SPDX-FileCopyrightText: 2026 MathItYT
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
# patched: lazy-import matplotlib (ml extra)

"""Plotting utilities for neural network visualization."""

from __future__ import annotations
from typing import TYPE_CHECKING

import io

import numpy as np
from manim import ImageMobject
from PIL import Image

from ....utils.deps import require

if TYPE_CHECKING:
    from matplotlib.figure import Figure


def convert_matplotlib_figure_to_image_mobject(
    fig: Figure, dpi: int = 200
) -> ImageMobject:
    """Takes a matplotlib figure and makes an image mobject from it.

    Parameters
    ----------
    fig
        Matplotlib figure.
    dpi
        Resolution of the rendered figure in dots per inch.

    Returns
    -------
        Image mobject containing the rendered figure.

    Examples
    --------
    .. manim:: MatplotlibFigureExample
       :save_last_frame:

       import matplotlib.pyplot as plt
       import numpy as np
       from manim import *
       from manim_extensions.machine_learning.utils.mobjects.plotting import (
           convert_matplotlib_figure_to_image_mobject,
       )

       class MatplotlibFigureExample(Scene):
           def construct(self):
               fig, ax = plt.subplots(figsize=(4, 3))
               x = np.linspace(0, 2 * np.pi, 100)
               ax.plot(x, np.sin(x), color="tab:blue")
               ax.set_title("sin(x)")
               image = convert_matplotlib_figure_to_image_mobject(fig)
               image.scale_to_fit_height(4)
               self.add(image)
    """
    plt = require("ml", "matplotlib.pyplot")

    fig.tight_layout(pad=0)
    # plt.axis('off')
    fig.canvas.draw()
    # Save data into a buffer
    image_buffer = io.BytesIO()
    plt.savefig(image_buffer, format="png", dpi=dpi)
    # Reopen in PIL and convert to numpy
    pil_image = Image.open(image_buffer).convert("RGB")
    image = np.asarray(pil_image)
    # Convert it to an image mobject
    image_mobject = ImageMobject(image, image_mode="RGB")

    return image_mobject

# SPDX-FileCopyrightText: 2026 MathItYT
#
# SPDX-License-Identifier: MIT

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
# patched: lazy-import matplotlib (ml extra)
"""Plotting utilities for neural network visualization."""

import io
from types import ModuleType
from typing import TYPE_CHECKING, cast

import numpy as np
from manim import ImageMobject
from PIL import Image

from ....utils.deps import require

if TYPE_CHECKING:
    from matplotlib.figure import Figure


def convert_matplotlib_figure_to_image_mobject(
    fig: "Figure", dpi: int = 200
) -> ImageMobject:
    """Takes a matplotlib figure and makes an image mobject from it.

    Parameters
    ----------
    fig : matplotlib figure
        Matplotlib figure.
    dpi : int, optional
        Resolution of the rendered figure in dots per inch, by default 200.

    Returns
    -------
    ImageMobject
        Image mobject containing the rendered figure.
    """
    plt = cast(ModuleType, require("ml", "matplotlib.pyplot"))

    fig.tight_layout(pad=0)
    # plt.axis('off')
    fig.canvas.draw()
    # Save data into a buffer
    image_buffer = io.BytesIO()
    plt.savefig(image_buffer, format='png', dpi=dpi)
    # Reopen in PIL and convert to numpy
    pil_image = Image.open(image_buffer)
    image = np.asarray(pil_image)
    # Convert it to an image mobject
    image_mobject = ImageMobject(image, image_mode="RGB")

    return image_mobject

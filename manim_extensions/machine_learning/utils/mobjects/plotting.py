# SPDX-FileCopyrightText: 2026 MathItYT
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
# patched: lazy-import matplotlib (ml extra), matplotlib figure converter exposed as an ImageMobject subclass

"""Plotting utilities for neural network visualization."""

from __future__ import annotations
from typing import TYPE_CHECKING, Any

import io

import numpy as np
from manim import ImageMobject
from PIL import Image

from ....utils.deps import require

if TYPE_CHECKING:
    from matplotlib.figure import Figure


class MatplotlibFigureImage(ImageMobject):
    """A matplotlib figure rendered as an image mobject.

    Parameters
    ----------
    fig
        Matplotlib figure.
    dpi
        Resolution of the rendered figure in dots per inch.
    **kwargs
        Keyword arguments forwarded to
        :class:`~manim.mobject.types.image_mobject.ImageMobject`.

    Examples
    --------
    .. manim:: MatplotlibFigure
       :save_last_frame:

       import matplotlib.pyplot as plt
       import numpy as np
       from manim import *
       from manim_extensions.machine_learning.utils.mobjects.plotting import (
           MatplotlibFigureImage,
       )

       class MatplotlibFigure(Scene):
           def construct(self):
               fig, ax = plt.subplots(figsize=(4, 3))
               x = np.linspace(0, 2 * np.pi, 100)
               ax.plot(x, np.sin(x), color="tab:blue")
               ax.set_title("sin(x)")
               image = MatplotlibFigureImage(fig)
               image.scale_to_fit_height(4)
               self.add(image)
    """

    def __init__(
        self, fig: Figure, dpi: int = 200, **kwargs: Any
    ) -> (
        None
    ):  # explicit-any-ok: forwarded unchanged through Manim's untyped **kwargs boundary
        plt = require("ml", "matplotlib.pyplot")

        fig.tight_layout(pad=0)
        # plt.axis('off')
        fig.canvas.draw()
        # Save data into a buffer
        image_buffer = io.BytesIO()
        plt.savefig(image_buffer, format="png", dpi=dpi)
        # Reopen with PIL and convert to a NumPy array
        pil_image = Image.open(image_buffer).convert("RGB")
        image = np.asarray(pil_image)
        kwargs.setdefault("image_mode", "RGB")
        super().__init__(image, **kwargs)

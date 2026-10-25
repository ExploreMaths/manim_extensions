# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Workaround for a manim 0.21/0.22 camera regression.

``Camera.display_image_mobject`` builds its transparent overlay with
``Image.fromarray(np.zeros((height, width)), mode="RGBA")`` -- a 2-D
array passed as RGBA, which Pillow rejects with ``Invalid mode for data
type``. This makes every scene containing an :class:`~manim.ImageMobject`
fail to render. Until manim fixes it upstream, patch Pillow's
``fromarray`` so that a 2-D array passed with ``mode="RGBA"`` is expanded
to 4 channels -- that pattern occurs only in the buggy camera call, so
normal ``fromarray`` uses are unaffected.
"""

import numpy as np
from PIL import Image as _PILImage

_original_fromarray = _PILImage.fromarray


def _patched_fromarray(obj, mode=None):
    if mode == "RGBA" and getattr(obj, "ndim", 0) == 2:
        obj = np.repeat(obj[:, :, None], 4, axis=2).astype(np.uint8)
    return _original_fromarray(obj, mode=mode)


def apply_manim_image_patch() -> None:
    """Monkey-patch Pillow's fromarray to tolerate 2-D RGBA input."""
    _PILImage.fromarray = _patched_fromarray

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
# patched: lazy-import pymunk (physics extra)
"""Image-to-shape utilities for Pymunk physics.

This module provides functions for converting images into Pymunk collision
shapes. Both transparent-background and solid-color images are handled.
"""

import numpy as np
from PIL import Image, ImageFilter, ImageOps

from ...utils.deps import require


def get_normalized_convex_polygons(
    pixel_array: np.ndarray, base_px_width: int = 512.0, target_cell_size: int = 4, img_manim_w: float = 8, img_manim_h: float = 14.22
):
    """Extract normalized convex polygons from a pixel array.

    Uses the marching-squares algorithm with convex decomposition to extract
    collision-ready convex polygons from an image. Automatically distinguishes
    transparent-background from solid-color images.

    Parameters
    ----------
    pixel_array : np.ndarray
        Input image pixel array of shape ``[H, W, C]``.
    base_px_width : int, optional
        Base width for downsampling, defaults to 512.0.
            Controls sampling precision.
    target_cell_size : float, optional
        Target cell size for the marching-squares grid, defaults to 4.
            Controls grid density.
    img_manim_w : float, optional
        Manim frame width, defaults to 8.
            Used for coordinate mapping.
    img_manim_h : float, optional
        Manim frame height, defaults to 14.22.
            Used for coordinate mapping.

    Returns
    -------
    list
        List of convex polygons in Manim coordinates, each polygon being a
        list of vertex coordinates.
    """
    pymunk = require("physics", "pymunk")
    from pymunk.autogeometry import march_soft, simplify_vertexes, convex_decomposition

    # 1. Get base dimensions
    orig_h, orig_w = pixel_array.shape[:2]
    is_rgba = pixel_array.shape[2] == 4 if len(pixel_array.shape) > 2 else False

    actual_base_width = min(base_px_width, orig_w)
    scale_factor = orig_w / actual_base_width
    actual_base_height = int(orig_h / scale_factor)

    # 2. Heuristic: "transparent background" or "solid-color with alpha"?
    use_alpha_mask = False
    if is_rgba:
        alpha_channel = pixel_array[:, :, 3]
        # Compute transparent pixel ratio: if > 1%, treat as cutout with transparent bg
        transparent_ratio = np.mean(alpha_channel < 32)
        if transparent_ratio > 0.1:
            use_alpha_mask = True

    # 3. Generate Mask based on heuristic
    if use_alpha_mask:
        # --- Path A: Transparent background ---
        # Use alpha channel directly — more reliable than color analysis
        img_obj = Image.fromarray(pixel_array[:, :, 3]).convert("L")
        img_resized = img_obj.resize(
            (int(actual_base_width), actual_base_height), Image.Resampling.LANCZOS
        )
        mask_np = np.where(np.array(img_resized) > 128, 255, 0).astype(np.uint8)
    else:
        # --- Path B: Solid-color background (preserves original contrast-stretch logic) ---
        img_rgb = Image.fromarray(pixel_array[:, :, :3].astype("uint8")).convert("L")
        img_obj = ImageOps.autocontrast(img_rgb, cutoff=0.5)
        img_resized = img_obj.resize(
            (int(actual_base_width), actual_base_height), Image.Resampling.LANCZOS
        )
        img_np = np.array(img_resized)

        # Ring-shaped border sampling
        border_pixels = np.concatenate(
            [img_np[0, :], img_np[-1, :], img_np[:, 0], img_np[:, -1]]
        )
        bg_color = np.median(border_pixels)
        bg_std = np.std(border_pixels)
        diff = np.abs(img_np.astype(np.int16) - bg_color)
        dynamic_threshold = max(10, bg_std * 3)
        mask_np = np.where(diff > dynamic_threshold, 255, 0).astype(np.uint8)

    # 4. Post-process and sample
    mask = Image.fromarray(mask_np)
    # Closing operation: bridge broken highlight regions
    mask = mask.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))

    def sample_func(point: np.ndarray):
        """Return the mask value at the given coordinate.

        Parameters
        ----------
        point : tuple
            Coordinate :math:`(x, y)`.

        Returns
        -------
        int
            Mask value at that point (0 or 255).
        """
        x, y = int(point[0]), int(point[1])
        if 0 <= x < actual_base_width and 0 <= y < actual_base_height:
            return mask.getpixel((x, y))
        return 0

    bb = pymunk.BB(0, 0, actual_base_width - 1, actual_base_height - 1)
    x_samples = max(20, int(actual_base_width / target_cell_size))
    y_samples = max(20, int(actual_base_height / target_cell_size))

    pl_set = march_soft(bb, x_samples, y_samples, 128.0, sample_func)

    # 4. Vertex mapping reconstruction
    pixel_polygons = []
    for polyline in pl_set:
        simplified = simplify_vertexes(polyline, 0.4)
        if len(simplified) > 3:
            try:
                parts = convex_decomposition(simplified, 0.1)
                for part in parts:
                    pixel_polygons.append(
                        [(p[0] * scale_factor, p[1] * scale_factor) for p in part]
                    )
            except Exception:
                # convex decomposition failed for this shape; skip it
                continue

    # Coordinate conversion
    manim_polygons = map_polygons_to_manim(
        pixel_polygons,
        img_px_w=orig_w,
        img_px_h=orig_h,
        img_manim_w=img_manim_w,
        img_manim_h=img_manim_h,
    )
    return manim_polygons


def map_polygons_to_manim(polygons: list, img_px_w: int, img_px_h: int, img_manim_w: float, img_manim_h: float):
    """Map pixel-coordinate polygons into Manim coordinates.

    Performs the coordinate transform from image pixel space into Manim's
    Cartesian scene coordinates.

    Parameters
    ----------
    polygons : list
        List of polygons in pixel coordinates.
    img_px_w : int
        Image width in pixels.
    img_px_h : int
        Image height in pixels.
    img_manim_w : float
        Manim frame width.
    img_manim_h : float
        Manim frame height.

    Returns
    -------
    list
        List of polygons in Manim coordinates.
    """
    manim_polygons = []
    for poly in polygons:
        manim_vertices = []
        for x, y in poly:
            # Apply coordinate mapping
            m_x = (x / img_px_w - 0.5) * img_manim_w
            m_y = (0.5 - y / img_px_h) * img_manim_h
            manim_vertices.append([m_x, m_y])
        manim_polygons.append(manim_vertices)
    return manim_polygons

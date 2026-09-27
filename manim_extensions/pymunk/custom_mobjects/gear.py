# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
# patched: lazy-import pymunk (physics extra)
"""Gear Mobject for Pymunk physics simulations."""

from manim import Circle, DEGREES, Exclusion, Polygon, Union, VMobject
import numpy as np

class Gear(VMobject):
    """A gear-shaped Mobject with teeth and an optional center hole.

    Parameters
    ----------
    num_teeth
        The number of teeth distributed around the gear. Defaults to ``12``.
    radius
        The radius of the base disc of the gear. Defaults to ``1.0``.
    tooth_height
        The height of each tooth, measured from the base disc outward.
        Defaults to ``0.4``.
    width_factor
        The ratio of tooth width to the space available for a single tooth.
        Defaults to ``0.5`` (half tooth, half gap).
    roundness
        The corner rounding radius applied to each tooth. Set to ``0`` for
        sharp corners. Defaults to ``0.05``.
    hole_radius
        The radius of the hole cut out of the gear's center. Set to ``0`` for
        a solid gear. Defaults to ``0.1``.
    **kwargs
        Forwarded to the parent :class:`~manim.mobject.types.vectorized_mobject.VMobject`.

    Examples
    --------
    .. manim:: PymunkGearDocExample
       :save_last_frame:

       from manim import *
       from manim_extensions.pymunk import *

       class PymunkGearDocExample(Scene):
           def construct(self):
               gears = VGroup(
                   Gear(num_teeth=8, radius=0.8, color=BLUE),
                   Gear(num_teeth=12, radius=1.0, tooth_height=0.5, color=GREEN),
                   Gear(num_teeth=16, radius=0.9, hole_radius=0, color=RED),
               )
               gears.arrange(RIGHT, buff=0.8)
               self.add(gears)
    """

    def __init__(
        self,
        num_teeth: int = 12,
        radius: float = 1.0,
        tooth_height: float = 0.4,
        width_factor: float = 0.5,  # Tooth width as fraction of tooth pitch space; 0.5 = half tooth, half gap
        roundness: float = 0.05,
        hole_radius: float = 0.1,
        **kwargs
    ):
        """Initialize a gear-shaped VMobject with configurable teeth count,
        radius, tooth height, width factor, corner roundness, and center hole.
        """
        super().__init__(**kwargs)
        
        # Auto-compute optimal tooth width
        # Formula: (2 * PI * r / n) * ratio factor
        auto_width = (np.pi * radius / num_teeth) * width_factor
        
        # 1. Create base disc
        res = Circle(radius=radius)
        
        # 2. Prepare all teeth
        teeth_to_union = []
        for i in range(num_teeth):
            # Use auto-computed width
            p1 = [-auto_width, radius, 0]
            p2 = [auto_width, radius, 0]
            p3 = [0, radius + tooth_height, 0]
            
            tooth = Polygon(p1, p2, p3)
            
            dist = radius + tooth_height/2 - 0.05
            angle = i * (360 / num_teeth) * DEGREES
            
            pos = [dist * np.cos(angle), dist * np.sin(angle), 0]
            tooth.move_to(pos)
            tooth.rotate(angle - 90 * DEGREES)
            
            if roundness > 0:
                tooth.round_corners(roundness)
            
            teeth_to_union.append(tooth)
        
        # 3. Boolean operations once (much faster than looping Union)
        res = Union(res, *teeth_to_union)
        
        # 4. Cut holes
        if hole_radius > 0:
            hole = Circle(radius=hole_radius)
            res = Exclusion(res, hole)
        
        self.set_points(res.get_points())
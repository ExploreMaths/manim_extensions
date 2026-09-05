# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Gear Mobject for Pymunk physics simulations."""

from manim import *
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
    """

    def __init__(
        self,
        num_teeth: int = 12,
        radius: float = 1.0,
        tooth_height: float = 0.4,
        width_factor: float = 0.5,  # 齿宽占单齿空间的比例，0.5 表示半齿半空
        roundness: float = 0.05,
        hole_radius: float = 0.1,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        # 自动计算最佳齿宽
        # 公式: (2 * PI * r / n) * 比例因子
        auto_width = (np.pi * radius / num_teeth) * width_factor
        
        # 1. 创建基础圆盘
        res = Circle(radius=radius)
        
        # 2. 准备所有齿
        teeth_to_union = []
        for i in range(num_teeth):
            # 使用自动计算的宽度
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
        
        # 3. 一次性进行布尔运算 (比循环 Union 快得多)
        res = Union(res, *teeth_to_union)
        
        # 4. 挖洞
        if hole_radius > 0:
            hole = Circle(radius=hole_radius)
            res = Exclusion(res, hole)
        
        self.set_points(res.get_points())
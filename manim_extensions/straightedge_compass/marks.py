# SPDX-FileCopyrightText: 2026 manim-straightedge-compass contributors
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Point markers and labels."""

from __future__ import annotations
from typing import Any

import numpy as np
from manim import Dot, MathTex, VGroup, UP

from .geometry import as_point

POINT_COLOR = "#FF6B6B"
LABEL_COLOR = "#F2F5F9"


class MarkedPoint(VGroup):
    """A coloured dot with an optional math label."""

    def __init__(
        self,
        point: Any,
        label: str = None,
        direction: Any = 0.42 * UP,
        color: Any = POINT_COLOR,
        radius: float = 0.06,
        font_size: int = 34,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        point = as_point(point)
        self.dot = Dot(point, radius=radius, color=color, z_index=15)
        self.add(self.dot)
        self.label_mob = None
        if label is not None:
            self.label_mob = MathTex(
                label, font_size=font_size, color=LABEL_COLOR, z_index=15
            )
            d = np.asarray(direction, dtype=float)
            n = np.linalg.norm(d[:2])
            if n > 0:
                d = d / n
                self.label_mob.move_to(point + d * (radius + 0.28))
            else:
                self.label_mob.next_to(self.dot, UP, buff=0.12)
            self.add(self.label_mob)

    @property
    def point(self) -> Any:
        """point."""
        return self.dot.get_center()

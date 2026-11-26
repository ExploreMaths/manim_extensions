# SPDX-FileCopyrightText: 2026 MathItYT
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Machine learning visualizations for Manim.

This module provides various machine learning related visualizations
including neural networks, decision trees, and diffusion models.
"""

from typing import Any, cast

from argparse import Namespace
from manim import *
import manim
from .utils.colorschemes.colorschemes import light_mode, dark_mode, ColorScheme


class ManimMLConfig:
    """Global configuration for the machine learning visualizations.

    Holds the active :class:`~manim_extensions.machine_learning.utils.colorschemes.colorschemes.ColorScheme` and the default 3D camera
    orientation used by neural-network scenes.

    Parameters
    ----------
    default_color_scheme
        Colour scheme applied to the machine learning visualisations.

    Examples
    --------
    .. manim:: ManimMLConfigOverview
       :save_last_frame:

       from manim import *
       from manim_extensions.machine_learning import ManimMLConfig

       ManimMLConfigTarget = ManimMLConfig

       class ManimMLConfigOverview(Scene):
           def construct(self):
               public = [n for n in dir(ManimMLConfigTarget) if not n.startswith("_")]
               card = VGroup(
                   Text('ManimMLConfig', font_size=36),
                   Text('module: manim_extensions.machine_learning', font_size=18, color=GREY),
                   Text('Global configuration for the machine learning visualizations', font_size=22),
                   Text("API: " + ", ".join(public[:6]), font_size=18, color=BLUE),
               ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
               card.scale_to_fit_width(11.5).move_to(ORIGIN)
               frame = RoundedRectangle(
                   width=12.1, height=card.height + 0.5, corner_radius=0.2, color=BLUE_D
               ).move_to(card)
               self.add(frame, card)

    .. code-block:: python

        from manim_extensions.machine_learning import ManimMLConfig

        config = ManimMLConfig()
    """

    def __init__(self, default_color_scheme: ColorScheme = dark_mode) -> None:
        self._color_scheme = default_color_scheme
        self.three_d_config = Namespace(
            three_d_x_rotation=90 * DEGREES,
            three_d_y_rotation=0 * DEGREES,
            rotation_angle=75 * DEGREES,
            rotation_axis=[0.02, 1.0, 0.0],
            # rotation_axis = [0.0, 0.9, 0.0]
            # rotation_axis = [0.0, 0.9, 0.0]
        )

    @property
    def color_scheme(self) -> ColorScheme:
        """Return the active color scheme.

        Returns
        -------
            The scheme currently applied to the config.
        """
        return self._color_scheme

    @color_scheme.setter
    def color_scheme(self, value: ColorScheme | str) -> None:
        """Set the active color scheme and apply its background color.

        Parameters
        ----------
        value
            A :class:`~manim_extensions.machine_learning.utils.colorschemes.colorschemes.ColorScheme` instance, or the name of a builtin
            scheme (``"dark_mode"`` / ``"light_mode"``).

        Raises
        ------
        ValueError
            Raised when ``value`` is a string other than ``"dark_mode"``
            or ``"light_mode"``.
        """
        if isinstance(value, str):
            if value == "dark_mode":
                self._color_scheme = dark_mode
            elif value == "light_mode":
                self._color_scheme = light_mode
            else:
                raise ValueError(
                    "Color scheme must be either 'dark_mode' or 'light_mode'"
                )
        elif isinstance(value, ColorScheme):
            self._color_scheme = value

        manim.config.background_color = self.color_scheme.background_color


# These are accessible from the manim_ml namespace
#: Shared ManimML configuration singleton exposed from the package namespace.
config = ManimMLConfig()  # type: ignore[assignment]  # intentionally shadows manim's star-imported config

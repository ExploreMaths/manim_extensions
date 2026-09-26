# SPDX-FileCopyrightText: 2026 MathItYT
#
# SPDX-License-Identifier: MIT

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Machine learning visualizations for Manim.

This module provides various machine learning related visualizations
including neural networks, decision trees, and diffusion models.

"""

from argparse import Namespace
from manim import *
import manim
from .utils.colorschemes.colorschemes import light_mode, dark_mode, ColorScheme

class ManimMLConfig:
    """Global configuration for the machine learning visualizations.

    Holds the active :class:`~manim_extensions.machine_learning.ManimMLConfig.ColorScheme` and the default 3D camera
    orientation used by neural-network scenes.
    """

    def __init__(self, default_color_scheme: ColorScheme = dark_mode) -> None:
        """Initialize the configuration.

        Parameters
        ----------
        default_color_scheme : ColorScheme, optional
            Color scheme used before any override. Defaults to
            ``dark_mode``.
        """
        self._color_scheme = default_color_scheme
        self.three_d_config = Namespace(
            three_d_x_rotation = 90 * DEGREES,
            three_d_y_rotation = 0 * DEGREES,
            rotation_angle = 75 * DEGREES,
            rotation_axis = [0.02, 1.0, 0.0]
            # rotation_axis = [0.0, 0.9, 0.0]
            #rotation_axis = [0.0, 0.9, 0.0]
        )

    @property
    def color_scheme(self) -> ColorScheme:
        """The currently active color scheme."""
        return self._color_scheme

    @color_scheme.setter
    def color_scheme(self, value: ColorScheme | str) -> None:
        """Set the active color scheme and apply its background color.

        Parameters
        ----------
        value : ColorScheme or str
            A :class:`~manim_extensions.machine_learning.ManimMLConfig.ColorScheme` instance, or the name of a builtin
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

# These are accesible from the manim_ml namespace
config = ManimMLConfig()  # type: ignore[assignment] # intentionally shadows manim's star-imported config
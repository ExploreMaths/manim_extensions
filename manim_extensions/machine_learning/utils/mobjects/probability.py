# SPDX-FileCopyrightText: 2026 MathItYT
#
# SPDX-License-Identifier: MIT

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Probability distribution utilities for neural network visualization."""

from typing import Any

import numpy as np
from manim import Axes, Ellipse, ManimColor, ORANGE, VGroup
from numpy.typing import NDArray


class GaussianDistribution(VGroup):
    """Object for drawing a Gaussian distribution.

    Parameters
    ----------
    axes : Axes
        Manim axes the distribution is drawn in.
    mean : np.ndarray, optional
        Mean of the distribution; defaults to [0.0, 0.0].
    cov : np.ndarray, optional
        Covariance matrix of the distribution; defaults to the identity.
    dist_theme : str, optional
        Drawing style; "gaussian" draws confidence ellipses and "ellipse" a
        single ellipse, by default "gaussian".
    color : ManimColor, optional
        Color of the ellipses, by default ORANGE.
    **kwargs
        Forwarded to the parent class.

    Examples
    --------
    .. manim:: GaussianDistributionDocExample
       :save_last_frame:

       from manim import *
       import numpy as np
       from manim_extensions.machine_learning.utils.mobjects.probability import (
           GaussianDistribution,
       )

       class GaussianDistributionDocExample(Scene):
           def construct(self):
               axes = Axes(
                   x_range=[-3, 3],
                   y_range=[-3, 3],
                   x_length=6,
                   y_length=6,
                   tips=False,
               )
               gaussian = GaussianDistribution(
                   axes,
                   mean=np.array([0.5, -0.5]),
                   cov=np.array([[1.2, 0.6], [0.6, 0.8]]),
               )
               self.add(axes, gaussian)
    """

    def __init__(
        self,
        axes: Axes,
        mean: NDArray[np.float64] | None = None,
        cov: NDArray[np.float64] | None = None,
        dist_theme: str = "gaussian",
        color: ManimColor = ORANGE,
        **kwargs: Any,
    ) -> None:
        """Initialize the distribution plot."""
        super(VGroup, self).__init__(**kwargs)
        self.axes = axes
        if mean is None:
            mean = np.array([0.0, 0.0])
        if cov is None:
            cov = np.array([[1, 0], [0, 1]])
        self.mean = mean
        self.cov = cov
        self.dist_theme = dist_theme
        self.color = color
        # Make the Gaussian
        if self.dist_theme == "gaussian":
            self.ellipses = self.construct_gaussian_distribution(
                self.mean, self.cov, color=self.color
            )
            self.add(self.ellipses)
        elif self.dist_theme == "ellipse":
            self.ellipses = self.construct_simple_gaussian_ellipse(
                self.mean, self.cov, color=self.color
            )
            self.add(self.ellipses)
        else:
            raise Exception(f"Uncrecognized distribution theme: {self.dist_theme}")

    """  
    @override_animation(Create)
    def _create_gaussian_distribution(self):
        return Create(self)
    """

    def compute_covariance_rotation_and_scale(
        self, covariance: NDArray[np.float64]
    ) -> tuple[float, float, float]:
        """Compute the rotation angle and axes of the covariance ellipse.

        Parameters
        ----------
        covariance : np.ndarray
            2D covariance matrix of the Gaussian distribution.

        Returns
        -------
        tuple[float, float, float]
            Rotation angle, width, and height of the covariance ellipse
            in frame coordinates.
        """
        def eigsorted(
            cov: NDArray[np.float64],
        ) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
            """
            Eigenvalues and eigenvectors of the covariance matrix.
            """
            vals, vecs = np.linalg.eigh(cov)
            order = vals.argsort()[::-1]
            return vals[order], vecs[:, order]

        def cov_ellipse(cov: NDArray[np.float64], nstd: float) -> tuple[float, float, float]:
            """
            Source: http://stackoverflow.com/a/12321306/1391441
            """

            vals, vecs = eigsorted(cov)
            theta = np.degrees(np.arctan2(*vecs[:, 0][::-1]))

            # Width and height are "full" widths, not radius
            width, height = 2 * nstd * np.sqrt(vals)

            return width, height, theta

        width, height, angle = cov_ellipse(covariance, 1)
        scale_factor = (
            np.abs(self.axes.x_range[0] - self.axes.x_range[1]) / self.axes.x_length
        )
        width /= scale_factor
        height /= scale_factor
        return angle, width, height

    def construct_gaussian_distribution(
        self,
        mean: NDArray[np.float64],
        covariance: NDArray[np.float64],
        color: ManimColor = ORANGE,
        num_ellipses: int = 4,
    ) -> VGroup:
        """Returns a 2d Gaussian distribution object with given mean and covariance.

        Parameters
        ----------
        mean : np.ndarray
            Mean of the Gaussian distribution.
        covariance : np.ndarray
            Covariance matrix of the Gaussian distribution.
        color : ManimColor, optional
            Color of the ellipses, by default ORANGE.
        num_ellipses : int, optional
            Number of concentric confidence ellipses, by default 4.

        Returns
        -------
        VGroup
            Group of concentric ellipses visualizing the distribution.
        """
        # map mean and covariance to frame coordinates
        mean = self.axes.coords_to_point(*mean)
        # Figure out the scale and angle of rotation
        rotation, width, height = self.compute_covariance_rotation_and_scale(covariance)
        # Make covariance ellipses
        opacity = 0.0
        ellipses = VGroup()
        for ellipse_number in range(num_ellipses):
            opacity += 1.0 / num_ellipses
            ellipse_width = width * (1 - opacity)
            ellipse_height = height * (1 - opacity)
            ellipse = Ellipse(
                width=ellipse_width,
                height=ellipse_height,
                color=color,
                fill_opacity=opacity,
                stroke_width=2.0,
            )
            ellipse.move_to(mean)
            ellipse.rotate(rotation)
            ellipses.add(ellipse)

        return ellipses

    def construct_simple_gaussian_ellipse(
        self,
        mean: NDArray[np.float64],
        covariance: NDArray[np.float64],
        color: ManimColor = ORANGE,
    ) -> VGroup:
        """Returns a 2d Gaussian distribution object with given mean and covariance.

        Parameters
        ----------
        mean : np.ndarray
            Mean of the Gaussian distribution.
        covariance : np.ndarray
            Covariance matrix of the Gaussian distribution.
        color : ManimColor, optional
            Color of the ellipse, by default ORANGE.

        Returns
        -------
        VGroup
            Group containing the single ellipse visualizing the distribution.
        """
        # Map mean and covariance to frame coordinates
        mean = self.axes.coords_to_point(*mean)
        angle, width, height = self.compute_covariance_rotation_and_scale(covariance)
        # Make covariance ellipses
        ellipses = VGroup()
        opacity = 0.4
        ellipse = Ellipse(
            width=width,
            height=height,
            color=color,
            fill_opacity=opacity,
            stroke_width=1.0,
        )
        ellipse.move_to(mean)
        ellipse.rotate(angle)
        ellipses.add(ellipse)
        ellipses.set_z_index(3)

        return ellipses
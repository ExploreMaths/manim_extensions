"""3D and 2D Waves module."""

from __future__ import annotations
from typing import Iterable, Optional

from manim import *
from manim.mobject.opengl.opengl_compatibility import ConvertToOpenGL

__all__ = [
    "LinearWave",
    "RadialWave",
    "StandingWave",
]


class RadialWave(Surface, metaclass=ConvertToOpenGL):
    """Wave surface that radiates from one or more point sources.

    The surface height is driven by a sinusoidal disturbance pattern based on the
    source positions and the current time.

    Parameters
    ----------
    sources
        The source points that generate the wave disturbance.
    wavelength
        The wavelength of the wave.
    period
        The period of the wave oscillation.
    amplitude
        The amplitude of the wave displacement.
    x_range
        The x-domain range used to construct the surface.
    y_range
        The y-domain range used to construct the surface.
    kwargs
        Additional keyword arguments passed to :class:`~manim.mobject.three_dimensions.Surface`.

    Examples
    --------

    .. manim:: RadialWaveExample
      :save_last_frame:

        from manim import *
        from manim_extensions.physics.wave import RadialWave

        class RadialWaveExample(Scene):
            def construct(self):
                wave = RadialWave(
                    ORIGIN + UP * 2,
                    wavelength=2,
                    amplitude=0.3,
                )
                self.add(wave)
"""

    def __init__(
        self,
        *sources: Optional[np.ndarray],
        wavelength: float = 1,
        period: float = 1,
        amplitude: float = 0.1,
        x_range: Iterable[float] = [-5, 5],
        y_range: Iterable[float] = [-5, 5],
        **kwargs,
    ) -> None:
        """Initialize a radial wave surface."""
        self.wavelength = wavelength
        self.period = period
        self.amplitude = amplitude
        self.time = 0
        self.kwargs = kwargs
        self.sources = sources

        super().__init__(
            lambda u, v: np.array([u, v, self._wave_z(u, v, sources)]),
            u_range=x_range,
            v_range=y_range,
            **kwargs,
        )

    def _wave_z(self, u: float, v: float, sources: Iterable[np.ndarray]) -> float:
        """Compute the wave height at position ``(u, v)`` summed over all sources.

        Parameters
        ----------
        u : float
            The x-coordinate in the wave field.
        v : float
            The y-coordinate in the wave field.
        sources : iterable of numpy.ndarray
            Source points that contribute to the disturbance.

        Returns
        -------
        float
            The cumulative wave height.
        """
        z = 0
        for source in sources:
            x0, y0, _ = source
            z += self.amplitude * np.sin(
                (2 * PI / self.wavelength) * ((u - x0) ** 2 + (v - y0) ** 2) ** 0.5
                - 2 * PI * self.time / self.period
            )
        return z

    def _update_wave(self, mob: Mobject, dt: float) -> None:
        """Advance the wave simulation by *dt* seconds and refresh the surface.

        Parameters
        ----------
        mob : Mobject
            The surface mobject being updated.
        dt : float
            The time step since the last update.
        """
        self.time += dt
        mob.match_points(
            Surface(
                lambda u, v: np.array([u, v, self._wave_z(u, v, self.sources)]),
                u_range=self.u_range,
                v_range=self.v_range,
                **self.kwargs,
            )
        )

    def start_wave(self):
        """Animate the wave propagation."""
        self.add_updater(self._update_wave)

    def stop_wave(self):
        """Stop animating the wave propagation."""
        self.remove_updater(self._update_wave)


class LinearWave(RadialWave):
    """A wave surface propagating in one spatial direction.

    Parameters
    ----------
    wavelength
        The wavelength of the wave.
    period
        The period of the wave oscillation.
    amplitude
        The amplitude of the wave displacement.
    x_range
        The x-domain range used to construct the surface.
    y_range
        The y-domain range used to construct the surface.
    kwargs
        Additional keyword arguments passed to :class:`~manim.mobject.three_dimensions.Surface`.

    Examples
    --------

    .. manim:: LinearWaveExample
      :save_last_frame:

        from manim import *
        from manim_extensions.physics.wave import LinearWave

        class LinearWaveExample(Scene):
            def construct(self):
                wave = LinearWave(wavelength=2, amplitude=0.3)
                self.add(wave)
"""

    def __init__(
        self,
        wavelength: float = 1,
        period: float = 1,
        amplitude: float = 0.1,
        x_range: Iterable[float] = [-5, 5],
        y_range: Iterable[float] = [-5, 5],
        **kwargs,
    ) -> None:
        """Initialize a linear wave surface."""
        super().__init__(
            ORIGIN,
            wavelength=wavelength,
            period=period,
            amplitude=amplitude,
            x_range=x_range,
            y_range=y_range,
            **kwargs,
        )

    def _wave_z(self, u: float, v: float, sources: Iterable[np.ndarray]) -> float:
        """Compute the height of the linear wave at position ``(u, v)``.

        Parameters
        ----------
        u : float
            The x-coordinate in the wave field.
        v : float
            The y-coordinate in the wave field (unused for linear waves).
        sources : iterable of numpy.ndarray
            Source points (unused for linear waves).

        Returns
        -------
        float
            The wave height.
        """
        return self.amplitude * np.sin(
            (2 * PI / self.wavelength) * u - 2 * PI * self.time / self.period
        )


class StandingWave(ParametricFunction):
    """A 2D standing wave formed by the superposition of opposing waves.

    Parameters
    ----------
    n
        The harmonic number of the standing wave.
    length
        The spatial length of the wave domain.
    period
        The time taken for one oscillation cycle.
    amplitude
        The maximum vertical displacement of the wave.
    kwargs
        Additional keyword arguments passed to :class:`~manim.mobject.types.parametric_curve.ParametricFunction`.

    Examples
    --------

    .. manim:: StandingWaveExample
      :save_last_frame:

        from manim import *
        from manim_extensions.physics.wave import StandingWave

        class StandingWaveExample(Scene):
            def construct(self):
                wave = StandingWave(n=3, length=6, amplitude=0.5)
                self.add(wave)
"""

    def __init__(
        self,
        n: int = 2,
        length: float = 4,
        period: float = 1,
        amplitude: float = 1,
        **kwargs,
    ) -> None:
        """Initialize a standing wave."""
        self.n = n
        self.length = length
        self.period = period
        self.amplitude = amplitude
        self.time = 0
        self.kwargs = {**kwargs}

        super().__init__(
            lambda t: np.array([t, amplitude * np.sin(n * PI * t / length), 0]),
            t_range=[0, length],
            **kwargs,
        )
        self.shift([-self.length / 2, 0, 0])

    def _update_wave(self, mob: Mobject, dt: float) -> None:
        """Advance the standing-wave simulation and refresh the curve.

        Parameters
        ----------
        mob : Mobject
            The parametric curve object being updated.
        dt : float
            The time step since the last update.
        """
        self.time += dt
        mob.become(
            ParametricFunction(
                lambda t: np.array(
                    [
                        t,
                        self.amplitude
                        * np.sin(self.n * PI * t / self.length)
                        * np.cos(2 * PI * self.time / self.period),
                        0,
                    ]
                ),
                t_range=[0, self.length],
                **self.kwargs,
            ).shift(self.wave_center + [-self.length / 2, 0, 0])
        )

    def start_wave(self):
        """Begin the standing-wave animation and store its current center."""
        self.wave_center = self.get_center()
        self.add_updater(self._update_wave)

    def stop_wave(self):
        """Stop the standing-wave animation."""
        self.remove_updater(self._update_wave)
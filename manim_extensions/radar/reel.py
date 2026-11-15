# SPDX-FileCopyrightText: 2026 FTZ-OPUS
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""One-command sequence player: :class:`~manim_extensions.radar.reel.RadarReel`.

New in 0.1.1: each step may be a **list** of :class:`~manim_extensions.radar.data.RadarData` — a
comparison snapshot. The reel then morphs every dataset of the chart at
once, colouring unlabeled datasets by their position so the same dataset
keeps its colour across the whole reel.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Iterable, List, Optional, Union

from manim import Scene, UpdateFromAlphaFunc

from .backdrop import DeepSpace
from .chart import RadarChart
from .data import RadarData

__all__ = ["RadarReel"]


class RadarReel:
    """Play a whole list of snapshots with a single command.

    Examples
    --------
    ::

        chart = RadarChart(axes=SIX_AXES, values=[...], title="Six axes")
        RadarReel(chart, [d1, d2, d3, d4], hold=0.6, backdrop=True).play_on(self)

    Comparison reel (0.1.1) — each step is a list of datasets::

        RadarReel(chart, [
            [holder_a, basic_a],
            [holder_b, basic_b],
        ], hold=0.8).play_on(self)

    Per-snapshot overrides come from :class:`~manim_extensions.radar.data.RadarData`:
    ``hold``, ``transition``, ``emphasis`` (``"zoom"`` / ``"gap"`` / ``"rim"``)
    and ``color``. In a comparison step they are read from the *first*
    dataset of the list. Snapshots without an explicit colour get one from
    the theme palette, in order (by position, so dataset 0 is always the
    same colour).
    """

    def __init__(
        self,
        chart: RadarChart,
        datasets: Iterable,
        *,
        hold: float = 0.6,
        transition: Optional[str] = None,
        run_time: Optional[float] = None,
        intro: Union[bool, float] = True,
        outro: Union[bool, float] = True,
        backdrop: Union[bool, DeepSpace, None] = None,
        gap_hold: float = 1.5,
        auto_color: bool = True,
        verbose: bool = False,
    ) -> None:
        self.chart = chart
        self.hold = float(hold)
        self.transition = transition
        self.run_time = run_time
        self.intro = intro
        self.outro = outro
        self.gap_hold = float(gap_hold)
        self.auto_color = auto_color
        self.verbose = verbose
        self.backdrop_spec = backdrop
        self.backdrop: Optional[DeepSpace] = None

        items = list(datasets)
        if not items:
            raise ValueError("RadarReel needs at least one dataset")
        self.steps: List[List[RadarData]] = [
            self._normalize_step(item) for item in items
        ]
        if auto_color:
            self.steps = [
                self._with_palette_colors(step, i) for i, step in enumerate(self.steps)
            ]
        # 0.1.0 compatibility: a flat list of the (colour-assigned) datasets
        self.datasets = [d for step in self.steps for d in step]

    # ------------------------------------------------------------------
    def _normalize_step(self, item) -> List[RadarData]:
        if isinstance(item, (list, tuple)) and not (
            item and isinstance(item[0], (int, float))
        ):
            step = list(item)
        else:
            step = [item]
        out: List[RadarData] = []
        for d in step:
            if isinstance(d, RadarData):
                out.append(d)
            elif isinstance(d, dict):
                payload = dict(d)
                axes = payload.pop("axes", self.chart.data.axes)
                out.append(RadarData(axes=axes, **payload))
            else:
                out.append(self.chart.data.with_values(d))
        return out

    def _with_palette_colors(
        self, step: List[RadarData], step_index: int
    ) -> List[RadarData]:
        """Colour unlabeled datasets from the theme palette.

        A lone dataset takes the *step* colour (0.1.0 behaviour: consecutive
        snapshots cycle through the palette). In a comparison step, colour
        follows the dataset's position, so the same dataset keeps its colour
        across the whole reel.
        """
        out = []
        for i, d in enumerate(step):
            color_index = step_index if len(step) == 1 else i
            if d.color:
                out.append(d)
            else:
                out.append(
                    replace(d, color=str(self.chart.theme.dataset_color(color_index)))
                )
        return out

    # ------------------------------------------------------------------
    @property
    def total_time(self) -> float:
        """Rough duration of the reel in seconds."""
        default_rt = self.run_time or self.chart.config.morph_run_time
        total = 0.0
        for step in self.steps:
            lead = step[0]
            total += default_rt + (lead.hold if lead.hold is not None else self.hold)
            if lead.emphasis == "gap":
                total += self.gap_hold + 0.9
        return total

    def summary(self) -> str:
        """Human readable description of what :meth:`~manim_extensions.radar.reel.RadarReel.play_on` will do."""
        lines = [
            f"RadarReel · {len(self.steps)} snapshots · "
            f"~{self.total_time:.1f}s · style={self.chart.config.title or '-'}"
        ]
        for i, step in enumerate(self.steps):
            lead = step[0]
            flags = []
            if lead.emphasis:
                flags.append(f"emphasis={lead.emphasis}")
            if lead.transition:
                flags.append(f"transition={lead.transition}")
            if lead.rim:
                flags.append("rim")
            tail = ("  [" + ", ".join(flags) + "]") if flags else ""
            name = " vs ".join(str(d.name or "-") for d in step)
            lines.append(f"  {i + 1:>3}. {name:<24} {tuple(lead.values)}{tail}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def play_on(self, scene: Scene) -> "RadarReel":
        """Play the whole sequence on ``scene``."""
        chart = self.chart
        if self.verbose:
            print(self.summary())
        if chart not in scene.mobjects:
            scene.add(chart)
        self._install_backdrop(scene)

        if self.intro:
            rt = (
                float(self.intro)
                if isinstance(self.intro, (int, float)) and self.intro is not True
                else 0.9
            )
            scene.play(chart.reveal(run_time=rt), run_time=rt)

        for step in self.steps:
            lead = step[0]
            if lead.emphasis == "gap":
                scene.play(chart.disappear(), run_time=0.8)
                self._fade_backdrop(scene, 0.0, 0.6)
                scene.wait(self.gap_hold)
                self._fade_backdrop(scene, 1.0, 0.4)
                scene.play(chart.glitch_in(), run_time=0.75)
                # after a glitch-in the chart is on the *old* state; morph now
                scene.play(
                    chart.morph_to(
                        step if len(step) > 1 else step[0],
                        transition=lead.transition or self.transition,
                        run_time=self.run_time,
                        rim=1.0 if lead.emphasis == "rim" else None,
                    )
                )
            else:
                trans = lead.transition or (
                    "zoom" if lead.emphasis == "zoom" else self.transition
                )
                scene.play(
                    chart.morph_to(
                        step if len(step) > 1 else step[0],
                        transition=trans,
                        run_time=self.run_time,
                        rim=1.0 if lead.emphasis == "rim" else None,
                    )
                )
            wait = lead.hold if lead.hold is not None else self.hold
            if wait > 0:
                scene.wait(wait)

        if self.outro:
            rt = (
                float(self.outro)
                if isinstance(self.outro, (int, float)) and self.outro is not True
                else 0.8
            )
            scene.play(chart.disappear(run_time=rt), run_time=rt)
            if self.backdrop is not None:
                self._fade_backdrop(scene, 0.0, 0.5)
                scene.remove(self.backdrop)
        return self

    # ------------------------------------------------------------------
    def _install_backdrop(self, scene: Scene) -> None:
        spec = self.backdrop_spec
        if spec is False or spec is None:
            return
        if isinstance(spec, DeepSpace):
            self.backdrop = spec
            if spec not in scene.mobjects:
                scene.add(spec)
        else:
            self.backdrop = DeepSpace(theme=self.chart.theme)
            scene.add(self.backdrop)
        self.backdrop.link(self.chart)

    def _fade_backdrop(self, scene: Scene, to: float, run_time: float) -> None:
        if self.backdrop is None:
            return
        start = self.backdrop._fade
        scene.play(
            UpdateFromAlphaFunc(
                self.backdrop,
                lambda m, a, s=start, t=to: m.set_fade(s + (t - s) * a),
            ),
            run_time=run_time,
        )

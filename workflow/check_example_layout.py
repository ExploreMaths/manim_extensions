# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Check that every ``.. manim::`` doc example is laid out sensibly.

For each example block the scene is constructed with
``skip_animations=True`` (final mobject states, no frames rendered) and
the union bounding box of the scene's mobjects is compared with the
camera frame:

- ``OUT_OF_FRAME``: content extends beyond the frame by more than 5% of
  the frame size on any side (it will be visibly cut off).
- ``TOO_SMALL``: content covers less than 25% of the frame in both
  dimensions (it renders as an unusably tiny figure).

Every doc example is probed. Examples whose code renders nested scenes are
skipped entirely. A probe error is a failure: the docs pipeline renders the
same code, so an example that cannot even construct headlessly must not pass
silently. The only exceptions are the explicitly listed environment errors
below, each with the reason it is an environment limitation rather than an
example defect.

Usage:
    python workflow/check_example_layout.py [--workers N]
"""

from __future__ import annotations

import argparse
import multiprocessing
import os
import shutil
import sys
import tempfile
import traceback
from pathlib import Path

WORKFLOW = Path(__file__).resolve().parent
sys.path.insert(0, str(WORKFLOW))

# Mirror docs/source/_extensions/manim_image_patch.py: manim 0.21/0.22
# builds its camera overlay with Image.fromarray(np.zeros((h, w)),
# mode="RGBA"), which Pillow rejects ("Invalid mode for data type") and
# fails every ImageMobject render. Expand 2-D arrays to 4 channels so the
# probe measures the same rendered content the docs build produces.
import numpy as np
from PIL import Image as _PILImage

_orig_fromarray = _PILImage.fromarray


def _patched_fromarray(obj, mode=None):
    if mode == "RGBA" and getattr(obj, "ndim", 0) == 2:
        obj = np.repeat(obj[:, :, None], 4, axis=2).astype(np.uint8)
    return _orig_fromarray(obj, mode=mode)


_PILImage.fromarray = _patched_fromarray

# A margin of 5% of the frame size is allowed before content counts as
# cut off (thin strokes at the exact edge are fine).
OUT_OF_FRAME_FRACTION = 0.05
# Content smaller than this fraction of the frame in BOTH dimensions is
# flagged as too small.
MIN_COVER_FRACTION = 0.25
# A slender strip (short in one dimension and not filling the other)
# renders as an unusably tiny figure even though one dimension covers
# more than MIN_COVER_FRACTION; e.g. a lone formula that is 35% wide but
# only 9% tall.  The thresholds are deliberately tight (really short
# side, other side below 70% of the frame) so wide banners, tall narrow
# axes and ordinary medium-size figures are not caught.
MIN_TINY_FRACTION = 0.10
MIN_TINY_OTHER_FRACTION = 0.60

# Probe failures that describe the local runner, not the example.  Every
# entry names the exact exception signature and why the CI runner differs;
# anything not listed here fails the check.
ENVIRONMENT_PROBE_ERRORS = (
    (
        "RuntimeError: latex failed but did not produce a log file.",
        "requires a working TeX distribution; the CI manim environment installs one",
    ),
    (
        "ValueError: Your installation does not support converting .dvi files to SVG.",
        "requires dvisvgm >= 2.4; the CI manim environment installs it",
    ),
    (
        "ImportError: This feature requires 'kociemba'.",
        "the rubikscube extra is not installed in the local probe; CI installs every extra",
    ),
)


_WORKER_ROOT: Path | None = None


def _worker_init(workdir):
    """Import manim once per worker and silence it."""
    global _WORKER_ROOT
    _WORKER_ROOT = Path(workdir)
    import logging

    from manim import config

    logging.getLogger("manim").setLevel(logging.ERROR)
    config.media_dir = Path(workdir) / "media"
    config.progress_bar = "none"
    config.verbosity = "ERROR"


def probe_block(task):
    """Construct one example and measure its content bounding box."""
    class_name, code, source, assets, renderer = task
    try:
        import numpy as np
        from manim import tempconfig

        namespace = {"__file__": "<doc example>", "__name__": "__manim_docgen__"}
        root = _WORKER_ROOT or Path(tempfile.mkdtemp())
        workdir = Path(tempfile.mkdtemp(dir=root))
        for asset in assets:
            target = workdir / Path(asset).name
            if not target.exists():
                try:
                    target.symlink_to(asset)
                except OSError:
                    shutil.copy2(asset, target)
        previous = Path.cwd()
        os.chdir(workdir)
        try:
            with tempconfig(
                {
                    "disable_caching": True,
                    "media_dir": str(workdir / "media"),
                    "frame_rate": 1,
                    "pixel_height": 480,
                    "pixel_width": 854,
                    "renderer": renderer,
                }
            ):
                exec(code, namespace)
                scene_class = namespace[class_name]
                try:
                    scene = scene_class(skip_animations=True)
                except TypeError:
                    scene = scene_class()

                # skip_animations short-circuits play() before it adds the
                # animated mobjects to the scene, so collect everything that
                # is added or played explicitly.
                collected = []
                orig_add, orig_play = scene.add, scene.play

                def tracking_add(*mobs, **kwargs):
                    collected.extend(mobs)
                    return orig_add(*mobs, **kwargs)

                def tracking_play(*anims, **kwargs):
                    def collect(anim, out):
                        mobs = getattr(anim, "mobjects", None)
                        if mobs:
                            out.extend(mobs)
                        for sub in getattr(anim, "animations", None) or ():
                            collect(sub, out)

                    for anim in anims:
                        collect(anim, collected)
                    return orig_play(*anims, **kwargs)

                scene.add, scene.play = tracking_add, tracking_play
                # construct() is called directly (not via render()), so run the
                # scene's setup() manually to mirror a real render -- scenes such
                # as CompassScene set up their mobjects there.
                scene.setup()
                scene.construct()
                pool = list(scene.mobjects)
                for mob in collected:
                    if mob not in pool:
                        pool.append(mob)
        finally:
            os.chdir(previous)

        camera = scene.camera
        # The OpenGL camera exposes frame geometry through get_width()/
        # get_height() and frame_center instead of the Cairo frame_* properties.
        frame_w = (
            camera.frame_width if hasattr(camera, "frame_width") else camera.get_width()
        )
        frame_h = (
            camera.frame_height
            if hasattr(camera, "frame_height")
            else camera.get_height()
        )
        # MovingCameraScene moves camera.frame; measure overflow against
        # the frame's actual position, not the origin.
        cam_frame = getattr(camera, "frame", None)
        if cam_frame is not None:
            fc = cam_frame.get_center()
        else:
            fc = np.array(camera.frame_center)

        mins = np.array([np.inf, np.inf, np.inf])
        maxs = np.array([-np.inf, -np.inf, -np.inf])
        counted = 0
        for mob in pool:
            try:
                pts = mob.get_all_points()
            except Exception:
                continue
            if len(pts) == 0:
                continue
            mins = np.minimum(mins, pts.min(axis=0))
            maxs = np.maximum(maxs, pts.max(axis=0))
            counted += 1
        if counted == 0:
            return (class_name, source, None, "no mobjects in scene")

        width = float(maxs[0] - mins[0])
        height = float(maxs[1] - mins[1])
        return (
            class_name,
            source,
            {
                "width": width,
                "height": height,
                "frame_width": frame_w,
                "frame_height": frame_h,
                "overflow_x": max(
                    0.0, fc[0] - frame_w / 2 - mins[0], maxs[0] - fc[0] - frame_w / 2
                ),
                "overflow_y": max(
                    0.0, fc[1] - frame_h / 2 - mins[1], maxs[1] - fc[1] - frame_h / 2
                ),
            },
            "",
        )
    except Exception:
        return (class_name, source, None, traceback.format_exc(limit=3))


def classify(class_name: str, m: dict) -> str | None:
    """Return the violation kind for a measurement, or None."""
    if m["overflow_x"] > OUT_OF_FRAME_FRACTION * m["frame_width"]:
        return "OUT_OF_FRAME"
    if m["overflow_y"] > OUT_OF_FRAME_FRACTION * m["frame_height"]:
        return "OUT_OF_FRAME"
    h_ratio = m["height"] / m["frame_height"]
    w_ratio = m["width"] / m["frame_width"]
    if h_ratio < MIN_COVER_FRACTION and w_ratio < MIN_COVER_FRACTION:
        return "TOO_SMALL"
    if h_ratio < MIN_TINY_FRACTION and w_ratio < MIN_TINY_OTHER_FRACTION:
        return "TOO_SMALL"
    if w_ratio < MIN_TINY_FRACTION and h_ratio < MIN_TINY_OTHER_FRACTION:
        return "TOO_SMALL"
    return None


def environment_reason(error: str) -> str | None:
    """Return the documented environment reason for a probe failure, if any."""
    for signature, reason in ENVIRONMENT_PROBE_ERRORS:
        if signature in error:
            return reason
    return None


def main() -> int:
    """Main check function."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Per-example construction timeout in seconds (default: 300)",
    )
    args = parser.parse_args()

    import render_doc_examples as rde

    blocks = []
    skipped = []
    for f in rde.iter_source_files():
        for block in rde.extract_blocks(f):
            task = (
                block["class_name"],
                block["code"],
                block["source"],
                block["assets"],
                block["renderer"],
            )
            # Blocks that render nested scenes inside construct() cannot be
            # probed headlessly; their layout is covered by the regular
            # media pipeline instead.
            if ".render(" in block["code"]:
                skipped.append(block["class_name"])
                continue
            blocks.append(task)
    print(
        f"Probing {len(blocks)} doc examples "
        f"({len(skipped)} skipped: nested render) ..."
    )

    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        pool = multiprocessing.Pool(
            args.workers, initializer=_worker_init, initargs=(tmp,)
        )
        try:
            async_results = [pool.apply_async(probe_block, (t,)) for t in blocks]
            results = []
            for class_name, source, ar in [
                (t[0], t[2], r) for t, r in zip(blocks, async_results)
            ]:
                try:
                    results.append(ar.get(timeout=args.timeout))
                except Exception:
                    results.append(
                        (
                            class_name,
                            source,
                            None,
                            f"probe timed out ({args.timeout}s)",
                        )
                    )
        finally:
            pool.terminate()
            pool.join()

    errors = [(c, s, e) for c, s, m, e in results if m is None]
    flagged = []
    for class_name, source, m, _err in results:
        if m is None:
            continue
        kind = classify(class_name, m)
        if kind:
            flagged.append((kind, class_name, source, m))

    environment_errors = [
        (class_name, source, err, environment_reason(err))
        for class_name, source, err in errors
        if environment_reason(err) is not None
    ]
    probe_failures = [
        (class_name, source, err)
        for class_name, source, err in errors
        if environment_reason(err) is None
    ]

    for kind, class_name, source, m in sorted(flagged):
        cover_w = m["width"] / m["frame_width"]
        cover_h = m["height"] / m["frame_height"]
        detail = (
            f"covers {cover_w:.0%}x{cover_h:.0%} of the frame"
            if kind == "TOO_SMALL"
            else f"overflows the frame by x={m['overflow_x']:.2f}, "
            f"y={m['overflow_y']:.2f} units"
        )
        print(f"  {kind:12} {class_name} ({source}): {detail}")
        # Surface each failure as a GitHub annotation so it is visible
        # without downloading the job log.
        print(f"::error file={source},title=Layout {kind}::" f"{class_name}: {detail}")
    for class_name, source, err, reason in environment_errors:
        first = err.strip().splitlines()[-1] if err.strip() else "?"
        print(
            f"  ENV probe error (allowed) {class_name} ({source}): "
            f"{first} [{reason}]"
        )
    for class_name, source, err in probe_failures:
        first = err.strip().splitlines()[-1] if err.strip() else "?"
        print(f"  PROBE ERROR {class_name} ({source}): {first}")
        print(
            f"::error file={source},title=Doc example probe::" f"{class_name}: {first}"
        )

    total = len(flagged) + len(probe_failures)
    if total:
        print(
            f"\nTotal: {total} layout/probe issue(s) "
            f"({len(environment_errors)} environment error(s) allowed)"
        )
        return 1
    print(
        "All doc examples are in frame and at a reasonable scale. "
        f"({len(environment_errors)} environment error(s) allowed)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

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

Intentional cases (full-bleed backgrounds, deliberately tiny demos) are
listed in ``workflow/example_layout_exemptions.json`` as a flat list of
scene class names. Examples whose code renders nested scenes are skipped
entirely; probe errors (an example that cannot run headlessly) are
reported as warnings and do not fail the check — renderability itself is
enforced by the docs media pipeline.

Usage:
    python workflow/check_example_layout.py [--workers N]
    python workflow/check_example_layout.py --write-exemptions
"""

from __future__ import annotations

import argparse
import json
import multiprocessing
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "workflow"))

EXEMPTIONS_FILE = Path(__file__).resolve().parent / "example_layout_exemptions.json"

# A margin of 5% of the frame size is allowed before content counts as
# cut off (thin strokes at the exact edge are fine).
OUT_OF_FRAME_FRACTION = 0.05
# Content smaller than this fraction of the frame in BOTH dimensions is
# flagged as too small.
MIN_COVER_FRACTION = 0.25

def _worker_init(workdir):
    """Import manim once per worker and silence it."""
    import logging

    from manim import config

    logging.getLogger("manim").setLevel(logging.ERROR)
    config.media_dir = Path(workdir) / "media"
    config.progress_bar = "none"
    config.verbosity = "ERROR"


def probe_block(task):
    """Construct one example and measure its content bounding box."""
    class_name, code, source = task
    try:
        import numpy as np
        from manim import tempconfig

        namespace = {"__file__": "<doc example>", "__name__": "__manim_docgen__"}
        with tempconfig({
            "disable_caching": True,
            "frame_rate": 1,
            "pixel_height": 480,
            "pixel_width": 854,
        }):
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
            scene.construct()
            pool = list(scene.mobjects)
            for mob in collected:
                if mob not in pool:
                    pool.append(mob)

        frame_h = scene.camera.frame_height
        frame_w = scene.camera.frame_width
        # MovingCameraScene moves camera.frame; measure overflow against
        # the frame's actual position, not the origin.
        cam_frame = getattr(scene.camera, "frame", None)
        fc = cam_frame.get_center() if cam_frame is not None else np.zeros(3)

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
        return (class_name, source, {
            "width": width,
            "height": height,
            "frame_width": frame_w,
            "frame_height": frame_h,
            "overflow_x": max(0.0, fc[0] - frame_w / 2 - mins[0],
                              maxs[0] - fc[0] - frame_w / 2),
            "overflow_y": max(0.0, fc[1] - frame_h / 2 - mins[1],
                              maxs[1] - fc[1] - frame_h / 2),
        }, "")
    except Exception:
        return (class_name, source, None, traceback.format_exc(limit=3))


def classify(class_name: str, m: dict) -> str | None:
    """Return the violation kind for a measurement, or None."""
    if m["overflow_x"] > OUT_OF_FRAME_FRACTION * m["frame_width"]:
        return "OUT_OF_FRAME"
    if m["overflow_y"] > OUT_OF_FRAME_FRACTION * m["frame_height"]:
        return "OUT_OF_FRAME"
    if (m["height"] < MIN_COVER_FRACTION * m["frame_height"]
            and m["width"] < MIN_COVER_FRACTION * m["frame_width"]):
        return "TOO_SMALL"
    return None


def main() -> int:
    """Main check function."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument(
        "--write-exemptions", action="store_true",
        help="Write ALL currently flagged scene names to the exemptions "
             "file. Review the result before committing!",
    )
    args = parser.parse_args()

    import render_doc_examples as rde

    blocks = []
    skipped = []
    for f in rde.iter_source_files():
        for block in rde.extract_blocks(f):
            task = (block["class_name"], block["code"], block["source"])
            # Blocks that render nested scenes inside construct() cannot be
            # probed headlessly; their layout is covered by the regular
            # media pipeline instead.
            if ".render(" in block["code"]:
                skipped.append(block["class_name"])
                continue
            blocks.append(task)
    print(f"Probing {len(blocks)} doc examples "
          f"({len(skipped)} skipped: nested render) ...")

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
                    results.append(ar.get(timeout=120))
                except Exception:
                    results.append(
                        (class_name, source, None, "probe timed out (120s)")
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

    if args.write_exemptions:
        EXEMPTIONS_FILE.write_text(
            json.dumps(sorted({c for _k, c, _s, _m in flagged}),
                       indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Wrote {len(flagged)} exempted names to {EXEMPTIONS_FILE.name}.")
        return 0

    exemptions = set()
    if EXEMPTIONS_FILE.exists():
        exemptions = set(json.loads(EXEMPTIONS_FILE.read_text(encoding="utf-8")))

    unexempted = [f for f in flagged if f[1] not in exemptions]
    remaining_errors = [e for e in errors if e[0] not in exemptions]

    for kind, class_name, source, m in sorted(unexempted):
        cover_w = m["width"] / m["frame_width"]
        cover_h = m["height"] / m["frame_height"]
        detail = (
            f"covers {cover_w:.0%}x{cover_h:.0%} of the frame"
            if kind == "TOO_SMALL"
            else f"overflows the frame by x={m['overflow_x']:.2f}, "
                 f"y={m['overflow_y']:.2f} units"
        )
        print(f"  {kind:12} {class_name} ({source}): {detail}")
    for class_name, source, err in remaining_errors:
        first = err.strip().splitlines()[-1] if err.strip() else "?"
        print(f"  WARN probe error (not counted) {class_name} ({source}): "
              f"{first}")

    total = len(unexempted)
    if total:
        print(f"\nTotal: {total} layout issue(s) "
              f"({len(flagged) - len(unexempted)} exempted)")
        return 1
    print("All doc examples are in frame and at a reasonable scale.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Pre-render all ``.. manim::`` doc examples into a media cache tree.

The Sphinx build (``docs/source/_extensions/manim_directive.py``, patched)
names every rendered example by a hash of its source and, when the
``MANIM_MEDIA_CACHE_DIR`` environment variable points at a cache tree
produced by this script, copies the media from the cache instead of
rendering. Read the Docs uses this to avoid rendering hundreds of
examples on every docs build; the cache is refreshed by the
``docs-media`` GitHub Actions workflow and stored on the ``rtd-media``
branch.

Cache layout::

    <out>/videos/<SceneClass>-<hash8>.{mp4,gif}
    <out>/images/<SceneClass>-<hash8>.png
    <out>/manifest.json          # output_file -> {sha256, source}

Usage:
    python workflow/render_doc_examples.py --out media_cache [--workers N]
"""

import argparse
import hashlib
import json
import multiprocessing
import re
import shutil
import sys
import textwrap
import time
import traceback
from pathlib import Path

from manim import *

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs" / "source"
SRC = ROOT / "manim_extensions"

# Same exclusions as the docs build: doc-build tooling and testing helpers
# are never autodoc'd, so their example blocks never render in the docs.
SKIP_PARTS = {"__pycache__", "docbuild", "testing", "custom_mobjects"}

MANIM_DIRECTIVE_RE = re.compile(r"\s*\.\.\s+manim::\s*(\S+)")
OPTION_RE = re.compile(r"\s*:(\w+):")

QUALITY_MAP = {
    "low": "low_quality",
    "medium": "medium_quality",
    "high": "high_quality",
    "fourk": "fourk_quality",
}


def iter_source_files():
    for base in (DOCS, SRC):
        for path in sorted(base.rglob("*")):
            if path.suffix not in (".rst", ".py"):
                continue
            if any(part in SKIP_PARTS for part in path.parts):
                continue
            yield path


def extract_blocks(path: Path):
    """Extract ``.. manim::`` blocks the way docutils would feed them to the
    directive: content lines at block indentation, ending at the first
    dedented line, with trailing blank lines stripped (the directive trims
    them too, see manim_directive.py)."""
    lines = path.read_text(encoding="utf-8").splitlines()
    blocks = []
    i = 0
    while i < len(lines):
        m = MANIM_DIRECTIVE_RE.match(lines[i])
        if not m:
            i += 1
            continue
        class_name = m.group(1)
        options = {}
        j = i + 1
        while j < len(lines) and (OPTION_RE.match(lines[j]) or not lines[j].strip()):
            opt = OPTION_RE.match(lines[j])
            if opt:
                name = opt.group(1)
                if name == "quality":
                    options[name] = lines[j].split(":", 2)[-1].strip()
                else:
                    options[name] = True
            j += 1
        content = []
        while j < len(lines):
            line = lines[j]
            if not line.strip():
                content.append("")
                j += 1
                continue
            indent = len(line) - len(line.lstrip())
            if content:
                base = min(
                    (len(l) - len(l.lstrip()) for l in content if l.strip()),
                    default=indent,
                )
                if indent < base:
                    break
            content.append(line)
            j += 1
        while content and not content[-1].strip():
            content.pop()
        if not content:
            i = j
            continue
        base = min(len(l) - len(l.lstrip()) for l in content if l.strip())
        code = "\n".join(l[base:] if l.strip() else "" for l in content)
        blocks.append(
            {
                "class_name": class_name,
                "save_last_frame": "save_last_frame" in options,
                "save_as_gif": "save_as_gif" in options,
                "quality": QUALITY_MAP.get(options.get("quality", "")),
                "code": code,
                "source": str(path.relative_to(ROOT)),
            }
        )
        i = max(j, i + 1)
    return blocks


def output_name(class_name: str, code: str) -> str:
    user_code = textwrap.dedent(code).splitlines()
    digest = hashlib.md5(chr(10).join(user_code).encode()).hexdigest()[:8]
    return f"{class_name}-{digest}"


def render_block(task):
    """Render one example in a subprocess. Returns (key, src_ext, ok, error)."""
    class_name, code, save_last_frame, save_as_gif, quality, workdir = task
    try:
        q = quality or "example_quality"
        frame_rate = QUALITIES[q]["frame_rate"]
        pixel_height = QUALITIES[q]["pixel_height"]
        pixel_width = QUALITIES[q]["pixel_width"]

        output_file = output_name(class_name, code)
        config.media_dir = Path(workdir)
        config.images_dir = "{media_dir}/images"
        config.video_dir = "{media_dir}/videos/{quality}"
        config.progress_bar = "none"
        config.verbosity = "WARNING"

        example_config = {
            "frame_rate": frame_rate,
            "pixel_height": pixel_height,
            "pixel_width": pixel_width,
            "save_last_frame": save_last_frame,
            "write_to_movie": not save_last_frame,
            "output_file": output_file,
        }
        if save_last_frame:
            example_config["format"] = None
        if save_as_gif:
            example_config["format"] = "gif"

        user_code = textwrap.dedent(code).splitlines()
        has_manim_import = any(
            line.strip() == "from manim import *" for line in user_code
        )
        exec_code = [
            *([] if has_manim_import else ["from manim import *"]),
            *user_code,
            f"{class_name}().render()",
        ]
        with tempconfig(example_config):
            exec("\n".join(exec_code), {})

        if save_last_frame:
            hits = list(Path(workdir).rglob(f"{output_file}.png"))
            ext = "png"
        else:
            ext = "gif" if save_as_gif else "mp4"
            hits = list(Path(workdir).rglob(f"{output_file}.{ext}"))
        if not hits:
            return (output_file, ext, False, "render produced no output file")
        return (output_file, str(hits[0]), True, "")
    except Exception:
        return (class_name, "", False, traceback.format_exc(limit=3))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, help="cache output directory")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument(
        "--only",
        default=None,
        help="render only blocks whose source path contains this substring",
    )
    args = parser.parse_args()

    out = Path(args.out)
    videos_out = out / "videos"
    images_out = out / "images"
    videos_out.mkdir(parents=True, exist_ok=True)
    images_out.mkdir(parents=True, exist_ok=True)
    manifest_path = out / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}

    blocks = []
    for path in iter_source_files():
        if args.only and args.only not in str(path):
            continue
        for block in extract_blocks(path):
            block["output_file"] = output_name(block["class_name"], block["code"])
            blocks.append(block)

    print(f"Found {len(blocks)} manim example blocks")

    todo = []
    skipped = 0
    for block in blocks:
        entry = manifest.get(block["output_file"])
        ext = (
            "png"
            if block["save_last_frame"]
            else ("gif" if block["save_as_gif"] else "mp4")
        )
        target_dir = images_out if block["save_last_frame"] else videos_out
        if (
            entry
            and entry.get("sha256") == block["output_file"]
            and (target_dir / f"{block['output_file']}.{ext}").exists()
        ):
            skipped += 1
            continue
        todo.append(block)

    print(f"{skipped} already cached, {len(todo)} to render")
    if not todo:
        return 0

    work_root = out / "_work"
    shutil.rmtree(work_root, ignore_errors=True)
    work_root.mkdir(parents=True)

    tasks = []
    for n, block in enumerate(todo):
        workdir = work_root / f"w{n % max(1, args.workers)}-{n}"
        workdir.mkdir(parents=True, exist_ok=True)
        tasks.append(
            (
                block["class_name"],
                block["code"],
                block["save_last_frame"],
                block["save_as_gif"],
                block.get("quality"),
                str(workdir),
            )
        )

    failures = 0
    t0 = time.time()
    with multiprocessing.Pool(args.workers) as pool:
        for key, src, ok, error in pool.imap_unordered(render_block, tasks):
            if not ok:
                failures += 1
                print(f"FAILED {key}: {error}", file=sys.stderr)
                continue
            src = Path(src)
            if src.suffix == ".png":
                shutil.copyfile(src, images_out / src.name)
            else:
                shutil.copyfile(src, videos_out / src.name)
            manifest[key] = {"sha256": key, "ext": src.suffix.lstrip(".")}

    shutil.rmtree(work_root, ignore_errors=True)
    manifest_path.write_text(json.dumps(manifest, indent=1, sort_keys=True))

    print(
        f"Rendered {len(todo) - failures}/{len(todo)} examples "
        f"in {time.time() - t0:.0f}s; cache now holds {len(manifest)} entries"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

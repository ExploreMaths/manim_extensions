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

ROOT = Path(__file__).resolve().parent.parent
# Ensure the source package shadows any stale installed copy in workers.
sys.path.insert(0, str(ROOT))

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

# Fine-grained cache invalidation tags. Each tag is a named version of an
# environmental factor that affects rendering (installed fonts, compiler
# versions, etc.). When rendering an example, we determine which tags are
# relevant to that example by scanning its code, and record the
# (tag -> value) mapping in the manifest entry. On cache check, the
# recorded values must exactly match the current values of the example's
# relevant tags; otherwise the example is re-rendered.
#
# Bumping a tag's value invalidates only the examples whose code triggers
# that tag. Adding a new tag invalidates the examples that match its
# heuristic (those whose code references the relevant APIs).
#
# History:
#   fontconfig_nerdfont = 1  # fontconfig-based Nerd Font installation
#   jetbrains_mono = 1      # fonts-jetbrains-mono apt package
ENV_TAGS = {
    "fontconfig_nerdfont": 1,
    "jetbrains_mono": 1,
}


def tags_for_block(block: dict) -> set[str]:
    """Heuristic: which ENV_TAGS affect this example based on its code."""
    code = block["code"]
    tags = set()
    # Nerd Font is only loaded when a QR code requests an icon (passed as
    # a string keyword argument), or when the nerdfont helpers are used
    # directly. Match `icon="` / `icon='` to avoid flagging examples that
    # merely use `icon` as a local variable name.
    if any(s in code for s in ("nerdfont", "NerdFont", 'icon="', "icon='")):
        tags.add("fontconfig_nerdfont")
    if any(
        s in code
        for s in ("FileTree", "DEFAULT_MONO_FONT", "JetBrains Mono", "Code(")
    ):
        tags.add("jetbrains_mono")
    return tags


def iter_source_files():
    # Examples live in rst sources and in autodoc'd package docstrings.
    # Python files under docs/ (sphinx extensions, conf) only *document*
    # the directive and must not be scanned.
    for path in sorted(DOCS.rglob("*.rst")):
        yield path
    for path in sorted(SRC.rglob("*.py")):
        if any(part in SKIP_PARTS for part in path.parts):
            continue
        yield path


def normalize_code(code: str) -> list:
    """Normalize a block exactly like manim_directive.py normalizes its
    content before hashing and executing it: doctest prompt stripping,
    dedent, trailing blank removal."""
    lines = code.splitlines()
    if lines and lines[0].startswith(">>> "):
        lines = [line[4:] for line in lines if line.startswith((">>> ", "... "))]
    else:
        lines = textwrap.dedent("\n".join(lines)).splitlines()
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


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
    user_code = normalize_code(code)
    digest = hashlib.md5(chr(10).join(user_code).encode()).hexdigest()[:8]
    return f"{class_name}-{digest}"


# The docs build executes every example with manim_directive.py's globals,
# so __file__ inside an example resolves to this path (VideoMobject's
# docstring example relies on it to locate docs/source/_static media).
DIRECTIVE_FILE = str(DOCS / "_extensions" / "manim_directive.py")


def render_block(task):
    """Render one example in a subprocess. Returns (key, src, ok, error, quality)."""
    class_name, code, save_last_frame, save_as_gif, quality, workdir = task
    output_file = output_name(class_name, code)
    q = quality or "example_quality"
    try:
        import logging

        from manim import config, tempconfig
        from manim.constants import QUALITIES

        logging.getLogger("manim").setLevel(logging.ERROR)

        frame_rate = QUALITIES[q]["frame_rate"]
        pixel_height = QUALITIES[q]["pixel_height"]
        pixel_width = QUALITIES[q]["pixel_width"]

        config.media_dir = Path(workdir)
        config.images_dir = "{media_dir}/images"
        config.video_dir = "{media_dir}/videos/{quality}"
        config.progress_bar = "none"
        config.verbosity = "ERROR"

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

        user_code = normalize_code(code)
        has_manim_import = any(
            line.strip() == "from manim import *" for line in user_code
        )
        exec_code = [
            *([] if has_manim_import else ["from manim import *"]),
            *user_code,
            f"{class_name}().render()",
        ]
        with tempconfig(example_config):
            exec(
                "\n".join(exec_code),
                {"__file__": DIRECTIVE_FILE, "__name__": "__manim_docgen__"},
            )

        if save_last_frame:
            hits = list(Path(workdir).rglob(f"{output_file}.png"))
            ext = "png"
        else:
            ext = "gif" if save_as_gif else "mp4"
            hits = list(Path(workdir).rglob(f"{output_file}.{ext}"))
        if not hits:
            return (output_file, "", False, "render produced no output file", q)
        return (output_file, str(hits[0]), True, "", q)
    except Exception:
        return (output_file, "", False, traceback.format_exc(limit=3), q)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, help="cache output directory")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument(
        "--quality",
        choices=["low", "medium", "high", "fourk"],
        default=None,
        help="render quality for blocks without an explicit :quality: option "
             "(default: manim's example quality)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="only report how many blocks would be rendered; exits 0 when "
             "everything is cached (does not require manim installed)",
    )
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
    only = args.only.replace("\\", "/") if args.only else None
    for path in iter_source_files():
        if only and only not in str(path).replace("\\", "/"):
            continue
        for block in extract_blocks(path):
            block["output_file"] = output_name(block["class_name"], block["code"])
            block["effective_quality"] = (
                block.get("quality")
                or (f"{args.quality}_quality" if args.quality else None)
                or "example_quality"
            )
            block["env_tags"] = tags_for_block(block)
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
        expected_tags = {t: ENV_TAGS[t] for t in block["env_tags"]}
        if (
            entry
            and entry.get("sha256") == block["output_file"]
            and entry.get("quality") == block["effective_quality"]
            and entry.get("env_tags", {}) == expected_tags
            and (target_dir / f"{block['output_file']}.{ext}").exists()
        ):
            skipped += 1
            continue
        todo.append(block)

    print(f"{skipped} already cached, {len(todo)} to render")
    if not todo or args.check:
        return 0 if not todo else 1

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
                block["effective_quality"],
                str(workdir),
            )
        )

    failures = 0
    done = 0
    t0 = time.time()
    total = len(tasks)
    todo_by_key = {b["output_file"]: b for b in todo}
    with multiprocessing.Pool(args.workers) as pool:
        for key, src, ok, error, q in pool.imap_unordered(render_block, tasks):
            done += 1
            pct = done * 100 // total
            if not ok:
                failures += 1
                print(
                    f"[{pct:>3}%] ({done}/{total}) "
                    f"\033[31mFAILED\033[0m {key}\n{error}",
                    file=sys.stderr,
                )
                continue
            print(f"[{pct:>3}%] ({done}/{total}) \033[32mOK\033[0m {key}")
            src = Path(src)
            if src.suffix == ".png":
                shutil.copyfile(src, images_out / src.name)
            else:
                shutil.copyfile(src, videos_out / src.name)
            block = todo_by_key[key]
            manifest[key] = {
                "sha256": key,
                "ext": src.suffix.lstrip("."),
                "quality": q,
                "env_tags": {t: ENV_TAGS[t] for t in block["env_tags"]},
            }

    shutil.rmtree(work_root, ignore_errors=True)
    manifest_path.write_text(json.dumps(manifest, indent=1, sort_keys=True))

    print(
        f"Rendered {len(todo) - failures}/{len(todo)} examples "
        f"in {time.time() - t0:.0f}s; cache now holds {len(manifest)} entries"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

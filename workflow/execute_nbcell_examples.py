# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Execute every ``.. nbcell::`` block and cache the real stdout.

The Docs media workflow runs this on every push; the resulting
``_nbcell_cache.json`` is pushed to the ``rtd-media`` branch and copied
next to ``nbcell_directive.py`` before the Read the Docs build. The
directive maps each cell's normalized source through
:func:`nbcell_directive.normalize_code`; a cache hit replaces the
hand-written ``:output:`` with the real stdout, so doc examples always
show current, true results. Cells that fail to execute (missing files,
network-dependent CLI demos, optional extras absent) are left out of the
cache, and the directive falls back to the authored output.

Cells of one document execute sequentially in a single subprocess with a
shared namespace (later cells may use variables from earlier ones, like a
notebook). Console cells run their command via ``subprocess``; a cell
whose output language is ``pytb`` records a raised exception's traceback
as its output, like a notebook would.

Usage:
    python workflow/execute_nbcell_examples.py [--out PATH] [--only SUBSTR]
    python workflow/execute_nbcell_examples.py --check [--cache PATH]
    python workflow/execute_nbcell_examples.py --runner JOB_JSON RESULT_JSON
"""

import argparse
import io
import json
import re
import shlex
import subprocess
import sys
import tempfile
import tokenize
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "docs" / "source" / "_extensions"))

from nbcell_directive import normalize_code  # noqa: E402

NBCELL_RE = re.compile(r"( *)\.\. nbcell::")
OPTION_RE = re.compile(r"^\s*:([\w-]+):\s*(.*)$")
DOC_TIME = 300  # seconds per document
CONSOLE_TIME = 90  # seconds per console cell


def iter_source_files():
    for p in sorted((ROOT / "docs" / "source").rglob("*.rst")):
        yield p
    for p in sorted((ROOT / "manim_extensions").rglob("*.py")):
        if "__pycache__" not in p.parts:
            yield p


def extract_cells(text):
    """Yield ``(code, options)`` for every nbcell block in raw source text."""
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        m = NBCELL_RE.match(lines[i])
        if not m:
            i += 1
            continue
        dind = len(m.group(1))
        j = i + 1
        options = {}
        cur_key = None
        # option block: non-blank lines deeper than the directive
        while j < len(lines):
            ln = lines[j]
            if not ln.strip():
                j += 1
                break
            ind = len(ln) - len(ln.lstrip())
            if ind <= dind:
                break
            om = OPTION_RE.match(ln)
            if om and ind == dind + 4:
                cur_key = om.group(1)
                options[cur_key] = om.group(2)
            elif cur_key and ind > dind + 4:
                options[cur_key] += "\n" + ln.strip()
            j += 1
        # content block: deeper-than-directive lines until a dedent
        content = []
        while j < len(lines):
            ln = lines[j]
            if not ln.strip():
                content.append("")
                j += 1
                continue
            ind = len(ln) - len(ln.lstrip())
            if ind <= dind:
                break
            content.append(ln[dind + 4:])
            j += 1
        while content and not content[-1].strip():
            content.pop()
        while content and not content[0].strip():
            content.pop(0)
        if content:
            yield "\n".join(content), options
        i = max(j, i + 1)


def collect_cells(only=None):
    """Return {source_name: [cell, ...]} across all rst/docstring sources."""
    docs = {}
    for path in iter_source_files():
        rel = path.relative_to(ROOT).as_posix()
        if only and only not in rel:
            continue
        text = path.read_text(encoding="utf-8")
        if path.suffix == ".py":
            chunks = []
            try:
                toks = list(tokenize.generate_tokens(io.StringIO(text).readline))
            except Exception:
                continue
            for tok in toks:
                if tok.type == tokenize.STRING:
                    chunks.append(tok.string)
        else:
            chunks = [text]
        cells = []
        for chunk in chunks:
            for code, options in extract_cells(chunk):
                cells.append({
                    "hash": normalize_code(code),
                    "code": code,
                    "language": options.get("language", "python"),
                    "console": "prompt-in" in options,
                    "pytb": options.get("output-language") == "pytb",
                })
        if cells:
            context = None
            if path.suffix == ".py":
                context = ".".join(path.relative_to(ROOT).with_suffix("").parts)
            docs[rel] = {"module": context, "cells": cells}
    return docs


def run_document(module, cells, cwd):
    """Execute one document's cells in a fresh subprocess. Returns results."""
    job = {"cwd": str(cwd), "module": module, "cells": cells}
    with tempfile.NamedTemporaryFile(
        "w", suffix=".json", delete=False, encoding="utf-8"
    ) as jf:
        json.dump(job, jf)
        job_path = jf.name
    result_path = job_path + ".out"
    try:
        proc = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()),
             "--runner", job_path, result_path],
            capture_output=True, text=True, timeout=DOC_TIME, cwd=ROOT,
        )
        if proc.returncode != 0:
            sys.stderr.write(f"runner failed for {job_path}:\n{proc.stderr[-800:]}\n")
            return {}
        return json.loads(Path(result_path).read_text(encoding="utf-8"))
    except subprocess.TimeoutExpired:
        sys.stderr.write(f"TIMEOUT executing document {job_path}\n")
        return {}
    finally:
        Path(job_path).unlink(missing_ok=True)
        Path(result_path).unlink(missing_ok=True)


def prepare_cwd():
    """Scratch cwd with the molecule files the examples reference."""
    tmp = Path(tempfile.mkdtemp(prefix="nbcell-"))
    for mol in list(ROOT.glob("*.mol")) + list((ROOT / "docs" / "source").glob("*.mol")):
        (tmp / mol.name).write_bytes(mol.read_bytes())
    legacy = tmp / "examples" / "molecule_files" / "mol_files"
    legacy.mkdir(parents=True)
    for mol in (ROOT / "docs" / "source").glob("*.mol"):
        (legacy / mol.name).write_bytes(mol.read_bytes())
    return tmp


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="media_cache/_nbcell_cache.json")
    parser.add_argument("--cache", default=None,
                        help="existing cache to merge (defaults to --out)")
    parser.add_argument("--only", default=None, help="restrict to matching paths")
    parser.add_argument("--check", action="store_true",
                        help="exit 1 if any cell hash is missing from the cache")
    parser.add_argument("--runner", nargs=2, help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.runner:
        return runner_mode(*args.runner)

    out_path = Path(args.out)
    cache_path = Path(args.cache) if args.cache else out_path
    old = {"version": 1, "cells": {}}
    if cache_path.exists():
        try:
            old = json.loads(cache_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    docs = collect_cells(only=args.only)
    total = sum(len(c) for c in docs.values())
    if args.check:
        missing = [c["hash"] for doc in docs.values() for c in doc["cells"]
                   if c["hash"] not in old.get("cells", {})]
        if missing:
            print(f"{len(missing)}/{total} nbcell outputs not cached")
            return 1
        print(f"all {total} nbcell outputs cached")
        return 0

    cells_cache = dict(old.get("cells", {}))
    executed = failed = 0
    for rel, doc in sorted(docs.items()):
        cwd = prepare_cwd()
        try:
            results = run_document(doc["module"], doc["cells"], cwd)
        finally:
            import shutil
            shutil.rmtree(cwd, ignore_errors=True)
        for cell in doc["cells"]:
            res = results.get(cell["hash"])
            if res and res.get("ok"):
                cells_cache[cell["hash"]] = {"ok": True, "stdout": res["stdout"]}
                executed += 1
            else:
                failed += 1
                if cell["hash"] not in cells_cache:
                    cells_cache[cell["hash"]] = {"ok": False, "stdout": ""}
        print(f"{rel}: {len(doc['cells'])} cells")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps({"version": 1, "cells": cells_cache}, indent=1) + "\n",
        encoding="utf-8",
    )
    print(f"cache: {len(cells_cache)} cells "
          f"({executed} freshly executed, {failed} failed this run)")
    print(f"wrote {out_path}")
    return 0


def runner_mode(job_path, result_path):
    """Execute cells of one document; internal entry point."""
    job = json.loads(Path(job_path).read_text(encoding="utf-8"))
    cwd = Path(job["cwd"])
    import os
    os.chdir(cwd)
    namespace = {"__name__": "__nbcell__"}
    prelude = "from manim import *\n"
    if job.get("module"):
        # Docstring examples assume their own module's namespace.
        prelude += f"from {job['module']} import *\n"
    try:
        exec(prelude, namespace)  # noqa: S102
    except Exception:
        traceback.print_exc()
        Path(result_path).write_text("{}", encoding="utf-8")
        return 0
    results = {}
    dead = False
    for cell in job["cells"]:
        if dead:
            continue
        if cell["console"]:
            try:
                cmd = shlex.split(cell["code"])
                if cmd and cmd[0] == "python":
                    cmd[0] = sys.executable
                proc = subprocess.run(
                    cmd, cwd=cwd, capture_output=True, text=True,
                    timeout=CONSOLE_TIME,
                )
                ok = proc.returncode == 0
                results[cell["hash"]] = {
                    "ok": ok, "stdout": (proc.stdout + proc.stderr).strip("\n"),
                }
            except Exception:
                results[cell["hash"]] = {"ok": False, "stdout": ""}
                dead = True
            continue
        buf = io.StringIO()
        try:
            with __import__("contextlib").redirect_stdout(buf):
                exec(cell["code"], namespace)  # noqa: S102
            results[cell["hash"]] = {"ok": True, "stdout": buf.getvalue().strip("\n")}
        except Exception:
            if cell["pytb"]:
                results[cell["hash"]] = {
                    "ok": True, "stdout": traceback.format_exc().strip("\n"),
                }
            else:
                results[cell["hash"]] = {"ok": False, "stdout": ""}
                dead = True  # namespace may be broken for the rest
    Path(result_path).write_text(json.dumps(results), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())

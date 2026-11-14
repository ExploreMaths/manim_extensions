# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Enforce ``:files:`` for examples that read bundled sample files.

Rules:
    - Every ``.. manim::`` / ``.. nbcell::`` block that reads a data file
      (``.mol``, ``.sdf``, ``.asnt``, ``.json``, ``.xml``, media, ...) MUST
      declare it with ``:files:``.
    - Files listed in ``:files:`` MUST exist inside the ``examples/`` tree
      and be referenced by bare name.
    - Example code MUST NOT build paths such as ``examples/...``,
      ``../examples/...``, ``_static/...`` or ``Path(__file__)``.
    - Files the example writes itself (``to_csv``, ``imsave``, ``savefig``,
      ``open(..., "w")``) are generated at run time and need no ``:files:``.

Usage:
    python workflow/validate_example_files.py
"""

import re
import sys
from pathlib import Path

from _context import DOCS, EXAMPLES, ROOT, SRC
from _example_assets import parse_file_list, resolve_asset

DIRECTIVE_RE = re.compile(r"^(\s*)\.\. (manim|nbcell)::")
OPTION_RE = re.compile(r"^\s*:([\w-]+):\s*(.*)$")

DATA_EXTENSIONS = (
    "mol",
    "sdf",
    "asnt",
    "json",
    "xml",
    "csv",
    "mp4",
    "png",
    "jpg",
    "jpeg",
    "svg",
    "gif",
    "obj",
    "mtl",
    "wav",
    "mp3",
)
QUOTED_RE = re.compile(r'"([^"\n]+)"|\'([^\'\n]+)\'')
PATH_MARKERS = (
    '"examples/',
    "'examples/",
    "../examples",
    '"_static"',
    "'_static'",
    "Path(__file__)",
)
WRITE_CALLS = ("to_csv", "to_json", "to_excel", "imsave", "savefig", "savetxt")


def iter_sources():
    """Yield the tracked files that can hold manim/nbcell examples."""
    for path in sorted(DOCS.rglob("*.rst")):
        if "_build" in path.parts or "_static" in path.parts:
            continue
        yield path
    for path in sorted(SRC.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        yield path


def iter_blocks(text):
    """Yield ``(lineno, kind, options, body)`` for every example directive."""
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        match = DIRECTIVE_RE.match(lines[i])
        if not match:
            i += 1
            continue
        indent = len(match.group(1))
        options = {}
        body = []
        current = None
        j = i + 1
        in_body = False
        while j < len(lines):
            line = lines[j]
            if not line.strip():
                in_body = True
                body.append("")
                j += 1
                continue
            line_indent = len(line) - len(line.lstrip())
            if line_indent <= indent:
                break
            option_match = OPTION_RE.match(line)
            if not in_body and option_match and line_indent == indent + 3:
                current = option_match.group(1)
                options[current] = option_match.group(2).strip()
            elif not in_body and current and line_indent > indent + 3:
                options[current] += " " + line.strip()
            else:
                in_body = True
                body.append(line)
            j += 1
        yield i + 1, match.group(2), options, "\n".join(body)
        i = j


def quoted_names(body):
    """File-looking literals in the example body.

    A literal counts as a bundled sample when it resolves inside
    ``examples/`` (bare name or nested path); path-like literals are
    reported so a broken ``examples/...`` reference is still caught.
    """
    names = []
    for first, second in QUOTED_RE.findall(body):
        value = first or second
        if "." not in value:
            continue
        if value.lower().rsplit(".", 1)[-1] not in DATA_EXTENSIONS:
            continue
        if "/" in value or resolve_asset(Path(value).name, ROOT, EXAMPLES) is not None:
            names.append(value)
    return names


def is_generated(name, body):
    """True when the example writes ``name`` itself before reading it."""
    for call in WRITE_CALLS:
        if re.search(rf'{call}\([^)]*["\']{re.escape(name)}["\']', body):
            return True
    if re.search(rf'open\([^)]*["\']{re.escape(name)}["\'][^)]*["\']w', body):
        return True
    return False


def check_file(path):
    """Return ``(directives, errors)`` for one source file."""
    rel = path.relative_to(ROOT).as_posix()
    errors = []
    directives = 0
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return 0, []
    for lineno, kind, options, body in iter_blocks(text):
        directives += 1
        declared = parse_file_list(options.get("files", ""))
        names = [name for name in quoted_names(body) if not is_generated(name, body)]
        if names and not declared:
            errors.append(
                f"{rel}:{lineno} missing-files: {kind} example reads "
                f"{', '.join(sorted(set(names)))} but has no ':files:' option"
            )
        for marker in PATH_MARKERS:
            if marker in body:
                errors.append(
                    f"{rel}:{lineno} path-instead-of-files: {kind} example builds a path "
                    f"containing {marker!r}; declare the file with ':files:' "
                    "and use its bare name"
                )
        for name in declared:
            if resolve_asset(name, ROOT, EXAMPLES) is None:
                errors.append(
                    f"{rel}:{lineno} unknown-asset: ':files:' entry {name!r} "
                    "does not exist under examples/"
                )
        for name in names:
            bare = Path(name).name
            if declared and bare not in declared:
                errors.append(
                    f"{rel}:{lineno} undeclared-file: {name!r} is read but not "
                    "listed in ':files:'"
                )
    return directives, errors


def main():
    directives = 0
    errors = []
    files = 0
    for path in iter_sources():
        count, found = check_file(path)
        if count:
            files += 1
            directives += count
            errors.extend(found)
    if errors:
        for error in errors:
            print(error)
        print(f"FAIL example files {len(errors)} problems in {files} files")
        return 1
    print(f"PASS example files {directives} directives in {files} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())

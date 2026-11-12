# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Validate class names used by ``.. manim::`` documentation examples.

Rules:

* The directive name must not contain ``Example``. Examples are named for
  what they show, mirroring Manim's own examples (``BooleanOperations``,
  ``SquareToCircle``), not for their role in the documentation.
* The directive name must be a PascalCase identifier.
* The directive must name a class defined at the top level of its own code
  block, so the rendered scene and the requested name cannot drift apart.

Usage:
    python workflow/validate_example_names.py
"""

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "workflow"))

from render_doc_examples import extract_blocks, iter_source_files  # noqa: E402

NAME_RE = re.compile(r"^[A-Z][A-Za-z0-9]*$")


def check_block(block):
    """Return a list of (rule, line, detail) for one example block."""
    requested = block["class_name"]
    problems = []

    if "Example" in requested:
        problems.append(
            (
                "example-suffix",
                1,
                f"rename {requested} after what it shows, without 'Example'",
            )
        )
    if not NAME_RE.fullmatch(requested):
        problems.append(
            (
                "class-name-format",
                1,
                f"{requested} is not a PascalCase identifier",
            )
        )

    try:
        tree = ast.parse(block["code"])
    except SyntaxError as exc:
        return problems + [("parse-error", exc.lineno or 0, exc.msg)]

    classes = [n.name for n in tree.body if isinstance(n, ast.ClassDef)]
    if requested not in classes:
        detail = "directive names {}, code defines {}".format(
            requested,
            ", ".join(classes) if classes else "no top-level class",
        )
        problems.append(("class-name-mismatch", 1, detail))
    return problems


def main():
    total = 0
    bad = 0
    for path in iter_source_files():
        for block in extract_blocks(path):
            total += 1
            problems = check_block(block)
            if problems:
                bad += 1
                rel = Path(block["source"])
                for rule, line, detail in problems:
                    prefix = f"{rel}:{line}: {block['class_name']}: "
                    print(f"{prefix}{rule}: {detail}")
    print(f"{total} example block(s) checked; {bad} with name problems")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

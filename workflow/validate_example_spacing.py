# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Validate blank-line layout in ``.. manim::`` examples.

Rules:
    - Import statements form one block: no blank lines between them.
    - Exactly one blank line separates the import block (and any top-level
      setup such as ``config`` assignments) from the scene class.
    - ``class ...`` and its ``def construct`` are adjacent: no blank line.
    - Inside ``construct``, a blank line is only a stage separator: it must
      either introduce a comment or follow a ``self.play`` / ``self.wait`` /
      ``self.add`` / ``self.remove`` call. A single blank line only; no blank
      directly after ``def construct``.

Usage:
    python workflow/validate_example_spacing.py
"""

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "workflow"))

from render_doc_examples import extract_blocks, iter_source_files  # noqa: E402

ACTION_PREFIXES = ("self.play(", "self.wait(", "self.add(", "self.remove(")
IMPORT_TYPES = (ast.Import, ast.ImportFrom)


def starts_action(line):
    return line.startswith(ACTION_PREFIXES)


def import_nodes(tree):
    return [n for n in tree.body if isinstance(n, IMPORT_TYPES)]


def top_level_after_imports(tree):
    """Return the last top-level node before the first class, if any."""
    before = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            return before[-1] if before else None
    return None


def check_block(block):
    """Return a list of (rule, line, detail)."""
    code = block["code"]
    lines = code.split("\n")
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return [("parse-error", exc.lineno or 0, exc.msg)]

    problems = []
    imports = import_nodes(tree)
    for first, second in zip(imports, imports[1:]):
        start = first.end_lineno + 1
        end = second.lineno - 1
        if any(not lines[i - 1].strip() for i in range(start, end + 1)):
            problems.append(
                (
                    "blank-between-imports",
                    second.lineno,
                    "remove blank line(s) between imports",
                )
            )

    scene = next((n for n in tree.body if isinstance(n, ast.ClassDef)), None)
    if scene is None:
        return problems

    previous = top_level_after_imports(tree)
    if previous is not None:
        gap = scene.lineno - previous.end_lineno - 1
        if gap != 1:
            problems.append(
                (
                    "import-class-spacing",
                    scene.lineno,
                    f"expected exactly 1 blank line before class, found {gap}",
                )
            )

    construct = next(
        (
            n
            for n in scene.body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            and n.name == "construct"
        ),
        None,
    )
    if construct is None:
        return problems

    earlier_body = [n for n in scene.body if n.lineno < construct.lineno]
    if not earlier_body and construct.lineno != scene.lineno + 1:
        problems.append(
            (
                "class-def-blank",
                construct.lineno,
                "remove blank line(s) between class and def construct",
            )
        )

    body = construct.body
    start, end = body[0].lineno, body[-1].end_lineno
    if start > construct.lineno + 1:
        blank_lines = range(construct.lineno + 1, start)
        if any(not lines[i - 1].strip() for i in blank_lines):
            problems.append(
                (
                    "blank-after-def",
                    construct.lineno + 1,
                    "remove blank line after def construct",
                )
            )

    for i in range(start + 1, end):
        if lines[i - 1].strip():
            continue
        # part of a blank run? report once at its first line
        if i > start + 1 and not lines[i - 2].strip():
            continue
        prev = next(
            (
                lines[j - 1].strip()
                for j in range(i - 1, construct.lineno, -1)
                if lines[j - 1].strip()
            ),
            "",
        )
        nxt = next(
            (
                lines[j - 1].strip()
                for j in range(i + 1, end + 1)
                if lines[j - 1].strip()
            ),
            "",
        )
        if not prev or not nxt:
            continue
        allowed = nxt.startswith("#") or (
            starts_action(prev) and not starts_action(nxt)
        )
        if not allowed:
            problems.append(
                (
                    "construct-blank",
                    i,
                    "blank lines in construct must start a stage "
                    "(comment or after play/wait/add/remove)",
                )
            )
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
    print(f"{total} example block(s) checked; {bad} with spacing problems")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())

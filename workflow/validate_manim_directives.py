# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Validate `:save_last_frame:` and final-hold rules in manim directive blocks.

Rules:
    - Static scenes (no self.play / self.animate)  -> MUST have :save_last_frame:
    - Animated scenes (has self.play / self.animate) -> MUST NOT have :save_last_frame:
    - Static scenes with :save_last_frame: should NOT use self.wait() (redundant)
    - Static scenes without :save_last_frame: MUST have it added
    - Non-looping animated scenes MUST end with ``self.wait()`` (one second)
    - Seamless-loop scenes are exempt; mark them with a
      ``# loops seamlessly`` comment, or use ``:save_as_gif:``

Usage:
    python validate_manim_directives.py
"""

import ast
import re
import sys
import textwrap
from pathlib import Path

from _context import DOCS, ROOT, SRC

ANIMATION_PATTERNS = [
    re.compile(r"\bself\.play\s*\("),
    re.compile(r"\bself\.animate\s*\("),
    re.compile(r"\bself\.animate\.value_tracker\b"),
    re.compile(r"\bsuper\(\)\.construct\s*\("),
    re.compile(r"\.play\s*\(\s*self\s*\)"),
    re.compile(r"\bself\.compass_\w+\s*\("),
    re.compile(r"\bself\.draw_(arc|line)\s*\("),
    re.compile(r"\bself\.put_(compass_aside|pencil_away|ruler_aside)\s*\("),
    re.compile(r"\bself\.rotate_compass_about_niddle_tip\s*\("),
]

WAIT_PATTERN = re.compile(r"\bself\.wait\s*\(")

MIN_FINAL_WAIT = 1.0

LOOP_MARKER_RE = re.compile(
    r"(?:loops?\s+seamlessly|seamless(?:ly)?\s+loop|first\s+and\s+last\s+frames?\s+match)",
    re.IGNORECASE,
)

SKIP_FILES = {
    "manim_directive.py",
}


def has_animation(code: str) -> bool:
    for pat in ANIMATION_PATTERNS:
        if pat.search(code):
            return True
    return False


def has_wait(code: str) -> bool:
    return bool(WAIT_PATTERN.search(code))


def has_loop_marker(code: str) -> bool:
    """Return whether the example is explicitly marked as a seamless loop."""
    return bool(LOOP_MARKER_RE.search(code))


def final_construct_statement(code: str, class_name: str):
    """Return the last statement of the scene's ``construct`` method."""
    try:
        tree = ast.parse(textwrap.dedent(code))
    except SyntaxError:
        return None
    cls = next(
        (
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef) and node.name == class_name
        ),
        None,
    )
    if cls is None:
        return None
    construct = next(
        (
            node
            for node in cls.body
            if isinstance(node, ast.FunctionDef) and node.name == "construct"
        ),
        None,
    )
    if construct is None or not construct.body:
        return None
    return construct.body[-1]


def delegated_construct(statement) -> bool:
    """Return whether the scene delegates its body to a parent scene."""
    if not isinstance(statement, ast.Expr) or not isinstance(statement.value, ast.Call):
        return False
    func = statement.value.func
    return (
        isinstance(func, ast.Attribute)
        and func.attr == "construct"
        and isinstance(func.value, ast.Call)
        and isinstance(func.value.func, ast.Name)
        and func.value.func.id == "super"
    )


def wait_seconds(statement) -> float | None:
    """Return the duration of a trailing ``self.wait(...)`` call, if any."""
    if not isinstance(statement, ast.Expr) or not isinstance(statement.value, ast.Call):
        return None
    func = statement.value.func
    if not isinstance(func, ast.Attribute) or func.attr != "wait":
        return None
    if not isinstance(func.value, ast.Name) or func.value.id != "self":
        return None
    if not statement.value.args:
        return 1.0
    try:
        return float(ast.literal_eval(statement.value.args[0]))
    except (ValueError, TypeError):
        return None


def check_final_wait(block) -> list[dict]:
    """Require a one-second hold at the end of a non-looping animation."""
    if block["has_save_as_gif"] or has_loop_marker(block["code"]):
        return []
    statement = final_construct_statement(block["code"], block["class_name"])
    if statement is None or delegated_construct(statement):
        return []
    seconds = wait_seconds(statement)
    if seconds is not None and seconds >= MIN_FINAL_WAIT:
        return []
    if seconds is None:
        message = (
            "Non-looping animated examples must end with `self.wait()` or longer; "
            "mark a seamless loop with a `# loops seamlessly` comment or use `:save_as_gif:`"
        )
        issue_type = "ANIMATED_MISSING_FINAL_WAIT"
    else:
        message = (
            f"Final `self.wait({seconds:g})` is shorter than {MIN_FINAL_WAIT:g}s; "
            "non-looping animated examples need at least one second"
        )
        issue_type = "ANIMATED_SHORT_FINAL_WAIT"
    return [
        {
            "type": issue_type,
            "line": block["start_line"],
            "class_name": block["class_name"],
            "message": message,
            "code_preview": block["code"][:200],
        }
    ]


CODE_DIRECTIVE_RE = re.compile(r"^(\s*)\.\.\s*(code-block|sourcecode|code)::")
OPTION_LIKE_RE = re.compile(r"^\s*:[\w-]+:")


def mask_code_directive_bodies(lines):
    """Blank out literal code inside ``code-block``/``sourcecode``/``code``.

    Directive text shown *inside* a code sample is documentation, not a
    directive the build should execute, so the scanners must ignore it.
    """
    masked = list(lines)
    i = 0
    while i < len(masked):
        m = CODE_DIRECTIVE_RE.match(masked[i])
        if not m:
            i += 1
            continue
        base = len(m.group(1))
        j = i + 1
        while j < len(masked):
            line = masked[j]
            if not line.strip():
                masked[j] = ""
                j += 1
                continue
            indent = len(line) - len(line.lstrip())
            if indent <= base:
                break
            masked[j] = ""
            j += 1
        masked[i] = ""
        i = j
    return masked


def extract_manim_blocks(file_path: Path):
    text = file_path.read_text(encoding="utf-8")
    lines = mask_code_directive_bodies(text.splitlines())

    blocks = []
    i = 0
    while i < len(lines):
        line = lines[i]

        m = re.match(r"\s*\.\.\s+manim::\s+(\S+)", line)
        if m:
            class_name = m.group(1)
            has_save_last_frame = False
            has_save_as_gif = False
            j = i + 1
            while j < len(lines) and (
                re.match(r"\s*:[\w_]+:", lines[j]) or lines[j].strip() == ""
            ):
                opt_match = re.match(r"\s*:(save_last_frame|save_as_gif):", lines[j])
                if opt_match:
                    if opt_match.group(1) == "save_last_frame":
                        has_save_last_frame = True
                    elif opt_match.group(1) == "save_as_gif":
                        has_save_as_gif = True
                j += 1

            code_lines = []
            code_start_line = j + 1
            while j < len(lines):
                current = lines[j]
                if re.match(r"\s*\.\.\s+manim::", current):
                    break
                stripped = current.strip()
                if stripped == '"""' or stripped == "'''":
                    break
                if stripped == "":
                    if j + 1 < len(lines) and not re.match(r"\s{3,}", lines[j + 1]):
                        break
                    if j == len(lines) - 1:
                        break
                code_lines.append(lines[j])
                j += 1

            code = "\n".join(code_lines)
            blocks.append(
                {
                    "class_name": class_name,
                    "has_save_last_frame": has_save_last_frame,
                    "has_save_as_gif": has_save_as_gif,
                    "code": code,
                    "start_line": i + 1,
                    "code_start_line": code_start_line,
                }
            )
            i = j
        else:
            i += 1

    return blocks


def check_file(file_path: Path):
    blocks = extract_manim_blocks(file_path)
    issues = []
    for block in blocks:
        if "from manim import *" not in {
            line.strip() for line in block["code"].splitlines()
        }:
            issues.append(
                {
                    "type": "MISSING_MANIM_IMPORT",
                    "line": block["start_line"],
                    "class_name": block["class_name"],
                    "message": "Manim examples must write `from manim import *` explicitly (the directive does not inject it)",
                    "code_preview": block["code"][:200],
                }
            )
            continue

        animated = has_animation(block["code"])
        wait_used = has_wait(block["code"])

        if animated and block["has_save_last_frame"]:
            issues.append(
                {
                    "type": "ANIMATED_HAS_SAVE_LAST_FRAME",
                    "line": block["start_line"],
                    "class_name": block["class_name"],
                    "message": "Has self.play/self.animate but also has :save_last_frame: (should REMOVE :save_last_frame:)",
                    "code_preview": block["code"][:200],
                }
            )
        elif not animated and not block["has_save_last_frame"] and wait_used:
            issues.append(
                {
                    "type": "STATIC_WITH_WAIT_MISSING_SAVE",
                    "line": block["start_line"],
                    "class_name": block["class_name"],
                    "message": "Is static (no self.play/self.animate), uses self.wait(), but missing :save_last_frame: (should ADD :save_last_frame: and REMOVE self.wait())",
                    "code_preview": block["code"][:200],
                }
            )
        elif not animated and not block["has_save_last_frame"]:
            issues.append(
                {
                    "type": "STATIC_MISSING_SAVE_LAST_FRAME",
                    "line": block["start_line"],
                    "class_name": block["class_name"],
                    "message": "Is static (no self.play/self.animate) but missing :save_last_frame: (should ADD :save_last_frame:)",
                    "code_preview": block["code"][:200],
                }
            )
        elif not animated and block["has_save_last_frame"] and wait_used:
            issues.append(
                {
                    "type": "STATIC_HAS_WAIT_REDUNDANT",
                    "line": block["start_line"],
                    "class_name": block["class_name"],
                    "message": "Is static with :save_last_frame: but also uses self.wait() (self.wait() is redundant, REMOVE it)",
                    "code_preview": block["code"][:200],
                }
            )

        if animated and not block["has_save_last_frame"]:
            issues.extend(check_final_wait(block))

    return issues


def main():
    targets = [
        SRC,
        DOCS,
    ]

    py_files = []
    for target in targets:
        if target.exists():
            py_files.extend(target.rglob("*.py"))
            py_files.extend(target.rglob("*.rst"))

    all_issues = {}
    total_blocks = 0
    files_with_blocks = set()
    total_checked = 0

    for fp in sorted(set(py_files)):
        if fp.name in SKIP_FILES:
            continue
        blocks = extract_manim_blocks(fp)
        if blocks:
            files_with_blocks.add(str(fp))
            total_blocks += len(blocks)
            total_checked += len(blocks)
            issues = check_file(fp)
            if issues:
                all_issues[str(fp)] = issues

    if all_issues:
        total_issues = sum(len(v) for v in all_issues.values())
        print(f"FAIL  manim-directives  {total_issues} issue(s)\n")
        for fp, issues in all_issues.items():
            for issue in issues:
                rel = Path(fp).relative_to(ROOT)
                print(
                    f"  {rel}:{issue['line']}  {issue['type'].lower()}: {issue['message']}"
                )
        print(f"\nTotal: {total_issues} issue(s)")
        return 1

    print(
        f"PASS  manim-directives  {total_blocks} block(s) in {len(files_with_blocks)} file(s)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

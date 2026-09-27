# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Validate reStructuredText formatting in docs and Python docstrings.

RST requires every block-level element (bullet list, enumeration list,
directive, line block, field list, transition, table, ...) to be
separated from the preceding paragraph by a blank line.  When that blank
line is missing the result is *not* a parse error in most cases:
docutils silently renders the would-be list as ordinary prose, so the
breakage only shows up in the rendered output.

This script catches the problem with two complementary checks:

1. **Abutting-block check** (regex-based).  Flags a bullet, enumeration,
   directive, line-block, field-list, transition or table marker that
   directly follows a non-blank prose line.  Consecutive items of the
   same list, list-table rows and section underlines are allowed.  Lines
   inside a directive or literal block (indented more than the ``..
   directive::`` / ``::`` line) are skipped, because they are code, not
   RST.
2. **docutils parse check**.  Parses each RST fragment with docutils and
   reports ``WARNING``/``ERROR``/``SEVERE`` system messages.  Sphinx
   extension directives and roles (``.. manim::``, ``:class:``, ...) and
   ``.. include::`` resolution failures are filtered out, since they
   only occur in standalone parsing and are resolved by Sphinx.

Both ``docs/source/**/*.rst`` files and docstrings in
``manim_extensions/**/*.py`` are scanned.

Usage::

    python workflow/validate_rst.py
    python workflow/validate_rst.py --only manim_extensions/geometry.py

Exit code 0 means no violations; exit code 1 means at least one was
found.
"""

from __future__ import annotations

import argparse
import ast
import io
import re
import sys
import textwrap
import warnings
from pathlib import Path

# docutils emits deprecation warnings on import under Python 3.12+; the
# lint runs in CI where warnings are noise, so suppress them.
warnings.filterwarnings("ignore", category=DeprecationWarning)

import docutils.frontend  # noqa: E402
import docutils.nodes  # noqa: E402
import docutils.parsers.rst  # noqa: E402
import docutils.utils  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs" / "source"
SRC = ROOT / "manim_extensions"

SKIP_DIR_PARTS = {"fontawesome", "__pycache__", ".git"}

# ---------------------------------------------------------------------------
# Block-start patterns (matched against a stripped line).
# ---------------------------------------------------------------------------
BULLET_RE = re.compile(r"^[-*+][ \t]+")
# Enumerated list items: arabic, auto-enumerator (#), single letter, or
# roman numerals, followed by a period and whitespace.
ENUM_RE = re.compile(r"^(\d+|#|[a-zA-Z]|[ivxlcdmIVXLCDM]+)\.[ \t]+")
DIRECTIVE_RE = re.compile(r"^\.\.[ \t]+\w[\w.:-]*::")
LINEBLOCK_RE = re.compile(r"^\|[ \t]")
# A field list item starts with ``:name:`` and is followed by whitespace
# or end-of-line.  An inline interpreted-text role such as ``:class:`text```
# has a backtick right after the closing colon and must NOT match.
FIELD_RE = re.compile(r"^:[^:\n]+:(?:[ \t]+|$)")
TRANSITION_RE = re.compile(r"^-{4,}$")
# Simple table borders contain internal whitespace (e.g. ``====  ====``);
# a bare run of ``=`` with no spaces is a section title underline.
SIMPLE_TABLE_RE = re.compile(r"^=[ \t]+=[ \t=]*$")
GRID_TABLE_RE = re.compile(r"^\+[-=+:]+\+$")
# A section underline is a bare run of one punctuation character with no
# internal whitespace (====, ----, ~~~~, ...).
SECTION_UNDERLINE_RE = re.compile(r"^[=\-~`'\"^_*+#]{3,}$")
# A line ending in ``::`` (that is not itself a directive) introduces a
# literal block; the following indented lines are code.
LITERAL_BLOCK_RE = re.compile(r"::$")

# ---------------------------------------------------------------------------
# Indentation rules
# ---------------------------------------------------------------------------
# Normal RST block content (directive body, list continuation,
# definition-list description) is indented 3 spaces relative to its
# parent block.  Code block content (literal block after ``::``, or the
# body of a code-producing directive) is indented 4 spaces.
NORMAL_DELTA = 3
CODE_DELTA = 4

# Directives whose body is code and whose first body line must be
# indented +4 (literal ``::`` blocks and ``raw``/``math`` directives).
# Subsequent lines are code with their own indentation and are not
# checked.
CODE_DIRECTIVES = frozenset({"raw", "math", "math-block"})

# Directives whose body is code but whose top-level body indentation
# follows the normal RST convention of +3 (``manim``, ``nbcell``,
# ``code-block``, ...).  The first body line must be +3; subsequent
# lines are code and are not checked.
MANIM_LIKE_DIRECTIVES = frozenset(
    {"manim", "nbcell", "code-block", "sourcecode", "code"}
)

# A directive option that disables indentation checking for the whole
# block it belongs to (use for ASCII art or other intentional layouts):
#
#     .. code-block:: text
#        :skip-indent:
#        ... (intentional arbitrary indentation)
SKIP_INDENT_OPTION_RE = re.compile(r"^:skip-indent:[ \t]*$")

# A comment directive that disables indentation checking for the block
# that immediately follows it:
#
#     .. rst-check: skip-indent
#     .. code-block:: text
#        ...
SKIP_INDENT_DIRECTIVE_RE = re.compile(r"^\.\.[ \t]+rst-check:[ \t]*skip-indent$")

# docutils messages caused by Sphinx extensions, standalone parsing, or
# numpydoc section conventions (section headers, ``**kwargs``/``*args``
# notation, consecutive definition-list entries).  All of these render
# correctly under Sphinx+numpydoc but confuse plain docutils.
SKIP_PHRASES = (
    "Unknown directive type",
    "Unknown interpreted text role",
    "No directive entry",
    "No role entry",
    'Error in "include" directive',
    '"include" directive',
    "Unexpected section title",
    "Inline strong start-string",
    "Inline emphasis start-string",
    "Definition list ends",
    "Unexpected indentation",
    "Block quote ends",
)

QUOTE_PREFIX_RE = re.compile(r"^[ \t]*[rRbBuU]*(\"\"\"|\"|'''|')")
QUOTE_SUFFIX_RE = re.compile(r"(\"\"\"|\"|'''|')[ \t]*$")


def _block_kind(stripped: str) -> str | None:
    """Return the RST block kind *stripped* starts, or ``None``."""
    if BULLET_RE.match(stripped):
        return "bullet list"
    if ENUM_RE.match(stripped):
        # A line like "3.14" or "1.0" is not a list item: ENUM_RE requires
        # whitespace after the period, so "1.0" (no space) is rejected.
        return "enumeration list"
    if DIRECTIVE_RE.match(stripped):
        return "directive"
    if LINEBLOCK_RE.match(stripped):
        return "line block"
    if FIELD_RE.match(stripped):
        return "field list"
    if TRANSITION_RE.match(stripped):
        return "transition"
    if SIMPLE_TABLE_RE.match(stripped) or GRID_TABLE_RE.match(stripped):
        return "table"
    return None


def check_abutting(lines: list[str]) -> list[tuple[int, str]]:
    """Find block elements that abut the previous line without a blank line.

    Parameters
    ----------
    lines : list of str
        The RST source lines, already dedented (internal indentation is
        preserved, since relative indentation drives the check).

    Returns
    -------
    list of (int, str)
        ``(0-based line index, message)`` for each violation.
    """
    hits: list[tuple[int, str]] = []
    # Indent of the directive / literal-block whose content we are inside.
    # Lines indented deeper than this are code and are skipped.
    block_content_indent: int | None = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())

        if not stripped:
            # A blank line does not by itself end a directive/literal
            # block (code blocks contain blank lines), so keep
            # block_content_indent as-is.
            continue

        if block_content_indent is not None and indent > block_content_indent:
            continue  # inside directive / literal-block content

        # We left the previous block's content region.
        block_content_indent = None

        # Disambiguate a section title underline from a transition or a
        # table border: a bare run of punctuation that directly follows a
        # plain-text line is the underline of that title, not a new block.
        if SECTION_UNDERLINE_RE.match(stripped):
            prev_stripped = lines[i - 1].strip() if i > 0 else ""
            if prev_stripped and _block_kind(prev_stripped) is None:
                continue  # title underline

        kind = _block_kind(stripped)
        if kind is None:
            # Lines ending in ``::`` open a literal block.
            if LITERAL_BLOCK_RE.search(stripped):
                block_content_indent = indent
            continue

        # A directive opens a content block of its own.
        if kind == "directive":
            block_content_indent = indent

        if i == 0:
            continue
        prev_line = lines[i - 1]
        prev_stripped = prev_line.strip()
        if not prev_stripped:
            continue  # blank line precedes -> valid

        # Consecutive item of the same list / row is fine.
        if _block_kind(prev_stripped) == kind:
            continue

        prev_indent = len(prev_line) - len(prev_line.lstrip())
        if prev_indent > indent:
            # The previous line is a continuation of the preceding list
            # item / block; the current block legitimately follows it.
            continue

        # A section underline legitimately precedes the first block.
        if SECTION_UNDERLINE_RE.match(prev_stripped):
            continue

        hits.append(
            (i, f"{kind} directly follows the previous line (missing blank line)")
        )

    return hits


def _directive_name(stripped: str) -> str:
    """Return the lower-cased directive name from a ``.. name::`` line."""
    # ``.. manim:: Foo``  ->  ``manim``
    body = stripped[3:]  # strip leading ".."
    body = body.lstrip()
    name = body.split("::", 1)[0]
    return name.split()[0].lower() if name else ""


def check_indentation(lines: list[str]) -> list[tuple[int, str]]:
    """Check that block content uses the required indentation.

    Rules
    -----
    * Normal directive body (``note``, ``warning``, ...): +3 spaces.
    * Code directive body (``code-block``, ``raw``, ``math``, ...):
      first line +4, subsequent lines are code (not checked).
    * Manim-like directive body (``manim``, ``nbcell``): first line +3,
      subsequent lines are code (not checked).
    * Literal block (after ``::``): first line +4, subsequent lines are
      code (not checked).
    * Bullet / enumeration list-item continuation: aligned with the
      text after the marker (e.g. ``* item`` -> +2).
    * Definition-list description (e.g. numpydoc ``name : type``): +4.

    Tables, section underlines, directive option lines (``:option:``)
    and their multi-line values are exempt.  A block immediately
    following ``.. rst-check: skip-indent`` is exempt from indentation
    checks entirely (use for ASCII art or other intentional layouts).

    Parameters
    ----------
    lines : list of str
        The RST source lines, already dedented (internal indentation is
        preserved, since relative indentation drives the check).

    Returns
    -------
    list of (int, str)
        ``(0-based line index, message)`` for each violation.
    """
    hits: list[tuple[int, str]] = []
    # Stack of [parent_indent, expected_delta, is_code_block, skip_indent].
    # Stored as lists so the ``skip_indent`` flag can be flipped when a
    # ``:skip-indent:`` option is seen inside the block.
    stack: list[list] = []
    # Indent of the first body line of the current code block (once set,
    # deeper lines are treated as code and exempt).
    code_body_indent: int | None = None
    # Indent of the most recent directive option line, for multi-line
    # option values.
    last_option_indent: int | None = None
    # Set by ``.. rst-check: skip-indent``; consumed by the next block.
    pending_skip = False

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        indent = len(line) - len(line.lstrip())

        # ``.. rst-check: skip-indent`` disables indentation checking
        # for the block that immediately follows.
        if SKIP_INDENT_DIRECTIVE_RE.match(stripped):
            pending_skip = True
            continue

        # Section-title underlines and table rows follow their own
        # alignment; do not enforce the delta on them.
        if SECTION_UNDERLINE_RE.match(stripped):
            continue
        if SIMPLE_TABLE_RE.match(stripped) or GRID_TABLE_RE.match(stripped):
            continue

        # Pop blocks whose content region this line is no longer inside.
        while stack and stack[-1][0] >= indent:
            stack.pop()
            code_body_indent = None

        in_code = bool(stack) and stack[-1][2]
        skip_indent = bool(stack) and stack[-1][3]

        # A directive option line (``:name: value``) that lives inside a
        # directive is allowed at the same indent as the body.
        is_option = bool(stack) and FIELD_RE.match(stripped)
        # A line deeper than the last option is a multi-line option value.
        is_option_value = (
            last_option_indent is not None
            and indent > last_option_indent
            and not is_option
            and not _block_kind(stripped)
        )

        if is_option:
            last_option_indent = indent
            # ``:skip-indent:`` disables indentation checking for the
            # whole directive block it belongs to.
            if SKIP_INDENT_OPTION_RE.match(stripped):
                stack[-1][3] = True
        elif not is_option_value:
            last_option_indent = None

        # Lines inside a skip-indent block are wholly exempt.
        if skip_indent:
            continue
        # Lines that are purely code or option values are exempt.
        if in_code and code_body_indent is not None and indent >= code_body_indent:
            continue
        if is_option or is_option_value:
            continue

        if stack:
            parent_indent, expected, _, _ = stack[-1]
            delta = indent - parent_indent
            if delta != expected:
                hits.append(
                    (
                        i,
                        f"indent +{delta} (expected +{expected}, "
                        f"got {indent} want {parent_indent + expected})",
                    )
                )
            if in_code:
                # First body line of a code block: record its indent so
                # deeper code lines are exempt (code has its own
                # indentation).  Record even if the first line itself is
                # wrong, to avoid cascading violations on every code
                # line.
                code_body_indent = indent

        # Open a new block if this line starts one.  Option lines and
        # their continuations never open a block.
        if is_option or is_option_value:
            continue
        if DIRECTIVE_RE.match(stripped):
            name = _directive_name(stripped)
            if name in CODE_DIRECTIVES:
                expected, is_code = CODE_DELTA, True
            elif name in MANIM_LIKE_DIRECTIVES:
                expected, is_code = NORMAL_DELTA, True
            else:
                expected, is_code = NORMAL_DELTA, False
            stack.append([indent, expected, is_code, pending_skip])
            code_body_indent = None
            pending_skip = False
        elif LITERAL_BLOCK_RE.search(stripped):
            stack.append([indent, CODE_DELTA, True, pending_skip])
            code_body_indent = None
            pending_skip = False
        elif BULLET_RE.match(stripped) or ENUM_RE.match(stripped):
            # List-item continuation must align with the text after the
            # marker (``* item`` -> text at +2, ``1. item`` -> +3).
            m = BULLET_RE.match(stripped) or ENUM_RE.match(stripped)
            marker_width = len(m.group(0))
            stack.append([indent, marker_width, False, pending_skip])
            pending_skip = False
        elif stack and not in_code:
            # A bare line that is more indented than the current block
            # opening but is not a known block start is treated as a
            # definition-list term (numpydoc ``name : type``).  Its
            # description uses the numpydoc convention of +4.
            parent_indent = stack[-1][0]
            if indent > parent_indent:
                stack.append([indent, CODE_DELTA, False, pending_skip])
                pending_skip = False

    return hits


def _docutils_settings():
    """Build docutils settings that never halt and report every level.

    The reporter's stream is pointed at a throwaway buffer so docutils
    does not echo every system message to stderr (we read the messages
    back from the parsed document tree instead).
    """
    parser = docutils.parsers.rst.Parser()
    settings = docutils.frontend.get_default_settings(parser)
    settings.halt_level = 5
    settings.report_level = 1
    settings.warning_stream = io.StringIO()
    return settings


def check_docutils(text: str) -> list[tuple[int, str]]:
    """Parse *text* with docutils and return real (non-Sphinx) issues.

    Parameters
    ----------
    text : str
        The RST source to parse.

    Returns
    -------
    list of (int, str)
        ``(1-based line, message)`` for each docutils warning/error that
        is not caused by Sphinx extensions or standalone ``include``
        resolution.
    """
    parser = docutils.parsers.rst.Parser()
    doc = docutils.utils.new_document("<rst>", _docutils_settings())
    try:
        parser.parse(text, doc)
    except Exception as exc:  # pragma: no cover - defensive
        return [(1, f"docutils crashed: {exc}")]

    issues: list[tuple[int, str]] = []
    for msg in doc.findall(docutils.nodes.system_message):
        if msg["level"] < 2:  # INFO is too noisy
            continue
        text_ = msg.astext()
        if any(phrase in text_ for phrase in SKIP_PHRASES):
            continue
        # ``:skip-indent:`` is a validator-only option; docutils flags
        # it as an unknown option, but Sphinx ignores unknown options.
        if "skip-indent" in text_:
            continue
        first_line = text_.splitlines()[0]
        issues.append((int(msg["line"]), first_line[:160]))
    return issues


# ---------------------------------------------------------------------------
# Source collection
# ---------------------------------------------------------------------------
def iter_rst_files() -> list[Path]:
    """Return every ``.rst`` file under ``docs/source``."""
    return sorted(p for p in DOCS.rglob("*.rst") if not SKIP_DIR_PARTS & set(p.parts))


def extract_docstrings(source: str) -> list[tuple[int, list[tuple[int, str]]]]:
    """Extract docstrings from *source* with original line numbers.

    Parameters
    ----------
    source : str
        Python source code.

    Returns
    -------
    list of (start_line, lines)
        For each docstring, its 1-based start line and a list of
        ``(source_line_no, dedented_text)`` pairs spanning the docstring
        body (quote characters removed).
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    src_lines = source.splitlines()
    results: list[tuple[int, list[tuple[int, str]]]] = []

    for node in ast.walk(tree):
        if not isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        if not (node.body and isinstance(node.body[0], ast.Expr)):
            continue
        val = node.body[0].value
        if not isinstance(val, ast.Constant):
            continue
        doc_value = getattr(val, "value", None)
        if not isinstance(doc_value, str):
            continue

        start = val.lineno
        end = val.end_lineno
        raw = list(src_lines[start - 1 : end])

        # Strip the opening quote prefix from the first line.
        if raw:
            m = QUOTE_PREFIX_RE.match(raw[0])
            if m:
                raw[0] = raw[0][m.end():]
            else:
                raw[0] = ""
        # Strip the closing quote suffix from the last line.
        if len(raw) > 1:
            m = QUOTE_SUFFIX_RE.search(raw[-1])
            if m:
                raw[-1] = raw[-1][: m.start()]
            else:
                raw[-1] = ""
        elif raw:
            # Single-line docstring: strip both quotes from one line.
            m = QUOTE_SUFFIX_RE.search(raw[0])
            if m:
                raw[0] = raw[0][: m.start()]

        dedented = textwrap.dedent("\n".join(raw))
        ded_lines = dedented.split("\n")
        pairs = [(start + i, ded_lines[i]) for i in range(len(ded_lines))]
        results.append((start, pairs))

    return results


def iter_py_files() -> list[Path]:
    """Return every ``.py`` file under ``manim_extensions`` (vendored assets skipped)."""
    out = []
    for p in SRC.rglob("*.py"):
        if SKIP_DIR_PARTS & set(p.parts):
            continue
        if p.name == "__init__.py":
            continue
        out.append(p)
    return sorted(out)


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------
def check_rst_file(path: Path) -> list[tuple[str, int, str]]:
    """Run both checks on a single ``.rst`` file."""
    text = path.read_text(encoding="utf-8")
    rel = str(path.relative_to(ROOT))
    issues: list[tuple[str, int, str]] = []

    lines = text.split("\n")
    for idx, msg in check_abutting(lines):
        issues.append((rel, idx + 1, msg))
    for idx, msg in check_indentation(lines):
        issues.append((rel, idx + 1, f"indentation: {msg}"))
    for line_no, msg in check_docutils(text):
        issues.append((rel, line_no, f"docutils: {msg}"))
    return issues


def check_py_file(path: Path) -> list[tuple[str, int, str]]:
    """Run both checks on every docstring in a Python file."""
    source = path.read_text(encoding="utf-8")
    rel = str(path.relative_to(ROOT))
    issues: list[tuple[str, int, str]] = []

    for _start, pairs in extract_docstrings(source):
        line_map = [ln for ln, _ in pairs]
        texts = [t for _, t in pairs]
        for idx, msg in check_abutting(texts):
            issues.append((rel, line_map[idx], msg))
        for idx, msg in check_indentation(texts):
            issues.append((rel, line_map[idx], f"indentation: {msg}"))
        joined = "\n".join(texts)
        for offset, msg in check_docutils(joined):
            # docutils line numbers are 1-based offsets into the docstring.
            src_line = line_map[offset - 1] if 1 <= offset <= len(line_map) else line_map[0]
            issues.append((rel, src_line, f"docutils: {msg}"))
    return issues


def main() -> int:
    """Run the RST validation and report violations."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--only",
        type=str,
        default=None,
        help="Restrict the scan to a single file path (relative to repo root).",
    )
    args = parser.parse_args()

    issues: list[tuple[str, int, str]] = []

    if args.only:
        target = (ROOT / args.only).resolve()
        if not target.exists():
            print(f"ERROR: {args.only} does not exist")
            return 1
        if target.suffix == ".rst":
            issues.extend(check_rst_file(target))
        elif target.suffix == ".py":
            issues.extend(check_py_file(target))
        else:
            print(f"ERROR: unsupported file type: {target.suffix}")
            return 1
    else:
        for rst in iter_rst_files():
            issues.extend(check_rst_file(rst))
        for py in iter_py_files():
            issues.extend(check_py_file(py))

    # De-duplicate (a line can be flagged by both checks).
    seen: set[tuple[str, int, str]] = set()
    unique: list[tuple[str, int, str]] = []
    for issue in issues:
        if issue not in seen:
            seen.add(issue)
            unique.append(issue)

    if not unique:
        print("OK: no RST formatting issues found")
        return 0

    unique.sort(key=lambda x: (x[0], x[1]))
    print(f"FAIL: {len(unique)} RST formatting issue(s):\n")
    for rel, line_no, msg in unique:
        print(f"  {rel}:{line_no}  {msg}")
    print(f"\nTotal: {len(unique)} issue(s)")
    return 1


if __name__ == "__main__":
    sys.exit(main())

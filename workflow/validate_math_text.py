# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Find mathematical notation that is still plain text or inline code.

The documentation mixes prose, RST roles, code blocks, and Python docstrings.
A formula such as ``x^2`` or ``P = MV/Y`` is easy to leave behind in ordinary
text, especially when it was originally written as ````x^2```` for a code
example.  This checker reports those cases so they can be rendered as
``:math:`` instead.

The rules are deliberately conservative.  Braces, brackets, and parentheses
are *not* enough on their own: ``{}``, ``[]``, and ``()`` are common Python,
JSON, TikZ, and CLI syntax.  Only braces attached to an exponent or subscript
(``x^{2}``, ``P_{i+1}``), or braces used inside a recognised LaTeX command
(``\\frac{...}{...}``), are treated as mathematics.

Contexts skipped by the checker:

* ``.. code-block::``, ``.. sourcecode::``, ``.. code::``, ``.. manim::``,
  ``.. nbcell::``, ``.. math::``, ``.. raw::`` and similar directive bodies;
* literal blocks introduced by a trailing ``::``;
* fenced code blocks and doctest examples in docstrings;
* inline code that is a Python identifier, dotted name, CLI flag, command,
  path, URL, configuration assignment, version constraint, or package specifier.

Usage::

    python workflow/validate_math_text.py
    python workflow/validate_math_text.py --only docs/source/reference/economics/index.rst
    python workflow/validate_math_text.py --audit

Exit code 0 means no high-confidence violations; exit code 1 means at least
one was found.  ``--audit`` also prints ambiguous candidates, but those do
not affect the exit status.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path

from _context import DOCS, ROOT, SRC

SKIP_DIR_PARTS = {"__pycache__", ".git", "_build", "_static"}

# Directive bodies that are code, generated API pages, or already mathematics.
SKIP_BODY_DIRECTIVES = frozenset(
    {
        "autoclass",
        "autofunction",
        "automodule",
        "autosummary",
        "code",
        "code-block",
        "currentmodule",
        "image",
        "literalinclude",
        "manim",
        "math",
        "math-block",
        "module",
        "nbcell",
        "raw",
        "sourcecode",
        "toctree",
    }
)

INLINE_CODE_RE = re.compile(r"``([^`\n]+)``")
MATH_ROLE_RE = re.compile(r":math:`[^`]*`")
ROLE_RE = re.compile(r":[\w:]+:`[^`]*`")
LINK_RE = re.compile(r"`[^`<>]*<[^<>]+>`_?")
URL_RE = re.compile(r"https?://\S+")
DIRECTIVE_RE = re.compile(r"^(\s*)\.\.\s+([\w:-]+)::")
FENCE_RE = re.compile(r"^\s*```")
USAGE_HEADING_RE = re.compile(r"^(?:Usage|Example|Examples):$")

LATEX_COMMAND_RE = re.compile(
    r"\\(?:frac|sqrt|sum|prod|int|lim|partial|nabla|cdot|times|div|"
    r"le|leq|ge|geq|neq|approx|infty|alpha|beta|gamma|delta|theta|"
    r"lambda|mu|sigma|phi|omega|pi|Omega|Delta|pm|mp|left|right|"
    r"text|mathrm|mathbf|bar|hat|vec|exp|log|sin|cos|tan|to)\b"
)
POWER_RE = re.compile(r"(?<![\w\\])[A-Za-z0-9)}\]]\s*\^\s*(?:\{|\d|[A-Za-z(+-])")
SUBSCRIPT_RE = re.compile(r"(?<![\w])[A-Za-z]\s*_\s*(?:\{|\d)")
SUBSCRIPT_WORD_RE = re.compile(r"\b[A-Z]_[A-Za-z][A-Za-z0-9_]*\b")
SUPERSCRIPTS_RE = re.compile(r"[⁰¹²³⁴⁵⁶⁷⁸⁹ᵉᵢᵣᵤᵥᵦᵧᵨᵩᵪ]")
MATH_SYMBOLS_RE = re.compile(r"[≤≥≠≈∞√∑∏∫∂∆Δπθλμσφω±×÷·−]")
EQUATION_RE = re.compile(r"(?<![\w.])([A-Za-z][A-Za-z0-9_^{}]*)\s*=\s*([^=,;]+)")
COMPARISON_RE = re.compile(
    r"(?<![\w.])([A-Za-z][A-Za-z0-9_^{}]*)\s*(<=|>=|!=|≤|≥|≠)\s*([A-Za-z0-9.^{}]+)"
)
FUNCTION_RE = re.compile(
    r"\b(?:f|g|h|D|S|O|sin|cos|tan|log|ln|exp|sqrt|abs|min|max)"
    r"\([A-Za-z0-9_+\-*/^ ]+\)"
)
MULTIPLICATION_RE = re.compile(r"[A-Za-z0-9)}\]]\s*(?:\*|×|÷|·)\s*[A-Za-z0-9({[]")
VERSION_RE = re.compile(
    r"\b(?:Python|manim|pymunk|Pillow|opencv-python|shapely|kociemba|"
    r"trimesh|scipy|moderngl|numpy|typing_extensions)\b\s*(?:>=|<=|==|~=|<|>)"
)

# Literal spellings that are themselves code examples, not mathematics.
CODE_LITERALS = frozenset(
    {
        "{}",
        "[]",
        "()",
        r"\text{}",
        r"\d",
        r"\n",
        r"\usepackage",
        r"\usetikzlibrary",
        r"\tikzset",
    }
)


@dataclass
class Hit:
    """One candidate reported by the checker."""

    path: Path
    line: int
    kind: str
    text: str
    reasons: tuple[str, ...]
    source: str


def _rel(path: Path) -> str:
    """Return a repository-relative path with POSIX separators."""
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _version_constraint(text: str) -> bool:
    """Return whether ``text`` looks like a dependency version constraint."""
    return bool(VERSION_RE.search(text))


def _looks_like_code(text: str) -> bool:
    """Return whether an inline literal is ordinary code rather than math."""
    stripped = text.strip()
    if not stripped or stripped in CODE_LITERALS:
        return True
    if stripped.startswith(("--", "-", "/", "./", "~/")) and "=" in stripped:
        return True
    if any(token in stripped for token in ("://", "::", "->", "=>", "__")):
        return True
    if any(ch in stripped for ch in ('"', "'", "`")):
        return True
    if stripped.startswith(
        (
            "pip ",
            "python ",
            "pytest ",
            "manim ",
            "black ",
            "flake8 ",
            "git ",
            "gh ",
            "coverage ",
        )
    ):
        return True
    if re.fullmatch(r"[A-Za-z_][\w.]*(?:\([^)]*\))?", stripped):
        # A plain identifier or call such as ``table_name`` / ``foo()``.
        return True
    if re.match(r"^[A-Za-z_][\w.]*\(", stripped) and "=" in stripped:
        # A call with keyword arguments, e.g. ``mobject.set(foo=True)``.
        return True
    assignment = re.match(r"([A-Za-z_]\w*)\s*=\s*(.*)", stripped)
    if assignment:
        lhs, rhs = assignment.group(1), assignment.group(2)
        if len(lhs) > 1 and lhs[0].islower():
            if rhs in {"True", "False", "None"}:
                return True
            if re.fullmatch(r"\d+(?:\.\d+)?", rhs):
                return True
            if rhs.startswith(("[", "<", '"', "'")):
                return True
            if re.fullmatch(r"[A-Za-z_]\w*", rhs) and not re.search(
                r"[+\-*/^]", stripped
            ):
                return True
    if re.fullmatch(
        r"[A-Za-z0-9_.-]+(?:\s*(?:>=|<=|==|~=|<|>)\s*(?:\d[\w.,*]*|\*))+",
        stripped,
    ):
        return True
    return False


def _equation_is_math(lhs: str, rhs: str) -> bool:
    """Return whether an assignment-like fragment is a formula."""
    if lhs.lower() in {
        "python",
        "manim",
        "pymunk",
        "pillow",
        "opencv-python",
        "shapely",
        "kociemba",
        "trimesh",
        "scipy",
        "moderngl",
        "numpy",
    }:
        return False
    if re.fullmatch(r"\d+(?:\.\d+)*", rhs.strip()):
        return len(lhs) <= 2 or bool(re.search(r"[_^]", lhs))

    if re.search(r"[+\-*/^·×÷−]", rhs):
        return True
    if re.search(r"\b(?:f|g|h|D|S|O|sin|cos|tan|log|ln|exp|sqrt)\(", rhs):
        return True
    if len(lhs) <= 2 or bool(re.search(r"[_^]", lhs)):
        return True
    return False


def _math_reasons(text: str, *, inline: bool) -> list[str]:
    """Return short reasons why ``text`` looks like unsupported mathematics."""
    stripped = text.strip()
    if not stripped or stripped in CODE_LITERALS:
        return []
    if stripped.startswith(r"\text{}") or stripped.startswith(r"\text{"):
        return []
    if _version_constraint(stripped):
        return []
    if re.fullmatch(r"[A-Za-z_][\w.-]*", stripped):
        # A lone identifier such as ``curve_points_1`` is code, not math.
        return []

    reasons: list[str] = []
    if LATEX_COMMAND_RE.search(stripped):
        reasons.append("LaTeX command")
    if POWER_RE.search(stripped):
        reasons.append("exponent")
    if SUBSCRIPT_RE.search(stripped):
        reasons.append("subscript")
    elif SUBSCRIPT_WORD_RE.search(stripped) and ("=" in stripped or inline):
        reasons.append("subscript word")
    if SUPERSCRIPTS_RE.search(stripped):
        reasons.append("unicode superscript")
    if MATH_SYMBOLS_RE.search(stripped):
        reasons.append("math symbol")
    if FUNCTION_RE.search(stripped):
        reasons.append("function notation")
    if MULTIPLICATION_RE.search(stripped) and not _looks_like_code(stripped):
        reasons.append("arithmetic")

    for match in EQUATION_RE.finditer(stripped):
        lhs, rhs = match.group(1), match.group(2)
        if _equation_is_math(lhs, rhs):
            reasons.append("equation")
            break

    for match in COMPARISON_RE.finditer(stripped):
        lhs, rhs = match.group(1), match.group(2)
        if lhs.lower() in {"d", "x", "y", "z", "feature", "a", "b", "c"}:
            reasons.append("comparison")
            break
        if len(lhs) <= 2 or re.search(r"[_^{}]", lhs):
            reasons.append("comparison")
            break
        if lhs.isidentifier() and rhs.isidentifier():
            # Ordinary variable comparison such as ``feature <= threshold``;
            # dependency versions are handled before this point.
            reasons.append("comparison")
            break

    if not reasons:
        return []
    if inline and _looks_like_code(stripped):
        # Keep mathematical function notation such as ``f(k)`` and ``D(Q)``.
        if not re.fullmatch(r"(?:f|g|h|D|S|O)\([^)]+\)", stripped):
            return []
    return reasons


def _strip_prose(line: str) -> str:
    """Remove inline markup whose contents are checked separately or code."""
    text = MATH_ROLE_RE.sub(" ", line)
    text = INLINE_CODE_RE.sub(" ", text)
    text = ROLE_RE.sub(" ", text)
    text = LINK_RE.sub(" ", text)
    text = URL_RE.sub(" ", text)
    text = text.replace("**", "").replace("*", "")
    return text


def _load_exemptions() -> list[dict[str, str]]:
    """Load the optional exemption table next to the checker."""
    path = ROOT / "workflow" / "math_text_exemptions.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("exemptions", [])


def _is_exempt(
    path: Path, text: str, kind: str, exemptions: list[dict[str, str]]
) -> bool:
    """Return whether a candidate is documented as intentional."""
    relative = _rel(path)
    for entry in exemptions:
        if entry.get("path") != relative:
            continue
        if entry.get("text") != text:
            continue
        if entry.get("kind", kind) != kind:
            continue
        return True
    return False


def _scan_lines(
    path: Path,
    lines: list[str],
    line_numbers: list[int],
    exemptions: list[dict[str, str]],
    *,
    audit: bool,
) -> list[Hit]:
    """Scan one RST document or docstring body."""
    hits: list[Hit] = []
    skip_indent: int | None = None
    literal_indent: int | None = None
    in_fence = False

    for index, line in enumerate(lines):
        line_no = line_numbers[index]
        indent = len(line) - len(line.lstrip())
        stripped = line.strip()

        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence or not stripped:
            continue

        if skip_indent is not None:
            if indent <= skip_indent:
                skip_indent = None
            else:
                continue
        if literal_indent is not None:
            if indent <= literal_indent:
                literal_indent = None
            else:
                continue

        directive = DIRECTIVE_RE.match(line)
        if directive:
            name = directive.group(2).lower()
            if name in SKIP_BODY_DIRECTIVES:
                skip_indent = indent
            continue

        if USAGE_HEADING_RE.match(stripped):
            # A plain code example after ``Usage:`` / ``Examples:``.
            literal_indent = indent
            continue

        if stripped.startswith((".. ", ">>>", "...")):
            continue

        if stripped.endswith("::"):
            # Scan the prose before the literal block, then skip its body.
            prefix = stripped[:-2].strip()
            if prefix:
                _append_hit(
                    path,
                    line_no,
                    "prose",
                    prefix,
                    line,
                    exemptions,
                    audit,
                    hits,
                )
            literal_indent = indent
            continue

        for inline_match in INLINE_CODE_RE.finditer(line):
            literal = inline_match.group(1).strip()
            reasons = _math_reasons(literal, inline=True)
            if reasons and not _is_exempt(path, literal, "inline", exemptions):
                hits.append(
                    Hit(
                        path,
                        line_no,
                        "inline",
                        literal,
                        tuple(reasons),
                        line.strip(),
                    )
                )

        prose = _strip_prose(line).strip()
        if prose:
            _append_hit(
                path,
                line_no,
                "prose",
                prose,
                line,
                exemptions,
                audit,
                hits,
            )

    return hits


def _append_hit(
    path: Path,
    line_no: int,
    kind: str,
    text: str,
    source: str,
    exemptions: list[dict[str, str]],
    audit: bool,
    hits: list[Hit],
) -> None:
    """Append a high-confidence or audit-only candidate."""
    reasons = _math_reasons(text, inline=False)
    if not reasons:
        if audit:
            weak = _weak_math_reason(text)
            if weak:
                hits.append(Hit(path, line_no, kind, text, (weak,), source.strip()))
        return
    if _is_exempt(path, text.strip(), kind, exemptions):
        return
    hits.append(Hit(path, line_no, kind, text, tuple(reasons), source.strip()))


def _weak_math_reason(text: str) -> str | None:
    """Return a reason for an ambiguous candidate, or ``None``."""
    stripped = text.strip()
    if re.search(r"[{}[\]()]", stripped) and re.search(r"[A-Za-z0-9]", stripped):
        if re.search(r"[=^_+\-*/]", stripped):
            return "ambiguous brackets/operators"
    return None


def _extract_docstrings(source: str) -> list[tuple[int, list[str]]]:
    """Extract docstrings with source line numbers."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    lines = source.splitlines()
    output: list[tuple[int, list[str]]] = []
    for node in ast.walk(tree):
        if not isinstance(
            node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
        ):
            continue
        if not (node.body and isinstance(node.body[0], ast.Expr)):
            continue
        value = node.body[0].value
        if not isinstance(value, ast.Constant) or not isinstance(value.value, str):
            continue

        start = value.lineno
        raw = lines[start - 1 : value.end_lineno]
        if raw:
            raw[0] = re.sub(r'^\s*[rRuUbBfF]*"""', "", raw[0])
            raw[0] = re.sub(r"^\s*[rRuUbBfF]*'''", "", raw[0])
        if len(raw) > 1:
            raw[-1] = re.sub(r'\s*"""$', "", raw[-1])
            raw[-1] = re.sub(r"\s*'''$", "", raw[-1])
        elif raw:
            raw[0] = re.sub(r'\s*"""$', "", raw[0])
            raw[0] = re.sub(r"\s*'''$", "", raw[0])

        body = textwrap.dedent("\n".join(raw)).split("\n")
        output.append((start, body))
    return output


def _iter_rst_files() -> list[Path]:
    """Return every RST source file that is not a build asset."""
    return sorted(
        path
        for path in DOCS.rglob("*.rst")
        if not SKIP_DIR_PARTS.intersection(path.parts)
    )


def _iter_py_files() -> list[Path]:
    """Return every package Python file, including vendored subpackages."""
    return sorted(
        path
        for path in SRC.rglob("*.py")
        if not SKIP_DIR_PARTS.intersection(path.parts)
    )


def _collect(only: str | None, audit: bool) -> list[Hit]:
    """Collect candidates from RST files and Python docstrings."""
    exemptions = _load_exemptions()
    hits: list[Hit] = []
    only_path = (ROOT / only).resolve() if only else None

    for path in _iter_rst_files():
        if only_path and path.resolve() != only_path:
            continue
        text = path.read_text(encoding="utf-8")
        hits.extend(
            _scan_lines(
                path,
                text.split("\n"),
                list(range(1, len(text.split("\n")) + 1)),
                exemptions,
                audit=audit,
            )
        )

    for path in _iter_py_files():
        if only_path and path.resolve() != only_path:
            continue
        source = path.read_text(encoding="utf-8")
        for start, body in _extract_docstrings(source):
            line_numbers = list(range(start, start + len(body)))
            hits.extend(
                _scan_lines(
                    path,
                    body,
                    line_numbers,
                    exemptions,
                    audit=audit,
                )
            )
    return hits


def _print_hits(hits: list[Hit], *, audit: bool) -> None:
    """Print candidates grouped by file."""
    for hit in hits:
        reasons = ", ".join(hit.reasons)
        print(f"{_rel(hit.path)}:{hit.line}: [{hit.kind}] {hit.text!r} ({reasons})")
        if audit:
            print(f"    {hit.source[:160]}")


def main() -> int:
    """Run the math-text validation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--only",
        help="restrict the scan to one file path, relative to the repository root",
    )
    parser.add_argument(
        "--audit",
        action="store_true",
        help="also print ambiguous bracket/operator candidates",
    )
    args = parser.parse_args()

    hits = _collect(args.only, args.audit)
    high_confidence = [
        hit
        for hit in hits
        if hit.kind in {"inline", "prose"}
        and hit.reasons != ("ambiguous brackets/operators",)
    ]

    # Auditing also prints ambiguous entries; keep the exit status tied to
    # high-confidence text only so CI is not blocked by intentional code.
    ambiguous = [
        hit for hit in hits if hit.reasons == ("ambiguous brackets/operators",)
    ]
    if high_confidence:
        print(f"FAIL validate-math-text: {len(high_confidence)} candidate(s)")
        _print_hits(high_confidence, audit=args.audit)
        if ambiguous:
            print(f"\n{len(ambiguous)} ambiguous candidate(s) (not failing):")
            _print_hits(ambiguous, audit=args.audit)
        return 1
    if ambiguous and args.audit:
        print(f"{len(ambiguous)} ambiguous candidate(s) (not failing):")
        _print_hits(ambiguous, audit=args.audit)
    print("PASS validate-math-text: no unwrapped math candidates")
    return 0


if __name__ == "__main__":
    sys.exit(main())

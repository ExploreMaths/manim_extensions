# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Reject CJK characters in all text files across the repository.

The project's source, comments and documentation are English.  This check
walks every text file, not just the installed package, and reports any CJK
character in prose, comments, docstrings or ordinary string content.  The
comment readers understand Python, RST, Markdown, TOML, YAML, shell, TeX,
CSS, JavaScript and SVG syntax; a final line pass catches everything else.
A small allowlist covers files whose purpose is Chinese sample data, such as
the ``ChineseMathTex`` examples, Chinese caption tests and the legacy radar
preset.

A violation reports the file, line, kind and the first offending character.

Usage:
    python workflow/validate_english_text.py
"""

from __future__ import annotations

import ast
import io
import re
import sys
import tokenize
from pathlib import Path

from _context import ROOT

CJK_RE = re.compile(
    "[\u2e80-\u2eff\u3000-\u303f\u3040-\u30ff\u3100-\u312f"
    "\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff00-\uffef]"
)

SKIP_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "_build",
    "build",
    "dist",
    "htmlcov",
    "media",
    "node_modules",
    "__test_media_dir__",
}
SKIP_PREFIXES = ("docs/build_check",)
ALLOW_CHINESE_FILES = {
    # ChineseMathTex examples intentionally contain Chinese TeX payloads.
    "docs/source/examples/index.rst",
    "tests/test_mobjects_chinese_mathtex.py",
    # These tests assert that Chinese captions still render correctly.
    "tests/test_three_d_full.py",
    # The legacy radar preset ships Chinese axis labels as its data.
    "manim_extensions/radar/legacy.py",
    # Copyright holder name in the REUSE metadata.
    "REUSE.toml",
}

PYTHON_SUFFIXES = {".py", ".pyi"}
TEXT_SUFFIXES = {
    ".bash",
    ".cff",
    ".cfg",
    ".css",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".md",
    ".mjs",
    ".rst",
    ".sh",
    ".svg",
    ".tex",
    ".toml",
    ".ts",
    ".txt",
    ".yml",
    ".yaml",
    ".zsh",
}
MARKER_SUFFIXES = {
    ".bash": ("#",),
    ".cfg": ("#",),
    ".cff": ("#",),
    ".ini": ("#", ";"),
    ".json": ("#",),
    ".sh": ("#",),
    ".tex": ("%",),
    ".toml": ("#",),
    ".txt": ("#",),
    ".yml": ("#",),
    ".yaml": ("#",),
    ".zsh": ("#",),
}
BLOCK_SUFFIXES = {
    ".css": {"//", "/*", "*"},
    ".js": {"//", "/*", "*"},
    ".mjs": {"//", "/*", "*"},
    ".ts": {"//", "/*", "*"},
}


def _iter_python(tree: ast.AST, path: Path, text: str):
    """Yield violations from Python comments and docstrings."""
    try:
        tokens = tokenize.generate_tokens(io.StringIO(text).readline)
    except tokenize.TokenError:
        tokens = []
    for token in tokens:
        if token.type == tokenize.COMMENT:
            match = CJK_RE.search(token.string)
            if match:
                yield token.start[0], "comment", token.string.strip(), match.group(0)

    for node in ast.walk(tree):
        if not isinstance(
            node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
        ):
            continue
        doc = ast.get_docstring(node, clean=False)
        if not doc:
            continue
        match = CJK_RE.search(doc)
        if match is None:
            continue
        start = node.body[0].lineno if node.body else getattr(node, "lineno", 1)
        line = start + doc[: match.start()].count("\n")
        name = "<module>" if isinstance(node, ast.Module) else node.name
        yield line, "docstring", f"{name}: {doc.strip().splitlines()[0]}", match.group(
            0
        )


def _iter_rst_comments(text: str):
    for lineno, line in enumerate(text.splitlines(), 1):
        stripped = line.lstrip()
        if not stripped.startswith(".."):
            continue
        match = CJK_RE.search(stripped)
        if match:
            yield lineno, "comment", stripped, match.group(0)


def _iter_block_comments(path: Path, text: str):
    """Yield comment text from block-comment files (CSS/JS and Markdown)."""
    in_comment = False
    for lineno, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if path.suffix == ".md":
            if "<!--" in line:
                in_comment = True
            match = CJK_RE.search(line)
            if in_comment and match:
                yield lineno, "comment", stripped, match.group(0)
            if "-->" in line:
                in_comment = False
            continue

        if in_comment:
            match = CJK_RE.search(line)
            if match:
                yield lineno, "comment", stripped, match.group(0)
            if "*/" in line:
                in_comment = False
            continue
        if "/*" in line:
            in_comment = True
            match = CJK_RE.search(line.split("/*", 1)[1])
            if match:
                yield lineno, "comment", stripped, match.group(0)
            if "*/" in line:
                in_comment = False
            continue
        for marker in BLOCK_SUFFIXES[path.suffix]:
            if marker == "*":
                continue
            if marker in line:
                match = CJK_RE.search(line.split(marker, 1)[1])
                if match:
                    yield lineno, "comment", stripped, match.group(0)
                break


def _iter_marker_comments(path: Path, text: str):
    markers = MARKER_SUFFIXES[path.suffix]
    for lineno, line in enumerate(text.splitlines(), 1):
        for marker in markers:
            if marker in line:
                match = CJK_RE.search(line.split(marker, 1)[1])
                if match:
                    yield lineno, "comment", line.strip(), match.group(0)
                break


def _is_skipped(path: Path):
    rel = path.relative_to(ROOT)
    if any(part in SKIP_DIRS for part in rel.parts):
        return True
    return any(str(rel).startswith(prefix) for prefix in SKIP_PREFIXES)


def main() -> int:
    """Scan every text file and report any CJK text."""
    violations = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or _is_skipped(path):
            continue
        if path.suffix not in TEXT_SUFFIXES and path.suffix not in PYTHON_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        rel = path.relative_to(ROOT)
        if str(rel) in ALLOW_CHINESE_FILES:
            continue

        findings = []
        if path.suffix in PYTHON_SUFFIXES:
            try:
                tree = ast.parse(text)
            except SyntaxError as exc:
                violations.append((path, 0, "syntax", f"syntax error: {exc}", ""))
                continue
            findings = list(_iter_python(tree, path, text))
        elif path.suffix == ".rst":
            findings = list(_iter_rst_comments(text))
        elif path.suffix in BLOCK_SUFFIXES:
            findings = list(_iter_block_comments(path, text))
        elif path.suffix in MARKER_SUFFIXES:
            findings = list(_iter_marker_comments(path, text))

        # Scan prose and string content as well.  The readers above understand
        # comment syntax; this pass catches Chinese in documentation bodies,
        # log messages, UI strings and other non-comment lines.  Files whose
        # whole purpose is Chinese sample data are in ALLOW_CHINESE_FILES.
        seen_lines = {line for line, _kind, _content, _char in findings}
        for lineno, line in enumerate(text.splitlines(), 1):
            match = CJK_RE.search(line)
            if match and lineno not in seen_lines:
                findings.append((lineno, "text", line.strip(), match.group(0)))

        for lineno, kind, excerpt, character in findings:
            violations.append((path, lineno, kind, excerpt, character))

    if not violations:
        print("PASS  english-text")
        return 0

    for path, lineno, kind, excerpt, character in violations:
        rel = path.relative_to(ROOT)
        print(
            f"{rel}:{lineno}: {kind}: non-English character {character!r} in {excerpt}"
        )
    print(f"\nFAIL  {len(violations)} CJK text violation(s)")
    return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Fix indentation of .. manim:: blocks in Python docstrings.

Rules:
- `.. manim:: ClassName` is at some base indentation (0, 4, 8, ...)
- `:save_last_frame:` (and other options) should be at base + 3 spaces
- First level of code (imports, class def) should be at base + 3 spaces
- Python indentation inside code is preserved relative to base + 3
"""

import os
import re
import sys


def find_manim_blocks(lines):
    """Find all .. manim:: block positions in the file.

    Returns list of (start_line_idx, end_line_idx, base_indent).
    """
    blocks = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r'^(\s*)\.\.\s+manim::\s+\w+\s*$', line)
        if m:
            base_indent = len(m.group(1))
            j = i + 1
            while j < len(lines):
                nxt = lines[j]
                stripped = nxt.strip()
                if stripped == '':
                    j += 1
                    continue
                indent = len(nxt) - len(nxt.lstrip())
                if indent <= base_indent:
                    break
                j += 1
            blocks.append((i, j, base_indent))
            i = j
        else:
            i += 1
    return blocks


def fix_manim_block(block_lines, base_indent):
    """Fix indentation within a single manim block.

    block_lines: list of strings, from the directive line through the last
                 code line (excluding the closing \""" or ''').
    base_indent:  indentation level of the .. manim:: directive.

    Returns fixed list of strings.
    """
    target = base_indent + 3

    dir_line = block_lines[0]

    options = []
    code_start = None
    for idx in range(1, len(block_lines)):
        bline = block_lines[idx]
        stripped = bline.strip()
        if stripped == '':
            code_start = idx + 1
            break
        if re.match(r'^:\w+:', stripped):
            options.append((idx, bline))
        else:
            code_start = idx
            break

    result = list(block_lines)

    for opt_idx, opt_line in options:
        content = opt_line.strip()
        result[opt_idx] = ' ' * target + content

    if code_start is not None and code_start < len(result):
        code_lines = []
        for idx in range(code_start, len(result)):
            code_lines.append((idx, result[idx]))

        min_indent = float('inf')
        for _, cline in code_lines:
            if cline.strip() == '':
                continue
            indent = len(cline) - len(cline.lstrip())
            if indent < min_indent:
                min_indent = indent

        if min_indent != float('inf') and min_indent != target:
            shift = target - min_indent
            for idx, cline in code_lines:
                if cline.strip() == '':
                    result[idx] = ''
                else:
                    old_indent = len(cline) - len(cline.lstrip())
                    new_indent = old_indent + shift
                    result[idx] = ' ' * new_indent + cline.lstrip()

    return result


def fix_file(filepath):
    """Fix all manim blocks in a Python file. Returns number of changes."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    blocks = find_manim_blocks(lines)

    if not blocks:
        return 0

    new_lines = []
    i = 0
    changes = 0

    for start, end, base_indent in blocks:
        new_lines.extend(lines[i:start])
        block_lines = lines[start:end]
        fixed = fix_manim_block(block_lines, base_indent)
        if fixed != block_lines:
            changes += 1
        new_lines.extend(fixed)
        i = end

    new_lines.extend(lines[i:])

    if changes > 0:
        new_content = '\n'.join(new_lines)
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            rel = os.path.relpath(filepath, start_dir)
            print(f"  Fixed {changes} block(s): {rel}")

    return changes


def main():
    total_files = 0
    total_changes = 0

    for root, dirs, files in os.walk(start_dir):
        dirs[:] = [d for d in dirs if d != '__pycache__']
        for fname in files:
            if fname.endswith('.py'):
                fpath = os.path.join(root, fname)
                if os.path.abspath(fpath) == os.path.abspath(__file__):
                    continue
                ch = fix_file(fpath)
                if ch > 0:
                    total_files += 1
                    total_changes += ch

    print(f"\nDone. Fixed {total_changes} manim block(s) in {total_files} file(s).")


if __name__ == '__main__':
    start_dir = os.path.dirname(os.path.abspath(__file__))
    main()
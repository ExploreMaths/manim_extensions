# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


"""Validate `:save_last_frame:` usage in manim directive blocks.

Rules:
    - Static scenes (no self.play / self.animate)  -> MUST have :save_last_frame:
    - Animated scenes (has self.play / self.animate) -> MUST NOT have :save_last_frame:
    - Static scenes with :save_last_frame: should NOT use self.wait() (redundant)
    - Static scenes without :save_last_frame: MUST have it added

Usage:
    python validate_manim_directives.py
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ANIMATION_PATTERNS = [
    re.compile(r'\bself\.play\s*\('),
    re.compile(r'\bself\.animate\s*\('),
    re.compile(r'\bself\.animate\.value_tracker\b'),
    re.compile(r'\.play\s*\(\s*self\s*\)'),
]

WAIT_PATTERN = re.compile(r'\bself\.wait\s*\(')

SKIP_FILES = {
    'manim_directive.py',
}


def has_animation(code: str) -> bool:
    for pat in ANIMATION_PATTERNS:
        if pat.search(code):
            return True
    return False


def has_wait(code: str) -> bool:
    return bool(WAIT_PATTERN.search(code))


def extract_manim_blocks(file_path: Path):
    text = file_path.read_text(encoding='utf-8')
    lines = text.splitlines()

    blocks = []
    i = 0
    while i < len(lines):
        line = lines[i]

        m = re.match(r'\s*\.\.\s+manim::\s+(\S+)', line)
        if m:
            class_name = m.group(1)
            has_save_last_frame = False
            j = i + 1
            while j < len(lines) and (re.match(r'\s*:[\w_]+:', lines[j]) or lines[j].strip() == ''):
                opt_match = re.match(r'\s*:(save_last_frame):', lines[j])
                if opt_match:
                    has_save_last_frame = True
                j += 1

            code_lines = []
            while j < len(lines):
                current = lines[j]
                if re.match(r'\s*\.\.\s+manim::', current):
                    break
                stripped = current.strip()
                if stripped == '"""' or stripped == "'''":
                    break
                if stripped == '':
                    if j + 1 < len(lines) and not re.match(r'\s{3,}', lines[j + 1]):
                        break
                    if j == len(lines) - 1:
                        break
                code_lines.append(lines[j])
                j += 1

            code = '\n'.join(code_lines)
            blocks.append({
                'class_name': class_name,
                'has_save_last_frame': has_save_last_frame,
                'code': code,
                'start_line': i + 1,
            })
            i = j
        else:
            i += 1

    return blocks


def check_file(file_path: Path):
    blocks = extract_manim_blocks(file_path)
    issues = []
    for block in blocks:
        animated = has_animation(block['code'])
        wait_used = has_wait(block['code'])

        if animated and block['has_save_last_frame']:
            issues.append({
                'type': 'ANIMATED_HAS_SAVE_LAST_FRAME',
                'line': block['start_line'],
                'class_name': block['class_name'],
                'message': "Has self.play/self.animate but also has :save_last_frame: (should REMOVE :save_last_frame:)",
                'code_preview': block['code'][:200],
            })
        elif not animated and not block['has_save_last_frame'] and wait_used:
            issues.append({
                'type': 'STATIC_WITH_WAIT_MISSING_SAVE',
                'line': block['start_line'],
                'class_name': block['class_name'],
                'message': "Is static (no self.play/self.animate), uses self.wait(), but missing :save_last_frame: (should ADD :save_last_frame: and REMOVE self.wait())",
                'code_preview': block['code'][:200],
            })
        elif not animated and not block['has_save_last_frame']:
            issues.append({
                'type': 'STATIC_MISSING_SAVE_LAST_FRAME',
                'line': block['start_line'],
                'class_name': block['class_name'],
                'message': "Is static (no self.play/self.animate) but missing :save_last_frame: (should ADD :save_last_frame:)",
                'code_preview': block['code'][:200],
            })
        elif not animated and block['has_save_last_frame'] and wait_used:
            issues.append({
                'type': 'STATIC_HAS_WAIT_REDUNDANT',
                'line': block['start_line'],
                'class_name': block['class_name'],
                'message': "Is static with :save_last_frame: but also uses self.wait() (self.wait() is redundant, REMOVE it)",
                'code_preview': block['code'][:200],
            })

    return issues


def main():
    targets = [
        ROOT / 'manim_extensions',
        ROOT / 'docs',
    ]

    py_files = []
    for target in targets:
        if target.exists():
            py_files.extend(target.rglob('*.py'))
            py_files.extend(target.rglob('*.rst'))

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

    print("=" * 70)
    print("MANIM DIRECTIVE VALIDATOR")
    print("=" * 70)
    print(f"\nFiles scanned:          {len(set(py_files)) - len(SKIP_FILES)}")
    print(f"Files with directives:  {len(files_with_blocks)}")
    print(f"Total .. manim:: blocks: {total_blocks}")

    if all_issues:
        total_issues = sum(len(v) for v in all_issues.values())
        print(f"\nISSUES FOUND: {total_issues}\n")
        print("-" * 70)
        for fp, issues in all_issues.items():
            print(f"\nFILE: {fp}")
            for issue in issues:
                if issue['type'] == 'ANIMATED_HAS_SAVE_LAST_FRAME':
                    icon = "ANIMATED + SAVE_LAST_FRAME (remove :save_last_frame:)"
                elif issue['type'] == 'STATIC_WITH_WAIT_MISSING_SAVE':
                    icon = "STATIC + self.wait() MISSING SAVE (add :save_last_frame:, remove self.wait())"
                elif issue['type'] == 'STATIC_MISSING_SAVE_LAST_FRAME':
                    icon = "STATIC MISSING SAVE_LAST_FRAME (add :save_last_frame:)"
                else:
                    icon = "STATIC HAS REDUNDANT self.wait() (remove self.wait())"
                print(f"  Line {issue['line']:4d} | {icon}")
                print(f"         Class: {issue['class_name']}")
                print(f"         {issue['message']}")
                print(f"         Code preview:")
                for line in issue['code_preview'].split('\n')[:8]:
                    print(f"           | {line}")
        print("\n" + "=" * 70)
        print(f"VALIDATION FAILED - {total_issues} issue(s) found")
        print("=" * 70)
        return 1
    else:
        print("\nAll directives are correct!")
        print("=" * 70)
        print("VALIDATION PASSED")
        print("=" * 70)
        return 0


if __name__ == '__main__':
    sys.exit(main())
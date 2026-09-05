# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


"""Validate that class constructor parameters are documented in the class docstring.

Rules:
    - Parameter documentation MUST be in the class docstring (not in __init__).
    - Every parameter in __init__ (except ``self``, ``*args``, and ``**kwargs``)
      MUST have a corresponding entry in the class docstring's ``Parameters`` section.
    - The __init__ docstring should only be a brief description, not full param docs.

Usage:
    python validate_param_docs.py [directory ...]

If no directory is given, scans ``manim_extensions/`` by default.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SKIP_FILES = {'__init__.py'}

# Vendored upstream subpackages keep their original docstring style.
SKIP_DIRS = {
    "arabic", "chemistry", "economics", "fontawesome", "machine_learning",
    "pymunk", "qr_codes", "svg_animations", "table", "weighted_line",
    "docbuild", "testing", "custom_mobjects",
}

SKIP_CLASSES = {'ABC'}

KNOWN_NO_PARAMS = {
    'ManimAnimations',
    'ManimTuringMachine',
    'PushDownAutomatonRule',
}


def _split_params(param_str: str):
    """Split a parameter string by commas, respecting nested brackets."""
    params = []
    depth = 0
    current = []
    for ch in param_str:
        if ch in ('[', '(', '{'):
            depth += 1
        elif ch in (']', ')', '}'):
            depth -= 1
        elif ch == ',' and depth == 0:
            params.append(''.join(current).strip())
            current = []
            continue
        current.append(ch)
    if current:
        params.append(''.join(current).strip())
    return [p for p in params if p]


def _extract_param_name(param: str):
    """Extract the parameter name from a raw parameter string like 'x: float = 5'."""
    p = param.strip()
    if not p:
        return None
    if p.startswith('**'):
        return '**kwargs'
    if p.startswith('*'):
        name_match = re.match(r'\*(\w+)', p)
        if name_match:
            return name_match.group(1)
        return '*args'
    name_match = re.match(r'([a-zA-Z_]\w*)', p)
    if name_match:
        return name_match.group(1)
    return None


def extract_class_init_blocks(file_path: Path):
    """Extract class_name, class_docstring, init_docstring, init_params for each class."""
    text = file_path.read_text(encoding='utf-8')
    lines = text.splitlines()

    results = []
    i = 0
    while i < len(lines):
        line = lines[i]

        class_match = re.match(r'^class\s+(\w+)', line)
        if not class_match:
            i += 1
            continue

        class_name = class_match.group(1)
        if class_name in SKIP_CLASSES:
            i += 1
            continue

        j = i + 1
        while j < len(lines) and (re.match(r'^\s*$', lines[j]) or re.match(r'^\s+#', lines[j])):
            j += 1

        class_docstring = None
        if j < len(lines) and (lines[j].strip().startswith('"""') or lines[j].strip().startswith("'''")):
            quote_char = '"""' if lines[j].strip().startswith('"""') else "'''"
            doc_lines = [lines[j]]
            if lines[j].strip().count(quote_char) < 2:
                j += 1
                while j < len(lines):
                    doc_lines.append(lines[j])
                    stripped = lines[j].strip()
                    if quote_char in stripped:
                        if stripped == quote_char:
                            break
                        if stripped.count(quote_char) >= 2:
                            break
                    j += 1
            else:
                j += 1
            class_docstring = '\n'.join(doc_lines)

        init_params = []
        init_docstring = ''
        k = j
        while k < len(lines):
            stripped = lines[k].strip()
            if re.match(r'^\s*def\s+__init__\s*\(', lines[k]):
                init_lines = [lines[k]]
                paren_depth = lines[k].count('(') - lines[k].count(')')
                k += 1
                while k < len(lines) and paren_depth > 0:
                    init_lines.append(lines[k])
                    paren_depth += lines[k].count('(') - lines[k].count(')')
                    k += 1
                init_def = '\n'.join(init_lines)

                sig_match = re.search(r'def\s+__init__\s*\(', init_def)
                if sig_match:
                    start = sig_match.end()
                    depth = 1
                    pos = start
                    while pos < len(init_def) and depth > 0:
                        ch = init_def[pos]
                        if ch == '(':
                            depth += 1
                        elif ch == ')':
                            depth -= 1
                        pos += 1
                    raw_params = init_def[start:pos - 1].strip()
                    if raw_params:
                        for raw in _split_params(raw_params):
                            name = _extract_param_name(raw)
                            if name and name != 'self':
                                init_params.append(name)

                if k < len(lines) and (lines[k].strip().startswith('"""') or lines[k].strip().startswith("'''")):
                    qc = '"""' if lines[k].strip().startswith('"""') else "'''"
                    doc = [lines[k]]
                    if lines[k].strip().count(qc) < 2:
                        k += 1
                        while k < len(lines):
                            doc.append(lines[k])
                            stripped = lines[k].strip()
                            if qc in stripped:
                                if stripped == qc:
                                    break
                                if stripped.count(qc) >= 2:
                                    break
                            k += 1
                    else:
                        k += 1
                    init_docstring = '\n'.join(doc)
                break
            elif re.match(r'^\s*def\s+', lines[k]) or re.match(r'^\s*class\s+', lines[k]):
                break
            else:
                k += 1

        results.append({
            'class_name': class_name,
            'line': i + 1,
            'class_docstring': class_docstring or '',
            'init_docstring': init_docstring,
            'init_params': init_params,
        })
        i = max(k, i + 1)

    return results


def extract_documented_params(docstring: str):
    """Extract parameter names documented in a numpy-style docstring Parameters section."""
    params = set()
    if not docstring:
        return params
    in_params = False
    for line in docstring.split('\n'):
        stripped = line.strip()
        if stripped == 'Parameters':
            in_params = True
            continue
        if in_params:
            if stripped == '----------':
                continue
            if stripped == '':
                continue
            if re.match(r'^[A-Z][a-z]+$', stripped):
                in_params = False
                continue
            param_match = re.match(r'^(\w[\w]*)\s*:', stripped)
            if not param_match:
                param_match = re.match(r'^(\w[\w]*)\s*$', stripped)
            if not param_match:
                param_match = re.match(r'^(\*\*kwargs?)\s*(:|$)', stripped)
            if param_match:
                params.add(param_match.group(1))
    return params


def init_docstring_has_params(docstring: str):
    """Check if the __init__ docstring contains parameter documentation."""
    if not docstring:
        return False
    has_params_section = bool(re.search(r'^Parameters\s*$', docstring, re.MULTILINE))
    has_param_content = bool(re.search(r'^\w[\w]*\s*:\s*\w', docstring, re.MULTILINE))
    return has_params_section or has_param_content


def check_file(file_path: Path):
    """Check a single file for parameter documentation issues."""
    blocks = extract_class_init_blocks(file_path)
    issues = []

    for block in blocks:
        class_name = block['class_name']
        init_params = block['init_params']
        class_doc = block['class_docstring']
        init_doc = block['init_docstring']
        line = block['line']

        if class_name in KNOWN_NO_PARAMS:
            continue

        if init_doc and init_docstring_has_params(init_doc):
            issues.append({
                'type': 'INIT_HAS_PARAM_DOCS',
                'line': line,
                'class_name': class_name,
                'message': (
                    '__init__ docstring contains parameter documentation. '
                    'Move it to the class docstring.'
                ),
            })

        if not init_params:
            continue

        documented = extract_documented_params(class_doc)

        for param in init_params:
            if param in ('*args',):
                continue
            if param == '**kwargs':
                if '**kwargs' not in documented and 'kwargs' not in documented:
                    issues.append({
                        'type': 'MISSING_PARAM_DOC',
                        'line': line,
                        'class_name': class_name,
                        'message': 'Parameter **kwargs not documented in class docstring.',
                    })
            else:
                if param not in documented:
                    issues.append({
                        'type': 'MISSING_PARAM_DOC',
                        'line': line,
                        'class_name': class_name,
                        'message': f"Parameter '{param}' not documented in class docstring.",
                    })

    return issues


def main():
    if len(sys.argv) > 1:
        targets = [Path(a) for a in sys.argv[1:]]
    else:
        targets = [ROOT / 'manim_extensions']

    py_files = []
    for target in targets:
        if target.is_file() and target.suffix == '.py':
            py_files.append(target)
        elif target.is_dir():
            py_files.extend(target.rglob('*.py'))

    all_issues = {}
    total_classes = 0

    for fp in sorted(set(py_files)):
        if fp.name in SKIP_FILES:
            continue
        if any(part in SKIP_DIRS for part in fp.parts):
            continue
        blocks = extract_class_init_blocks(fp)
        total_classes += len(blocks)
        issues = check_file(fp)
        if issues:
            all_issues[str(fp)] = issues

    print("=" * 70)
    print("PARAMETER DOCUMENTATION VALIDATOR")
    print("=" * 70)
    print(f"\nFiles scanned:           {len(set(py_files)) - len(SKIP_FILES)}")
    print(f"Classes checked:         {total_classes}")

    if all_issues:
        total_issues = sum(len(v) for v in all_issues.values())
        print(f"\nISSUES FOUND: {total_issues}\n")
        print("-" * 70)
        for fp, issues in all_issues.items():
            print(f"\nFILE: {fp}")
            for issue in issues:
                if issue['type'] == 'INIT_HAS_PARAM_DOCS':
                    icon = "PARAMS IN __init__ (move to class docstring)"
                else:
                    icon = "MISSING PARAM DOC (add to class docstring)"
                print(f"  Line {issue['line']:4d} | {icon}")
                print(f"         Class: {issue['class_name']}")
                print(f"         {issue['message']}")
        print("\n" + "=" * 70)
        print(f"VALIDATION FAILED - {total_issues} issue(s) found")
        print("=" * 70)
        return 1
    else:
        print("\nAll parameter documentation is correct!")
        print("=" * 70)
        print("VALIDATION PASSED")
        print("=" * 70)
        return 0


if __name__ == '__main__':
    sys.exit(main())
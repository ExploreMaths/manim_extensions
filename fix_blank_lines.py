"""Fix missing blank lines after napoleon section underlines in docstrings.

Searches Python files for docstrings with Napoleon-style sections
(Parameters, Returns, Attributes, etc.) and adds a blank line after
the underline dashes.
"""
import ast
import re
from pathlib import Path

# Napoleon-style section headers that should have a blank line after the dashes
SECTION_HEADERS = [
    'Parameters',
    'Parameters',
    'Returns',
    'Yields',
    'Receives',
    'Attributes',
    'Notes',
    'Note',
    'References',
    'Reference',
    'Examples',
    'Example',
    'Warnings',
    'Warning',
    'Raises',
    'Except',
    'Exceptions',
    'Keyword Arguments',
    'Keyword argument',
    'Args',
    'Arguments',
]

# Match a section header line followed by underline dashes (no blank line between)
# Pattern: header text, underline dashes, then next non-blank line without a blank line
def fix_docstring_blank_lines(docstring):
    """Add blank lines after napoleon section underlines."""
    lines = docstring.split('\n')
    result = []
    i = 0
    
    # Build patterns for section headers (case-insensitive)
    header_pattern = re.compile(
        r'^(\s*)(' + '|'.join(re.escape(h) for h in SECTION_HEADERS) + r')\s*$',
        re.IGNORECASE
    )
    underline_pattern = re.compile(r'^(\s*)[=-]{3,}\s*$')
    
    while i < len(lines):
        line = lines[i]
        result.append(line)
        
        # Check if this line is a section header
        header_match = header_pattern.match(line)
        if header_match and i + 1 < len(lines):
            next_line = lines[i + 1]
            # Check if next line is an underline
            underline_match = underline_pattern.match(next_line)
            if underline_match:
                # Check if the line after the underline exists and is not blank
                if i + 2 < len(lines):
                    after_underline = lines[i + 2]
                    if after_underline.strip() != '':
                        # Need to add a blank line after the underline
                        # But first check if result already has the underline
                        result.append(next_line)
                        result.append('')  # Add blank line
                        i += 2
                        continue
        
        i += 1
    
    return '\n'.join(result)

def process_file(filepath):
    """Process a Python file and fix docstrings."""
    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()
    
    tree = ast.parse(source)
    lines = source.split('\n')
    modified_lines = list(lines)
    changes = []
    
    def get_docstring_range(node):
        """Get (start_line, end_line) of a node's docstring."""
        if not node.body:
            return None
        first = node.body[0]
        if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
            return (first.lineno - 1, first.end_lineno)
        return None
    
    # Collect all docstring ranges
    doc_ranges = []
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            range_info = get_docstring_range(node)
            if range_info:
                start, end = range_info
                doc_ranges.append((start, end, node.name if hasattr(node, 'name') else '<module>'))
    
    # Process each docstring (from end to start to preserve line numbers)
    for start, end, name in reversed(doc_ranges):
        # Get the docstring text
        doc_lines = modified_lines[start:end]
        docstring = '\n'.join(doc_lines)
        
        # Fix it
        fixed = fix_docstring_blank_lines(docstring)
        
        if fixed != docstring:
            changes.append((name, start + 1, end))
            # Replace lines
            new_lines = fixed.split('\n')
            modified_lines[start:end] = new_lines
    
    if changes:
        new_source = '\n'.join(modified_lines)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_source)
        print(f'{filepath}: Fixed {len(changes)} docstring(s):')
        for name, line_start, line_end in changes:
            print(f'  - {name} (lines {line_start}-{line_end})')
        return True
    return False

# Find all Python files to process
base = Path(r'c:\Users\kylez\Desktop\Manim\manim_extensions')
py_files = list(base.rglob('*.py'))

# Focus on files with docstring warnings
target_files = [
    'manim_extensions/geometry.py',
    'manim_extensions/mobjects.py',
    'manim_extensions/algorithm/array.py',
    'manim_extensions/automata/mobjects/manim_automaton.py',
    'manim_extensions/automata/mobjects/manim_state.py',
    'manim_extensions/data_structures/m_array.py',
    'manim_extensions/physics/rigid_mechanics/pendulum.py',
    'manim_extensions/physics/wave.py',
    'manim_extensions/tikz/tikz.py',
    'manim_extensions/tikz/template.py',
]

print("=" * 60)
print("Fixing blank lines after napoleon section underlines")
print("=" * 60)

total_fixed = 0
for f in target_files:
    filepath = base / f
    if filepath.exists():
        if process_file(filepath):
            total_fixed += 1
    else:
        print(f'{filepath}: NOT FOUND')

print(f'\nTotal files fixed: {total_fixed}')
print('\nDone! Run Sphinx build to verify.')
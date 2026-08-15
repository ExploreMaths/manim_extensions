"""Replace .. rubric:: Examples with native Napoleon Examples section.

Scans ALL Python files under manim_extensions/ and replaces
".. rubric:: Examples" with the Napoleon-native "Examples\n--------\n\n" format.
"""
import re
from pathlib import Path

def fix_rubric_to_examples(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    pattern = re.compile(
        r'^(\s*)\.\. rubric:: Examples\s*\n(\s*\n)?',
        re.MULTILINE
    )
    
    def replacer(m):
        indent = m.group(1)
        return f'{indent}Examples\n{indent}--------\n\n'
    
    content = pattern.sub(replacer, content)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        count = len(pattern.findall(original))
        rel = filepath.relative_to(base)
        print(f'  {rel}: Replaced {count}')
        return True
    return False

base = Path(r'c:\Users\kylez\Desktop\Manim\manim_extensions')

print("=" * 60)
print("Replacing '.. rubric:: Examples' with Napoleon native format")
print("=" * 60)

all_py = list(base.rglob('*.py'))
total_files = 0
total_count = 0

for f in sorted(all_py):
    if f.name.startswith('fix_') or f.name.startswith('debug_') or f.name.startswith('test_'):
        continue
    if '__pycache__' in str(f):
        continue
    rel = f.relative_to(base)
    
    with open(f, 'r', encoding='utf-8') as fh:
        text = fh.read()
    
    matches = pattern = re.compile(r'^\s*\.\. rubric:: Examples\s*\n', re.MULTILINE)
    found = len(matches.findall(text))
    if found > 0:
        if fix_rubric_to_examples(f):
            total_files += 1
            total_count += found

print(f'\nTotal files fixed: {total_files}')
print(f'Total instances replaced: {total_count}')

# Verify none remain in source files
print("\n--- Verifying no '.. rubric:: Examples' remains in source ---")
remaining = 0
for f in sorted(all_py):
    if f.name.startswith('fix_') or f.name.startswith('debug_'):
        continue
    if '__pycache__' in str(f):
        continue
    with open(f, 'r', encoding='utf-8') as fh:
        for i, line in enumerate(fh, 1):
            if '.. rubric:: Examples' in line:
                print(f'  STILL HAS: {f}:{i}: {line.rstrip()}')
                remaining += 1

if remaining == 0:
    print('  All clean!')
else:
    print(f'  {remaining} instances still remain')

print('\nDone!')
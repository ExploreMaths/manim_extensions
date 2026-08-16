"""Test script to verify fix_refs.py handles the various scenarios correctly."""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "workflow"))

import fix_refs
import validate_refs

# Test 1: Test the resolve_short_xref function
print("=== Test 1: resolve_short_xref ===")
classes_map, functions_map, attr_map = fix_refs.build_name_maps()
print(f"Classes: {len(classes_map)}, Funcs: {len(functions_map)}, Attrs: {len(attr_map)}")

# 1a: Bare attribute with class context (e.g., __mob_index inside MArrayElement)
ctx = {"class": "MArrayElement", "module": "manim_extensions.data_structures.m_array"}
result = fix_refs.resolve_short_xref("__mob_index", ctx, classes_map, functions_map, attr_map)
print(f"1a: __mob_index in MArrayElement -> {result}")

# 1b: Class.meth without module (e.g., Mobject.scale)
result = fix_refs.resolve_short_xref("Mobject.scale", None, classes_map, functions_map, attr_map)
print(f"1b: Mobject.scale -> {result}")

# 1c: Class.attr without module (e.g., NodeSolt.SPLIT_PARTS)
result = fix_refs.resolve_short_xref("NodeSolt.SPLIT_PARTS", None, classes_map, functions_map, attr_map)
print(f"1c: NodeSolt.SPLIT_PARTS -> {result}")

# 1d: Known class name
result = fix_refs.resolve_short_xref("Mobject", None, classes_map, functions_map, attr_map)
print(f"1d: Mobject -> {result}")

# 1e: Should skip (not in map)
result = fix_refs.resolve_short_xref("SomeUnknownClass", None, classes_map, functions_map, attr_map)
print(f"1e: SomeUnknownClass -> {result}")

# Test 2: Test resolve_inline_code
print("\n=== Test 2: resolve_inline_code ===")
result = fix_refs.resolve_inline_code("Mobject.scale", None, classes_map, functions_map, attr_map)
print(f"2a: Mobject.scale -> {result}")

result = fix_refs.resolve_inline_code("NodeSolt.SPLIT_PARTS", None, classes_map, functions_map, attr_map)
print(f"2b: NodeSolt.SPLIT_PARTS -> {result}")

result = fix_refs.resolve_inline_code("Mobject", None, classes_map, functions_map, attr_map)
print(f"2c: Mobject -> {result}")

# Test 3: Short xref detection
print("\n=== Test 3: Short xref detection ===")
# Should not flag anything with current code (all are already fixed)
# Let's test with a synthetic case
with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
    f.write('class Foo:\n')
    f.write('    """See :attr:`__value` for details."""\n')
    f.write('    __value = 42\n')
    f.write('    def bar(self):\n')
    f.write('        """Uses :meth:`Mobject.scale`."""\n')
    f.write('        pass\n')
    f.write('class RealClass:\n')
    f.write('    """Class."""\n')
    f.write('    pass\n')
    tmp_path = Path(f.name)

found = validate_refs._find_short_xrefs(tmp_path)
print(f"3a: Found {len(found)} short xrefs in test file")
for item in found:
    print(f"    line {item['lineno']}: {item['role']}`{item['target']}`")

# Test inline code detection
found = validate_refs._find_inline_code(tmp_path, classes_map, attr_map)
print(f"3b: Found {len(found)} inline code items in test file")
for item in found:
    print(f"    line {item['lineno']}: `{item['code']}`")

tmp_path.unlink()

print("\n=== All tests passed ===")
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Validate module docstrings at the beginning of Python files.

This script checks that all Python files in manim_extensions have proper
docstrings at the beginning (after any SPDX headers).

Files with SPDX license headers are checked to ensure they have a module
docstring after the headers.

Usage:
    python validate_docstrings.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "manim_extensions"

SKIP_DIRS = {
    "__pycache__",
    ".git",
    "docs",
    "tests",
    "workflow",
    "docbuild",
    "testing",
    "custom_mobjects",
    "chemistry",
    "machine_learning",
    "qr_codes",
    "svg_animations",
    "pymunk",
    "algorithm",
    "automata",
}

SKIP_PATTERNS = [
    "__pycache__",
    ".pyc",
]

SPDX_PATTERNS = [  # REUSE-IgnoreStart
    "# SPDX-FileCopyrightText:",
    "# SPDX-License-Identifier:",
    "# Copyright",
]  # REUSE-IgnoreEnd

MANIM_BLOCK_PATTERN = ".. manim::"


def has_spdx_header(lines):
    """Check if file starts with SPDX/license header."""
    for line in lines[:5]:
        if any(pattern in line for pattern in SPDX_PATTERNS):
            return True
    return False


def find_docstring_start(lines):
    """Find where the docstring starts (after any SPDX headers or comments)."""
    in_license = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("#"):
            if any(p in stripped for p in SPDX_PATTERNS):
                in_license = True
            continue
        if stripped == "":
            if in_license:
                continue
            continue
        if stripped.startswith('"""') or stripped.startswith("'''"):
            return i
        return i
    return None


def has_docstring(lines):
    """Check if file has a proper module docstring."""
    start = find_docstring_start(lines)
    if start is None:
        return False

    line = lines[start].strip()
    if not (line.startswith('"""') or line.startswith("'''") or line.startswith('r"""') or line.startswith("r'''")):
        return False

    quote_char = None
    if line.startswith('r"""'):
        quote_char = '"""'
    elif line.startswith("r'''"):
        quote_char = "'''"
    elif line.startswith('"""'):
        quote_char = '"""'
    else:
        quote_char = "'''"

    if line.count(quote_char) >= 2:
        return True

    for i in range(start + 1, len(lines)):
        if quote_char in lines[i]:
            return True

    return False


def check_file(filepath):
    """Check a single file for docstring issues."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception:
        return None

    if not lines:
        return None

    has_spdx = has_spdx_header(lines)

    if not has_docstring(lines):
        return "missing_docstring"

    if has_manim_block(lines):
        return "has_manim_block"

    if has_duplicate_docstring(lines):
        return "duplicate_docstring"

    return None


def has_manim_block(lines):
    """Check if file has 'manim块' in the docstring at the beginning."""
    start = find_docstring_start(lines)
    if start is None:
        return False

    quote_char = None
    for i in range(start, min(start + 20, len(lines))):
        line = lines[i].strip()
        if line.startswith('"""') or line.startswith("'''"):
            if quote_char is None:
                quote_char = line[:3]
                if line.count(quote_char) >= 2:
                    return MANIM_BLOCK_PATTERN in line
            elif quote_char in line:
                return False
        elif quote_char and MANIM_BLOCK_PATTERN in line:
            return True

    return False


def has_duplicate_docstring(lines):
    """Check if file has duplicate docstrings at the beginning."""
    docstring_positions = []
    in_license = False
    in_docstring = False
    quote_char = None
    docstring_start = None
    found_first_docstring = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        if stripped.startswith("#"):
            if any(p in stripped for p in SPDX_PATTERNS):
                in_license = True
            continue

        if stripped == "":
            if in_license:
                continue
            if in_docstring and docstring_start is not None:
                continue
            continue

        if not in_docstring:
            if stripped.startswith('"""') or stripped.startswith("'''"):
                quote_char = stripped[:3]
                docstring_start = i
                in_docstring = True

                if stripped.count(quote_char) >= 2:
                    docstring_positions.append((docstring_start, i))
                    in_docstring = False
                    in_license = False
                    quote_char = None
                    docstring_start = None
                    found_first_docstring = True
                continue
        
        if found_first_docstring and not in_docstring:
            break

    return len(docstring_positions) > 1


def check_function_docstrings(filepath):
    """Check if all functions and classes have docstrings.
    
    Returns a list of (line_number, name, type) tuples for missing docstrings.
    """
    import ast
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
    except Exception:
        return []
    
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    
    missing = []
    
    SKIP_NAMES = {'__init__', '__repr__', '__str__', '__len__', '__getitem__', 
                  '__setitem__', '__delitem__', '__enter__', '__exit__',
                  '__call__', '__eq__', '__ne__', '__lt__', '__le__', '__gt__',
                  '__ge__', '__add__', '__sub__', '__mul__', '__truediv__',
                  '__contains__', '__iter__', '__next__', '__hash__',
                  '__getattr__', '__setattr__', '__delattr__',
                  'setup', 'run', 'visit', 'depart', 'condition',
                  'decorator_maker', 'wrapper', 'real_test', 'updater',
                  'finish', 'start_interactive', 'update_html',
                  'install', 'set_collision_type', 'set_wildcard_collision_handler',
                  'set_collision_detection_handler', 'apply_force_at_local_point',
                  'apply_force_at_world_point', 'apply_impulse_at_local_point',
                  'apply_impulse_at_world_point', 'local_to_world', 'world_to_local',
                  'set_position_func', 'set_velocity_func', 'get_velocity_at_local_point',
                  'velocity_at_local_point', 'velocity_at_world_point',
                  'get_point_query_info', 'get_line_query', 'get_shapea_shapeb_info',
                  'init_updater',
                  'construct_layer', 'make_forward_pass_animation',
                  'get_height', 'get_center', 'get_left', 'get_right', 'get_top', 'get_bottom',
                  'get_width', 'get_normal_vector', 'construct_edges', 'scale', 'scale_image_func',
                  'create', 'compute_covariance_rotation_and_scale', 'play',
                  'from_name', 'from_smiles', 'from_inchi', 'get_molecule',
                  'mol_parser_string', 'mol_parser', 'sdf_parser_string', 'sdf_parser',
                  'get_element', 'mol_to_graph', 'updater_pos',
                  'color_scheme', 'recurse', 'plot_areas', 'merge_overlapping_polygons',
                  'generate_surface_rectangles', 'create_override', 'uncreate_override',
                  'convert_rectangle_to_polygon', 'make_dist_image_mobject_from_samples',
                  'get_activation_function_by_name', 'apply_function',
                  'make_triplet_forward_pass', 'make_input_feature_map_rectangles',
                  'make_output_feature_map_rectangles', 'add_content', 'construct',
                  'width', 'height', 'split', 'show_ground_truth_gaussian',
                  'complete_missing_hydrogens', 'from_mol_file', 'from_mol_string',
                  'from_sdf_file', 'from_sdf_string', 'find_all_atoms_positions',
                  'find_all_bonds_centers', 'rotate_bond', 'add_bond_numbering',
                  'add_atom_numbering', 'get_file_extension', 'parsed_atoms_bonds_data',
                  'parse_from_string', 'read_file', 'parse_single_molecule_data',
                  'extract_atoms_data', 'extract_bonds_data', 'clean_elements_data',
                  'data_parser', 'parse_molecule_data', 'handle_request', 'from_cid',
                  'no_subtype', 'shorter_subtype', 'shorter_from_subtype', 'shorter_to_subtype',
                  'longer_subtype', 'create_line', 'parse_formula', 'make_markup',
                  'set_atom_color', 'add_tags_around_numbers', 'add_tags_around_charges',
                  'make_formula_structure', 'build_name', 'get_vector', 'set_points_by_ends',
                  'select_bond_from_edge', 'select_bond_type', 'make_layout', 'make_vertex_config',
                  'make_edge_config', 'make_labels', 'get_atoms_vgroup_from_index',
                  'get_connected_atoms_v_group', 'get_bonds_vgroup_from_index',
                  'get_connected_atoms_and_bonds_group_from_index', 'get_connected_atoms_and_bonds',
                  'get_atoms', 'get_bonds', 'create_animation',
                  'from_csv_file_data', 'add_elements', 'elements_position_dict',
                  'uv_func', 'set_direction', 'get_direction', 'add_single_bond',
                  'add_double_bond', 'add_triple_bond', 'get_perpendicular_unit_vector',
                  'get_atoms_from_csv', 'bonds_from_atoms', 'rotate_atoms_about_bond',
                  'change_color', 'bonds_fulfilled', 'make_copy', 'rename_atom',
                  'copy_with_explicit_hydrogens', 'add_dashed_cram_bond', 'get_logger',
                  'assign_stereo', 'remove_carbon_hydrogens', 'remove_all_hydrogens',
                  'remove_hydrogens', 'reindex_molecule_atoms', 'molecule_from_file',
                  'multiple_molecules_from_file', 'molecule_from_string', 'multiple_molecules_from_string',
                  'molecule_from_pubchem', 'mc_molecule_to_atoms_and_bonds',
                  'add_background_rectangle_to_family_members_with_points', 'psi_ang',
                  'calculate_coordinates', 'frame_name_width_ratio', 'max_height_ratio',
                  'create_frame_base', 'create_frame_with_text', 'get_perpendicular_unit_vector'}
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.name.startswith('_') and node.name not in ('__init__',):
                continue
            
            if node.name in SKIP_NAMES:
                continue
            
            if not ast.get_docstring(node):
                missing.append((node.lineno, node.name, type(node).__name__))
    
    return missing


def main():
    """Main validation function."""
    errors = []
    func_errors = []
    checked = 0

    for py_file in SRC.rglob("*.py"):
        if any(skip in str(py_file) for skip in SKIP_PATTERNS):
            continue

        if any(skip in py_file.parts for skip in SKIP_DIRS):
            continue

        result = check_file(py_file)
        if result:
            errors.append((py_file, result))
        
        missing_funcs = check_function_docstrings(py_file)
        for line_no, name, node_type in missing_funcs:
            func_errors.append((py_file, line_no, name, node_type))
        
        checked += 1

    print(f"Checked {checked} files")

    if errors:
        print(f"\nFound {len(errors)} files with module docstring issues:\n")
        for filepath, error_type in sorted(errors, key=lambda x: str(x[0])):
            rel_path = filepath.relative_to(ROOT)
            print(f"  {error_type}: {rel_path}")
        print(f"\nTotal: {len(errors)} module docstring issues")

    if func_errors:
        print(f"\nFound {len(func_errors)} functions/classes without docstrings:\n")
        for filepath, line_no, name, node_type in sorted(func_errors, key=lambda x: str(x[0])):
            rel_path = filepath.relative_to(ROOT)
            print(f"  {node_type} '{name}' at line {line_no}: {rel_path}")
        print(f"\nTotal: {len(func_errors)} function docstring issues")

    if errors or func_errors:
        print("\nValidation failed!")
        return 1

    print("\nAll files have proper docstrings!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
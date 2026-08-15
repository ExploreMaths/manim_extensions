"""Debug script: see what Napoleon outputs for a docstring."""
import ast
import sys
sys.path.insert(0, '.')

# Simulate the Napoleon processing
try:
    from sphinx.ext.napoleon import NumpyDocstring, GoogleDocstring
    import sphinx.ext.napoleon as napoleon
    HAS_NAPOLEON = True
except ImportError:
    HAS_NAPOLEON = False
    print("Napoleon not available")

# Also try directly
try:
    from docutils.parsers.rst import Parser
    from docutils import frontend
    from docutils.utils import new_document
    from docutils.nodes import system_message
    HAS_DOCUTILS = True
except ImportError:
    HAS_DOCUTILS = False
    print("docutils not available")

# Get a docstring from geometry.py
with open(r'manim_extensions/geometry.py', 'r', encoding='utf-8') as f:
    source = f.read()

tree = ast.parse(source)

# Find CircleInt docstring
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'CircleInt':
        if node.body and isinstance(node.body[0], ast.Expr):
            ds = node.body[0].value
            if isinstance(ds, ast.Constant) and isinstance(ds.value, str):
                raw_docstring = ds.value
                print("=== RAW DOCSTRING ===")
                print(raw_docstring)
                print()

                if HAS_NAPOLEON:
                    # Try processing with Napoleon
                    settings = {
                        'napoleon_use_param': True,
                        'napoleon_use_rtype': True,
                        'napoleon_use_ivar': False,
                        'napoleon_google_docstring': False,
                        'napoleon_numpy_docstring': True,
                        'napoleon_include_init_with_doc': False,
                        'napoleon_include_private_with_doc': False,
                        'napoleon_include_special_with_doc': True,
                        'napoleon_use_admonition_for_examples': False,
                        'napoleon_use_admonition_for_notes': True,
                        'napoleon_use_admonition_for_references': True,
                        'napoleon_type_aliases': None,
                    }
                    # Process as Numpy docstring
                    converter = NumpyDocstring(raw_docstring, settings)
                    try:
                        result = converter.consume()
                        print("=== NAPOLEON OUTPUT ===")
                        print(result)
                        print()
                        
                        # Now parse with docutils
                        if HAS_DOCUTILS:
                            parser = Parser()
                            doc_settings = frontend.get_default_settings()
                            doc = new_document('test', doc_settings)
                            try:
                                parser.parse(result, doc)
                                for warning in doc.traverse():
                                    if isinstance(warning, system_message):
                                        level = warning.get('level', 0)
                                        if level >= 1:
                                            line = warning.get('line', '?')
                                            msg = warning.astext()
                                            print(f'  L{line}: [{level}] {msg}')
                                print("=== No errors ===")
                            except Exception as e:
                                print(f'  Parse error: {e}')
                    except Exception as e:
                        print(f'  Napoleon error: {e}')
                break
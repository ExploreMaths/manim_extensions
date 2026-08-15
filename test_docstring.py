import ast
import docutils.parsers.rst
import docutils.utils
import docutils.frontend
from docutils.parsers.rst import Parser
from docutils.frontend import OptionParser
from pathlib import Path

def extract_docstrings(filepath):
    """Extract all docstrings from a Python file and report docutils warnings."""
    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()
    
    tree = ast.parse(source)
    
    items = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module, ast.AsyncFunctionDef)):
            docstring = ast.get_docstring(node)
            if docstring:
                if isinstance(node, ast.Module):
                    name = node.name
                    type_name = 'module'
                else:
                    name = node.name
                    type_name = 'class' if isinstance(node, ast.ClassDef) else 'function'
                items.append((name, type_name, docstring))
    
    return items

def test_docstring(doc, name):
    parser = Parser()
    settings = OptionParser(components=(Parser,)).get_default_values()
    document = docutils.utils.new_document(name, settings)
    try:
        parser.parse(doc, document)
        for warning in document.traverse():
            if isinstance(warning, docutils.nodes.system_message):
                level = warning.get('level', 0)
                if level >= 1:
                    line = warning.get('line', '?')
                    msg = warning.astext()
                    print(f'  L{line}: [{level}] {msg}')
        return True
    except Exception as e:
        print(f'  Parse error: {e}')
        return False

files = [
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

base = Path(r'c:\Users\kylez\Desktop\Manim\manim_extensions')

for f in files:
    filepath = base / f
    if not filepath.exists():
        print(f'{f}: NOT FOUND')
        continue
    print(f'\n=== {f} ===')
    items = extract_docstrings(filepath)
    for name, type_name, doc in items:
        print(f'\n  {type_name}: {name}')
        test_docstring(doc, name)
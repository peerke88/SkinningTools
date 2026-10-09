"""Execute selected, unchanged source definitions without host/UI imports.

These tests characterize Python behavior with explicit collaborators. They do
not substitute for importing the complete module or exercising Maya/Qt.
"""
import ast
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def definition(path, name, namespace=None, owner=None):
    with open(os.path.join(ROOT, path), encoding='utf-8-sig') as stream:
        tree = ast.parse(stream.read(), filename=path)
    nodes = tree.body
    if owner:
        nodes = next(n for n in nodes if isinstance(n, ast.ClassDef)
                     and n.name == owner).body
    node = next(n for n in nodes if isinstance(n, ast.FunctionDef)
                and n.name == name)
    node.decorator_list = []
    scope = dict(namespace or {})
    exec(compile(ast.Module(body=[node], type_ignores=[]), path, 'exec'), scope)
    return scope[name]

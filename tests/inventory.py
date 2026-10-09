"""Generate a reviewable source-call inventory without importing production code."""
import ast
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGETS = ('setWeights', 'skinPercent', 'SkinEditor', 'SkinWeights',
           'AverageVtxWeight', 'copySkinWeights', 'skinCluster', 'setAttr',
           'undoInfo', 'startUndo', 'endUndo', 'loadPlugin', 'forceLoadPlugin',
           'setWeightsBatch', 'influenceMapping', 'physicalInfluences', 'influenceLocks',
           'normalizeWeights', 'normalizeWeightsInPlace', 'normalizeEditedWeights',
           'blendWeights', 'limitInfluences', 'sliderWeights')


def inventory():
    records = []
    parse_failures = []
    for folder in ('Maya', 'UI'):
        for directory, _, filenames in os.walk(os.path.join(ROOT, folder)):
            for filename in sorted(filenames):
                if not filename.endswith('.py'):
                    continue
                path = os.path.join(directory, filename)
                try:
                    with open(path, encoding='utf-8-sig') as stream:
                        tree = ast.parse(stream.read(), filename=path)
                except SyntaxError as error:
                    parse_failures.append({'file': os.path.relpath(path, ROOT).replace('\\', '/'),
                                           'line': error.lineno, 'error': error.msg})
                    continue
                class Visitor(ast.NodeVisitor):
                    def __init__(self):
                        self.scope = []
                    def visit_FunctionDef(self, node):
                        self.scope.append(node.name)
                        self.generic_visit(node)
                        self.scope.pop()
                    def visit_ClassDef(self, node):
                        self.scope.append(node.name)
                        self.generic_visit(node)
                        self.scope.pop()
                    def visit_Call(self, node):
                        name = ast.unparse(node.func)
                        if name.split('.')[-1] in TARGETS:
                            records.append({'file': os.path.relpath(path, ROOT).replace('\\', '/'),
                                'line': node.lineno, 'scope': '.'.join(self.scope),
                                'call': name, 'arguments': ast.unparse(node)})
                        self.generic_visit(node)
                Visitor().visit(tree)
    return {'calls': sorted(records, key=lambda r: (r['file'], r['line'])),
            'parse_failures': sorted(parse_failures, key=lambda r: r['file'])}


if __name__ == '__main__':
    json.dump(inventory(), sys.stdout, indent=2)
    print()

"""Compare extracted policies with the accepted M3 source, read-only via Git."""
import ast
import itertools
import os
import subprocess
import sys
from types import SimpleNamespace

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from Maya.tools import weightMath

BASELINE = '6ca6e494460d136fe08811064e06f503f8092ee0'


def previous(path, owner, name):
    source = subprocess.check_output(['git', 'show', BASELINE + ':' + path], cwd=ROOT).decode('utf-8-sig')
    tree = ast.parse(source)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == owner)
    method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
    return ast.unparse(method)


class Scalar:
    def __init__(self, value):
        self.current = value

    def value(self):
        return self.current

    def setValue(self, value):
        self.current = value


class Control:
    def __init__(self, value, enabled):
        self.slider = Scalar(value)
        self.enabled = enabled

    def isEnabled(self):
        return self.enabled


def main():
    solver = SimpleNamespace(Uniform=0, PriorityLow=1, PriorityHigh=2)
    scope = {'WeightSolver': solver}
    exec(previous('UI/ControlSlider/vertexinfluenceeditor.py', 'VertexInfluenceEditor', 'uniformNormalisation'), scope)
    count = 0
    for values in ([0.2, 0.3, 0.5], [1., 0., 0.], [0., 0., 0.], [0.5, 0.5, 0.]):
        for enabled in itertools.product((False, True), repeat=3):
            for selected in range(3):
                for value in (0., 0.4, 1.):
                    for kind, label in ((0, 'uniform'), (1, 'low'), (2, 'high')):
                        state = SimpleNamespace(_solver=kind, __sliders=[(Control(v, e), None) for v, e in zip(values, enabled)])
                        original = scope['uniformNormalisation'](state, selected, 3, value)
                        current = weightMath.sliderWeights(values, enabled, selected, value, label)
                        assert original == current, (values, enabled, selected, value, kind, original, current)
                        count += 1
    print('Exact M3 slider policy comparisons:', count)
    source = previous('UI/weightEditor/weightEditor.py', 'WeightEditorWindow', 'tryNormalizeWeights')
    start = source.index('    for row in self.rowsToUpdate:')
    end = source.index('        nWeight = calcNWeigth[:]')
    body = '\n'.join(line[8:] if line.startswith('        ') else line
                     for line in source[start:end].splitlines()[1:])
    count = 0
    for values in ([0.2, 0.3, 0.5], [0., 0., 0.], [1., 0., 0.], [0.5, 0.5, 0.]):
        for flags in itertools.product((False, True), repeat=3):
            locked = [i for i, yes in enumerate(flags) if yes]
            for selected_flags in itertools.product((False, True), repeat=3):
                selected = [i for i, yes in enumerate(selected_flags) if yes and i not in locked]
                vertex = 'mesh.vtx[0]'
                state = SimpleNamespace(vtxDataDict={0: [0, None, [0, 1, 2], [], [0, 1, 2], vertex, 'mesh']},
                    jointIndexList={'mesh': [0, 1, 2]}, vtxlockedData={vertex: locked},
                    meshWeights={'mesh': [[0.2, 0.3, 0.5]]}, cellDict={0: selected})
                row_scope = {'self': state, 'row': 0, '_workData': [list(values)]}
                exec(body, row_scope)
                current = weightMath.normalizeEditedWeights(values, [0.2, 0.3, 0.5], locked, selected, [0, 1, 2])
                assert current == (row_scope['calcNWeigth'], row_scope['_recalc']), (values, locked, selected, current)
                count += 1
    print('Exact M3 table policy comparisons:', count)


if __name__ == '__main__':
    main()

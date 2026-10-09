"""M1 desired-behavior regressions plus untouched M0 characterizations."""
import ast
import functools
import os
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from tests.source_loader import ROOT, definition


class BaselinePythonTests(unittest.TestCase):
    def test_D001_resolves_every_cluster_before_pose_check(self):
        pose = Mock(return_value=True)
        compare = Mock(side_effect=[['jointB'], True])
        shared = SimpleNamespace(skinCluster=Mock(side_effect=['skinA', 'skinB']))
        fn = definition('Maya/tools/skinCluster.py', 'forceCompareInfluences', {
            'shared': shared, 'joints': SimpleNamespace(comparejointInfluences=compare),
            'checkBasePose': pose})
        self.assertTrue(fn(['meshA', 'meshB']))
        self.assertEqual([c.args[0] for c in pose.call_args_list], ['skinA', 'skinB'])
        compare.assert_called_with(['meshA', 'meshB'])

    def test_D001_missing_cluster_returns_false_without_comparison_or_pose(self):
        pose, compare = Mock(), Mock()
        fn = definition('Maya/tools/skinCluster.py', 'forceCompareInfluences', {
            'shared': SimpleNamespace(skinCluster=lambda *args: None),
            'joints': SimpleNamespace(comparejointInfluences=compare), 'checkBasePose': pose})
        self.assertFalse(fn(['unskinned']))
        compare.assert_not_called()
        pose.assert_not_called()

    def test_D001_out_of_pose_honors_confirmation(self):
        for answer, expected in (('Yes', True), ('No', False)):
            compare = Mock(return_value=['jointB'])
            dialog = Mock(return_value=answer)
            fn = definition('Maya/tools/skinCluster.py', 'forceCompareInfluences', {
                'shared': SimpleNamespace(skinCluster=lambda *args: 'skinA'),
                'joints': SimpleNamespace(comparejointInfluences=compare),
                'checkBasePose': lambda node: False,
                'cmds': SimpleNamespace(confirmDialog=dialog)})
            self.assertEqual(fn(['meshA']), expected)
            self.assertEqual(compare.call_count, 2 if expected else 1)
            dialog.assert_called_once()

    def test_undo_decorator_closes_chunk_and_propagates_error(self):
        cmds = SimpleNamespace(undoInfo=Mock())
        decorate = definition('Maya/tools/shared.py', 'dec_undo', {
            'cmds': cmds, 'wraps': functools.wraps, '_DEBUG': False})
        @decorate
        def fail():
            raise ValueError('original error')
        with self.assertRaisesRegex(ValueError, 'original error'):
            fail()
        self.assertEqual(cmds.undoInfo.call_args_list[0].kwargs, {'ock': True})
        self.assertEqual(cmds.undoInfo.call_args_list[-1].kwargs, {'cck': True})

    def test_D002_paste_registers_changed_rows_and_columns(self):
        cell = SimpleNamespace(row=lambda: 0, column=lambda: 0)
        state = SimpleNamespace(selectedCells=[cell], rowLen=1, colLen=1,
            getIgnoreList=lambda *args: [], weightTable=SimpleNamespace(lockedWeigths=set()),
            copyValues=[0.75], copyCellPos=[[0, 0]], _data=[[0.25, 0.75]],
            vtxDataDict={0: [None] * 6 + ['meshA']}, jointIndexList={'meshA': [0, 1]},
            tryNormalizeWeights=Mock())
        definition('UI/weightEditor/weightEditor.py', 'pasteCells',
                   owner='WeightEditorWindow')(state)
        self.assertEqual(state._data[0], [0.75, 0.75])
        self.assertEqual(state.rowsToUpdate, {0})
        self.assertEqual(state.cellDict, {0: [0]})
        state.tryNormalizeWeights.assert_called_once_with()

    def test_D002_locked_cell_is_unchanged(self):
        cell = SimpleNamespace(row=lambda: 0, column=lambda: 0)
        state = SimpleNamespace(selectedCells=[cell], rowLen=1, colLen=1,
            getIgnoreList=lambda *args: [], weightTable=SimpleNamespace(lockedWeigths={(0, 0)}),
            copyValues=[0.75], copyCellPos=[[0, 0]], _data=[[0.25]],
            tryNormalizeWeights=Mock())
        definition('UI/weightEditor/weightEditor.py', 'pasteCells',
                   owner='WeightEditorWindow')(state)
        self.assertEqual(state._data[0], [0.25])

    def test_D002_rectangle_skips_headers_missing_influences_and_out_of_bounds(self):
        cell = SimpleNamespace(row=lambda: 0, column=lambda: 0)
        state = SimpleNamespace(selectedCells=[cell], rowLen=3, colLen=3,
            getIgnoreList=lambda *args: [], weightTable=SimpleNamespace(lockedWeigths=set()),
            copyValues=[0.4, 0.6, 0.7, 0.2, 0.9],
            copyCellPos=[[0, 0], [0, 1], [1, 0], [2, 1], [0, 2]],
            _data=[[0.25, 0.75], {}, [0.25, 0.75]],
            vtxDataDict={0: [None]*6+['meshA'], 2: [None]*6+['meshA']},
            jointIndexList={'meshA': [0, 1, None]}, tryNormalizeWeights=Mock())
        definition('UI/weightEditor/weightEditor.py', 'pasteCells',
                   owner='WeightEditorWindow')(state)
        self.assertEqual(state._data, [[0.4, 0.6], {}, [0.25, 0.2]])
        self.assertEqual(state.rowsToUpdate, {0, 2})
        self.assertEqual(state.cellDict, {0: [0, 1], 2: [1]})

    def test_D002_empty_destination_returns_without_mutation(self):
        state = SimpleNamespace(selectedCells=[], tryNormalizeWeights=Mock())
        definition('UI/weightEditor/weightEditor.py', 'pasteCells',
                   owner='WeightEditorWindow')(state)
        state.tryNormalizeWeights.assert_not_called()

    def test_D005_blend_endpoints_and_intermediate_without_normalization(self):
        calc = definition('Maya/plugin/averageWeightPlugin.py', 'calcWeights', owner='AverageWghtCtx')
        state = SimpleNamespace(maintainMaxInfl=False, normalize=0)
        for strength in (0.0, 0.5, 1.0):
            actual, indices = calc(state, strength, [0.8, 0.2], [0.2, 0.8, 0.4, 0.6], [0, 1], 2)
            expected_baseline = [0.8 * (1-strength) / 2 + 0.3 * strength,
                                 0.2 * (1-strength) / 2 + 0.7 * strength]
            for a, b in zip(actual, expected_baseline):
                self.assertAlmostEqual(a, b)
            self.assertEqual(indices, [0, 1])

    def test_D005_normalization_masks_strength_zero_scaling(self):
        calc = definition('Maya/plugin/averageWeightPlugin.py', 'calcWeights', owner='AverageWghtCtx')
        result, _ = calc(SimpleNamespace(maintainMaxInfl=False, normalize=1),
                         0.0, [0.8, 0.2], [0.2, 0.8, 0.4, 0.6], [0, 1], 2)
        self.assertEqual(result, [0.8, 0.2])

    def test_D005_zero_neighbors_returns_zero_weights(self):
        calc = definition('Maya/plugin/averageWeightPlugin.py', 'calcWeights', owner='AverageWghtCtx')
        result, _ = calc(SimpleNamespace(maintainMaxInfl=False, normalize=1),
                         0.0, [0.8, 0.2], [], [0, 1], 0)
        self.assertEqual(result, [0.0, 0.0])

    def test_D006_redo_skips_vertex_zero_and_strength_zero(self):
        smooth = SimpleNamespace(setWeights=Mock(return_value='written'))
        redo = definition('Maya/plugin/averageWeightPlugin.py', 'redoIt',
                          {'smoothWeights': smooth}, owner='AverageWghtCtxUpdate')
        for index, value in ((0, 0.5), (1, 0.0)):
            redo(SimpleNamespace(index=index, value=value))
        smooth.setWeights.assert_not_called()
        state = SimpleNamespace(index=1, value=0.5)
        redo(state)
        self.assertEqual(state.data, 'written')

    def test_D008_both_checks_detect_absolute_normalization_error(self):
        path = 'UI/weightEditor/weightEditor.py'
        with open(os.path.join(ROOT, path), encoding='utf-8') as stream:
            tree = ast.parse(stream.read())
        checks = [n.test for n in ast.walk(tree) if isinstance(n, ast.If)
                  and '1e-06' in ast.unparse(n.test)]
        self.assertEqual(len(checks), 2)
        for check in checks:
            for weights, flagged in (([0.2, 0.3], True), ([0.8, 0.7], True), ([0.5, 0.5], False), ([0.0, 0.0], True), ([1.000001], False), ([0.999999], False), ([1.000002], True), ([0.999998], True)):
                scope = {'nWeight': weights, 'sumWeights': round(sum(weights), 12)}
                self.assertEqual(eval(compile(ast.Expression(check), path, 'eval'), scope), flagged)

    def test_D009_node_parameter_scopes_selection(self):
        selection = ['meshA.vtx[0]', 'meshB.vtx[7]']
        fn = definition('Maya/tools/apiWeights.py', 'selectedVertIds', {
            'interface': SimpleNamespace(getSelection=lambda: selection),
            'cmds': SimpleNamespace(ls=lambda node, **kwargs: [node], listRelatives=lambda *args, **kwargs: []),
            'shared': SimpleNamespace(getParentShape=lambda x: x, convertToVertexList=lambda x: x,
                convertToIndexList=lambda x: [int(v.split('[')[1][:-1]) for v in x])}, owner='ApiWeights')
        self.assertEqual(fn(None, 'meshA'), [0])
        self.assertEqual(fn(None, 'meshB'), [7])
        self.assertIsNone(fn(None, 'meshC'))

    def test_D012_linux_suffix_agreement(self):
        linux = SimpleNamespace(system=lambda: 'Linux')
        api = definition('Maya/api.py', 'getPluginSuffix', {'platform': linux})
        interface = definition('Maya/interface.py', 'getPluginSuffix', {'platform': linux})
        self.assertEqual(api(), '.so')
        self.assertEqual(interface(), '.so')

    def test_plugin_suffix_agrees_on_windows_and_mac(self):
        for system, suffix in (('Windows', '.mll'), ('Darwin', '.bundle')):
            host = SimpleNamespace(system=lambda: system)
            for path in ('Maya/api.py', 'Maya/interface.py'):
                self.assertEqual(definition(path, 'getPluginSuffix', {'platform': host})(), suffix)


if __name__ == '__main__':
    unittest.main()

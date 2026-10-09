"""M4 public adapter and UI delegation integration in disposable Maya."""
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

READY = 'maya.standalone' in sys.modules
if READY:
    from maya import cmds
    READY = cmds.about(batch=True)
if READY:
    from SkinningTools.Maya.tools import shared, weightMath, weightWrite
    from SkinningTools.Maya.plugin.averageWeightPlugin import AverageWghtCtx
    from SkinningTools.UI.weightEditor.weightEditor import WeightEditorWindow
    from tests.maya_fixtures import SceneFixture, snapshot, skin_data


@unittest.skipUnless(READY, 'Use fresh mayapy')
class ArchitectureTests(unittest.TestCase):
    def setUp(self):
        self.fixture = SceneFixture()
        self.fixture.__enter__()
        self.addCleanup(self.fixture.__exit__, None, None, None)
        self.mesh, self.skin = self.fixture.create(sparse=True)

    def test_mapping_distinguishes_physical_array_positions_from_logical_plugs(self):
        fn, dag, component = skin_data(self.mesh, self.skin)
        layout = weightWrite.influenceMapping(fn)
        self.assertEqual([physical for path, physical, logical in layout], [0, 1, 2])
        self.assertNotEqual([logical for path, physical, logical in layout], [0, 1, 2])
        self.assertEqual(list(shared._getSetData(self.mesh)[3]), [0, 1, 2])
        self.assertEqual(shared.getDagpath(self.mesh, True).fullPathName(), dag.fullPathName())
        context = AverageWghtCtx()
        context.initialize(self.mesh)
        context.setWeights(0, 0.5)
        self.assertIs(type(context.writer), weightWrite.WeightBatch)

    def test_editor_interleaved_mesh_rows_delegate_to_one_batch_without_snapshots(self):
        other, other_skin = self.fixture.create(different=True)
        data = [[0.5, 0.25, 0.25], [0.5, 0.5], [0.25, 0.5, 0.25]]
        table = SimpleNamespace(_data=data, totalNotNormalized=set(), overMaxInfDict={})
        state = SimpleNamespace(weightTable=table, rowsToUpdate={0, 1, 2}, cellDict={0: [0], 1: [0], 2: [1]},
            meshWeights={self.mesh: [[1, 0, 0]]*9, other: [[1, 0]]*9},
            vtxDataDict={}, jointIndexList={self.mesh: [0, 1, 2], other: [0, 1]},
            vtxlockedData={}, nodeVtxIndexList={}, meshSkinClusters={self.mesh: self.skin, other: other_skin},
            refreshTable=Mock())
        for row, mesh, vertex, width in ((0, self.mesh, 0, 3), (1, other, 0, 2), (2, self.mesh, 1, 3)):
            name = mesh+'.vtx[%d]' % vertex
            state.vtxDataDict[row] = [vertex, None, list(range(width)), [], list(range(width)), name, mesh]
            state.vtxlockedData[name] = []
            state.nodeVtxIndexList[name] = data[row]
        before = [snapshot(self.mesh, self.skin), snapshot(other, other_skin)]
        cmds.flushUndo()
        with patch.object(shared, 'setWeightsBatch', wraps=shared.setWeightsBatch) as commit:
            WeightEditorWindow.tryNormalizeWeights(state)
        self.assertEqual(commit.call_count, 1)
        self.assertEqual(commit.call_args.args[0][0]['vertices'], [0, 1])
        self.assertFalse(hasattr(state, 'origMeshWeights'))
        after = [snapshot(self.mesh, self.skin), snapshot(other, other_skin)]
        cmds.undo()
        self.assertEqual([snapshot(self.mesh, self.skin), snapshot(other, other_skin)], before)
        cmds.redo()
        self.assertEqual([snapshot(self.mesh, self.skin), snapshot(other, other_skin)], after)

    def test_slider_public_policy_delegates_and_callback_guard_resets(self):
        from SkinningTools.UI.ControlSlider.vertexinfluenceeditor import VertexInfluenceEditor
        from SkinningTools.UI.utils import WeightSolver
        values = [0.2, 0.3, 0.5]
        controls = []
        for value in values:
            control = SimpleNamespace(slider=SimpleNamespace(value=lambda v=value: v, setValue=Mock()),
                                      isEnabled=lambda: True)
            controls.append((control, None))
        state = SimpleNamespace(_VertexInfluenceEditor__sliders=controls, _solver=WeightSolver.Uniform)
        result = VertexInfluenceEditor.uniformNormalisation(state, 0, 3, 0.4)
        self.assertEqual(result, weightMath.sliderWeights(values, [True]*3, 0, 0.4))
        controls[0][0].slider.setValue.assert_not_called()
        controls[1][0].slider.setValue.assert_called_once_with(result[1])
        state._VertexInfluenceEditor__busyWithCallback = False
        state._VertexInfluenceEditor__sliders = controls[:1]
        update = VertexInfluenceEditor._VertexInfluenceEditor__updateWeights
        update(state, 0, 0.5)
        self.assertFalse(state._VertexInfluenceEditor__busyWithCallback)
        state._VertexInfluenceEditor__sliders = controls
        state.uniformNormalisation = Mock(side_effect=ValueError('injected calculation failure'))
        with self.assertRaisesRegex(ValueError, 'injected calculation failure'):
            update(state, 0, 0.5)
        self.assertFalse(state._VertexInfluenceEditor__busyWithCallback)

    def test_editor_final_zero_row_does_not_drop_an_earlier_edit(self):
        other, other_skin = self.fixture.create(different=True)
        shared.setWeights(other, [0.0]*18)
        data = [[0.5, 0.25, 0.25], [0.0, 0.0]]
        state = SimpleNamespace(weightTable=SimpleNamespace(_data=data, totalNotNormalized=set(), overMaxInfDict={}),
            rowsToUpdate={0, 1}, cellDict={0: [0], 1: [0]},
            meshWeights={self.mesh: [[1, 0, 0]]*9, other: [[0, 0]]*9},
            jointIndexList={self.mesh: [0, 1, 2], other: [0, 1]}, vtxDataDict={},
            vtxlockedData={}, nodeVtxIndexList={}, meshSkinClusters={self.mesh: self.skin, other: other_skin},
            refreshTable=Mock())
        for row, mesh, width in ((0, self.mesh, 3), (1, other, 2)):
            vertex = mesh+'.vtx[0]'
            state.vtxDataDict[row] = [0, None, list(range(width)), [], list(range(width)), vertex, mesh]
            state.vtxlockedData[vertex] = []
            state.nodeVtxIndexList[vertex] = data[row]
        before = [snapshot(self.mesh, self.skin), snapshot(other, other_skin)]
        cmds.flushUndo()
        WeightEditorWindow.tryNormalizeWeights(state)
        self.assertEqual(snapshot(self.mesh, self.skin)['weights'][:3], [0.5, 0.25, 0.25])
        self.assertEqual(snapshot(other, other_skin), before[1])
        cmds.undo()
        self.assertEqual([snapshot(self.mesh, self.skin), snapshot(other, other_skin)], before)

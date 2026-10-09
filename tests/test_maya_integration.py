"""Real host checks; ordinary Python discovery reports environment skips."""
import os
import sys
import time
import unittest
from types import SimpleNamespace

READY = 'maya.standalone' in sys.modules

if READY:
    from maya import cmds
    READY = cmds.about(batch=True)

if READY:
    from maya.api import OpenMaya as om
    from SkinningTools.Maya.tools import shared, skinCluster, apiWeights
    from SkinningTools.UI.weightEditor.weightsTableModel import WeightsTableModel
    from SkinningTools.UI.qt_util import Qt
    from tests.maya_fixtures import SceneFixture, snapshot, write_raw, skin_data


@unittest.skipUnless(READY, 'Use a fresh mayapy process with tests/run_maya.py')
class MayaBaselineTests(unittest.TestCase):
    def setUp(self):
        self.fixture = SceneFixture()
        self.fixture.__enter__()
        self.addCleanup(self.fixture.__exit__, None, None, None)
        self.mesh, self.skin = self.fixture.create()

    def test_fixture_captures_sparse_mapping_locks_and_settings(self):
        other, skin = self.fixture.create(sparse=True)
        before = snapshot(other, skin)
        self.assertNotEqual(before['logical_indices'], before['physical_indices'])
        cmds.setAttr(before['influences'][0] + '.liw', True)
        self.assertTrue(snapshot(other, skin)['locks'][0])
        self.assertEqual(len(before['weights']), 27)
        self.assertEqual(before['settings']['normalizeWeights'], 0)

    def test_fixture_under_over_zero_weights_and_different_meshes(self):
        other, skin = self.fixture.create(different=True)
        for total in (0.0, 0.5, 1.5):
            write_raw(other, skin, [v for _ in range(9) for v in (total / 2, total / 2)])
            self.assertAlmostEqual(sum(snapshot(other, skin)['weights'][:2]), total)
        self.assertEqual(len(snapshot(other, skin)['influences']), 2)
        self.assertEqual(len(snapshot(self.mesh, self.skin)['influences']), 3)

    def test_fixture_boundary_and_isolated_vertices(self):
        mesh = self.fixture.isolated()
        selection = om.MSelectionList()
        selection.add(mesh)
        iterator = om.MItMeshVertex(selection.getDagPath(0))
        self.assertTrue(iterator.onBoundary())
        iterator.setIndex(3)
        self.assertEqual(list(iterator.getConnectedVertices()), [])

    def test_missing_skincluster_returns_none_silently(self):
        mesh = cmds.polyCube(name=self.fixture.namespace + ':unskinned')[0]
        self.assertIsNone(shared.skinCluster(mesh, True))
        with self.assertRaises(RuntimeError):
            shared.getDagpath('nonexistent_reliability_skin')

    def test_fixture_rejects_invalid_dimensions_and_nonfinite_before_write(self):
        before = snapshot(self.mesh, self.skin)
        for weights in ([0.0], [float('nan')] * 27, [float('inf')] * 27):
            with self.assertRaises(ValueError):
                write_raw(self.mesh, self.skin, weights)
            self.assertEqual(snapshot(self.mesh, self.skin), before)

    def test_fixture_cleanup_after_failure_preserves_existing_nodes_and_selection(self):
        before = set(cmds.ls(long=True))
        cmds.select(self.mesh, replace=True)
        selection = cmds.ls(selection=True, long=True)
        with self.assertRaisesRegex(ValueError, 'injected fixture failure'):
            with SceneFixture() as nested:
                nested.create(sparse=True)
                raise ValueError('injected fixture failure')
        self.assertEqual(set(cmds.ls(long=True)), before)
        self.assertEqual(cmds.ls(selection=True, long=True), selection)

    def test_D001_real_call_swallows_nameerror(self):
        # The actual decorated function returns None; undecorated call exposes it.
        self.assertIsNone(skinCluster.forceCompareInfluences([self.mesh]))
        with self.assertRaisesRegex(NameError, 'skinClusterName'):
            skinCluster.forceCompareInfluences.__wrapped__([self.mesh])

    def test_D003_direct_write_has_no_undo_record(self):
        before = snapshot(self.mesh, self.skin)
        weights = [v for _ in range(9) for v in (0.25, 0.75, 0.0)]
        cmds.flushUndo()
        shared.setWeights(self.mesh, om.MDoubleArray(weights))
        self.assertEqual(snapshot(self.mesh, self.skin)['weights'], weights)
        self.assertNotEqual(before['weights'], weights)
        self.assertTrue(cmds.undoInfo(query=True, undoQueueEmpty=True))

    def test_D004_physical_indices_work_with_sparse_logical_indices(self):
        mesh, skin = self.fixture.create(sparse=True)
        before = snapshot(mesh, skin)
        self.assertNotEqual(before['logical_indices'], list(range(3)))
        weights = [v for _ in range(9) for v in (0.125, 0.25, 0.625)]
        shared.setWeights(mesh, om.MDoubleArray(weights))
        after = snapshot(mesh, skin)
        self.assertEqual(after['weights'], weights)
        self.assertEqual(after['logical_indices'], before['logical_indices'])

    def test_D009_real_selection_leaks_between_meshes(self):
        other, skin = self.fixture.create(different=True)
        cmds.select([self.mesh + '.vtx[0]', other + '.vtx[7]'], replace=True)
        reader = apiWeights.ApiWeights()
        self.assertEqual(sorted(reader.selectedVertIds(self.mesh)), [0, 7])
        self.assertEqual(sorted(reader.selectedVertIds(other)), [0, 7])

    def test_D014_list_input_constructor_fails_before_write(self):
        before = snapshot(self.mesh, self.skin)
        with self.assertRaisesRegex(TypeError, 'No matching constructor'):
            shared.setWeights(self.mesh, [0.0] * 27)
        self.assertEqual(snapshot(self.mesh, self.skin), before)

    def test_D011_real_qt_signal_arguments(self):
        window = SimpleNamespace(vtxDataDict={0: [None]*6 + [self.mesh]}, jointIndexList={self.mesh: [0, 1]})
        model = WeightsTableModel([[0.25, 0.75]], window=window)
        delivered = []
        model.dataChanged.connect(lambda first, last, roles: delivered.append((first, last, roles)))
        self.assertTrue(model.setData((0, 0), 0.5, Qt.EditRole))
        self.assertEqual(model._data[0][0], 0.5)
        self.assertEqual(len(delivered), 1)
        print('D011 delivered indices:', delivered[0][0], delivered[0][1])
        self.assertFalse(delivered[0][0].isValid())
        self.assertFalse(delivered[0][1].isValid())

    def test_skin_editor_exact_repeated_undo_redo_and_unrelated_mesh(self):
        plugin = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Maya', 'plugin', 'SkinEditPlugin.py')
        cmds.loadPlugin(plugin, quiet=True)
        other, other_skin = self.fixture.create(different=True)
        unrelated = snapshot(other, other_skin)
        before = snapshot(self.mesh, self.skin)
        new = [0.25, 0.75, 0.0, 0.5, 0.5, 0.0]
        original = before['weights'][:6]
        cmds.flushUndo()
        cmds.SkinEditor(self.mesh, self.skin, vid=[0, 1], jid=[0, 1, 2], nw=new, ow=original)
        after = snapshot(self.mesh, self.skin)
        self.assertEqual(after['weights'][:6], new)
        for _ in range(3):
            cmds.undo()
            self.assertEqual(snapshot(self.mesh, self.skin), before)
            cmds.redo()
            self.assertEqual(snapshot(self.mesh, self.skin), after)
        self.assertEqual(snapshot(other, other_skin), unrelated)

    def test_shared_bulk_read_write_timing(self):
        for subdivisions in (2, 10, 32):
            mesh, skin = self.fixture.create(subdivisions=subdivisions)
            before = snapshot(mesh, skin)
            start = time.perf_counter()
            weights = shared.getWeights(mesh)
            shared.setWeights(mesh, weights)
            elapsed = time.perf_counter() - start
            self.assertEqual(snapshot(mesh, skin), before)
            print('Bulk get/set: %d vertices, %d influences, %.6f seconds' %
                  ((subdivisions+1)**2, len(before['influences']), elapsed))


if __name__ == '__main__':
    unittest.main()

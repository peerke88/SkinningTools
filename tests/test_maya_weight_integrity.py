"""M2 desired contract; each test runs only in disposable standalone Maya."""
import gc
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

READY = 'maya.standalone' in sys.modules
if READY:
    from maya import cmds
    READY = cmds.about(batch=True)
if READY:
    from maya.api import OpenMaya as om
    from SkinningTools.Maya.tools import shared
    from tests.maya_fixtures import SceneFixture, snapshot, write_raw


@unittest.skipUnless(READY, 'Use tests/run_maya.py in fresh mayapy')
class WeightIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.fixture = SceneFixture()
        self.fixture.__enter__()
        self.addCleanup(self.fixture.__exit__, None, None, None)
        self.mesh, self.skin = self.fixture.create(sparse=True)
        self.other, self.other_skin = self.fixture.create(different=True)
        write_raw(self.mesh, self.skin, [v for _ in range(9) for v in (0.2, 0.3, 0.1)])
        self.before = self.snapshots()

    def snapshots(self):
        return [snapshot(self.mesh, self.skin), snapshot(self.other, self.other_skin)]

    def test_bulk_list_write_exact_undo_redo_of_unnormalized_original(self):
        cmds.flushUndo()
        shared.setWeights(self.mesh, [v for _ in range(9) for v in (0.25, 0.25, 0.5)])
        after = self.snapshots()
        self.assertEqual(after[0]['weights'][:3], [0.25, 0.25, 0.5])
        for _ in range(3):
            cmds.undo()
            self.assertEqual(self.snapshots(), self.before)
            cmds.redo()
            self.assertEqual(self.snapshots(), after)

    def test_batch_two_meshes_single_undo_entry(self):
        cmds.flushUndo()
        shared.setWeightsBatch([
            {'mesh': self.mesh, 'weights': [v for _ in range(9) for v in (0.5, 0.25, 0.25)]},
            {'mesh': self.other, 'weights': [v for _ in range(9) for v in (0.75, 0.25)]}])
        after = self.snapshots()
        self.assertNotEqual(after[1]['weights'], self.before[1]['weights'])
        cmds.undo()
        self.assertEqual(self.snapshots(), self.before)
        self.assertTrue(cmds.undoInfo(query=True, undoQueueEmpty=True))
        cmds.redo()
        self.assertEqual(self.snapshots(), after)

    def test_api_full_mesh_setter_uses_same_command_and_validates_cluster(self):
        from SkinningTools.Maya import api
        cmds.flushUndo()
        api.setSkinWeights(self.mesh, self.skin, [0.1] * 27)
        after = self.snapshots()
        self.assertEqual(after[0]['weights'], [0.1] * 27)
        cmds.undo()
        self.assertEqual(self.snapshots(), self.before)
        cmds.redo()
        self.assertEqual(self.snapshots(), after)
        with self.assertRaisesRegex(ValueError, 'supplied skinCluster'):
            api.setSkinWeights(self.mesh, self.other_skin, [0.0] * 27)
        self.assertEqual(self.snapshots(), after)

    def test_batch_invalid_second_mesh_has_no_partial_write(self):
        cmds.flushUndo()
        with self.assertRaises((ValueError, RuntimeError)):
            shared.setWeightsBatch([
                {'mesh': self.mesh, 'weights': [0.0] * 27},
                {'mesh': self.other, 'weights': [0.0]}])
        self.assertEqual(self.snapshots(), self.before)
        self.assertTrue(cmds.undoInfo(query=True, undoQueueEmpty=True))

    def test_invalid_values_rejected_before_mutation(self):
        for value in (float('nan'), float('inf'), -0.1, 1.1):
            with self.assertRaises((ValueError, RuntimeError)):
                shared.setWeights(self.mesh, [value] * 27)
            self.assertEqual(self.snapshots(), self.before)

    def test_locked_sparse_influence_preserved_and_unlocked_normalized(self):
        cmds.setAttr(self.before[0]['influences'][1] + '.liw', True)
        before = self.snapshots()
        shared.setWeights(self.mesh, [v for _ in range(9) for v in (1.0, 0.0, 0.0)])
        after = self.snapshots()
        self.assertEqual(after[0]['weights'][:3], [0.7, 0.3, 0.0])
        self.assertEqual(after[0]['locks'], before[0]['locks'])
        self.assertEqual(after[0]['settings'], before[0]['settings'])
        cmds.undo()
        self.assertEqual(self.snapshots(), before)
        cmds.redo()
        self.assertEqual(self.snapshots(), after)

    def test_command_partial_reordered_vertices_and_physical_influences(self):
        cmds.loadPlugin(os.path.join(shared.os.path.dirname(shared.__file__), '..', 'plugin', 'SkinEditPlugin.py'), quiet=True)
        cmds.SkinEditor(self.mesh, self.skin, vid=[4, 0], jid=[2, 0, 1],
                        nw=[0.5, 0.25, 0.25, 0.25, 0.5, 0.25], ow=[0.0] * 6, n=False)
        after = self.snapshots()
        self.assertEqual(after[0]['weights'][:3], [0.5, 0.25, 0.25])
        self.assertEqual(after[0]['weights'][12:15], [0.25, 0.25, 0.5])
        cmds.undo()
        self.assertEqual(self.snapshots(), self.before)
        cmds.redo()
        self.assertEqual(self.snapshots(), after)

    def test_D019_closest_point_remap_rejects_list_target_positions(self):
        from SkinningTools.UI.utils import remapClosestPoints
        with self.assertRaisesRegex(TypeError, 'unhashable'):
            remapClosestPoints([[0.0, 0.0, 0.0]], [[0.0, 0.0, 0.0]], 1)

    def test_D020_import_sampling_includes_invalid_upper_vertex(self):
        from SkinningTools.Maya.tools import weightsManager
        mesh = cmds.ls(self.mesh, long=True)[0]
        payload = {'vertIds': {mesh: list(range(9))},
                   'vertPos': {mesh: [cmds.pointPosition(mesh + '.vtx[%i]' % i, world=True)
                                      for i in range(9)]}}
        with patch.object(weightsManager, 'randint', return_value=9) as sample:
            with self.assertRaises(IndexError):
                weightsManager.WeightsManager().checkNeedsClosestVtxSearch(payload, mesh, mesh)
            sample.assert_called_once_with(0, 9)

    def test_weight_file_import_uses_atomic_batch_for_existing_clusters(self):
        from SkinningTools.Maya.tools import weightsManager
        cmds.select([self.mesh, self.other], replace=True)
        manager = weightsManager.WeightsManager()
        payload = manager.gatherData()
        mesh, other = [cmds.ls(node, long=True)[0] for node in (self.mesh, self.other)]
        # Isolate the existing-cluster write boundary from geometry matching.
        # D019/D020 separately characterize existing closest-search defects.
        payload['weights'][mesh] = [[0.5, 0.25, 0.25] for _ in range(9)]
        payload['weights'][other] = [[0.75, 0.25] for _ in range(9)]
        before = self.snapshots()
        with tempfile.TemporaryDirectory(prefix='skinningtools_m2_') as directory:
            path = os.path.join(directory, 'weights.json')
            with open(path, 'w') as stream:
                json.dump(payload, stream)
            cmds.flushUndo()
            with patch.object(manager, 'checkNeedsClosestVtxSearch', return_value=False):
                manager.importData(path)
            after = self.snapshots()
            self.assertEqual(after[0]['weights'][:3], [0.5, 0.25, 0.25])
            self.assertEqual(after[1]['weights'][:2], [0.75, 0.25])
            cmds.undo()
            self.assertEqual(self.snapshots(), before)
            self.assertTrue(cmds.undoInfo(query=True, undoQueueEmpty=True))
            cmds.redo()
            self.assertEqual(self.snapshots(), after)
            payload['weights'][mesh] = [[0.25, 0.25, 0.5] for _ in range(9)]
            payload['weights'][other][0][0] = float('nan')
            with open(path, 'w') as stream:
                json.dump(payload, stream)
            with patch.object(manager, 'checkNeedsClosestVtxSearch', return_value=False):
                with self.assertRaises(ValueError):
                    manager.importData(path)
            self.assertEqual(self.snapshots(), after)

    def test_write_failure_after_second_mutation_rolls_back_both(self):
        # Load through the production boundary, then patch the registered class.
        cmds.setAttr(self.skin + '.normalizeWeights', 1)
        cmds.setAttr(self.skin + '.maintainMaxInfluences', True)
        shared.setWeights(self.mesh, om.MDoubleArray(self.before[0]['weights']))
        before = self.snapshots()
        command_class = next(value for value in gc.get_objects()
                             if isinstance(value, type) and value.__name__ == 'SkinEditClass'
                             and not value.__module__.startswith('SkinningTools.'))
        original = command_class._write
        calls = []
        def fail_after_write(command, operation, weights):
            original(command, operation, weights)
            calls.append(operation)
            if len(calls) == 2:
                raise RuntimeError('injected failure after second mutation')
        cmds.flushUndo()
        with patch.object(command_class, '_write', fail_after_write):
            with self.assertRaisesRegex(RuntimeError, 'injected failure after second mutation'):
                shared.setWeightsBatch([
                    {'mesh': self.mesh, 'weights': [v for _ in range(9) for v in (0.5, 0.25, 0.25)]},
                    {'mesh': self.other, 'weights': [v for _ in range(9) for v in (0.5, 0.5)]}])
        self.assertEqual(self.snapshots(), before)
        self.assertTrue(cmds.undoInfo(query=True, undoQueueEmpty=True))

    def test_explicit_normalization_off_and_zero_weights_all_scene_modes(self):
        shared.setWeights(self.mesh, [0.0] * 27)
        self.assertEqual(snapshot(self.mesh, self.skin)['weights'], [0.0] * 27)
        for mode in (0, 1, 2):
            cmds.setAttr(self.skin + '.normalizeWeights', mode)
            cmds.setAttr(self.skin + '.maintainMaxInfluences', True)
            cmds.setAttr(self.skin + '.maxInfluences', 2)
            before = self.snapshots()
            shared.setWeightsBatch([{'mesh': self.mesh, 'normalize': False,
                                    'weights': [v for _ in range(9) for v in (0.2, 0.2, 0.2)]}])
            after = self.snapshots()
            self.assertEqual(after[0]['weights'][:3], [0.2, 0.2, 0.2])
            self.assertEqual(after[0]['settings'], before[0]['settings'])
            cmds.undo()
            self.assertEqual(self.snapshots(), before)
            cmds.redo()
            self.assertEqual(self.snapshots(), after)

    def test_mismatched_cluster_duplicate_vertices_and_invalid_physical_index(self):
        shared.setWeights(self.mesh, [v for _ in range(9) for v in (0.5, 0.25, 0.25)])
        before = self.snapshots()
        requests = [
            {'mesh': self.mesh, 'skinCluster': self.other_skin, 'vertices': [0],
             'influences': [0, 1], 'weights': [0.5, 0.5]},
            {'mesh': self.mesh, 'skinCluster': self.skin, 'vertices': [0, 0],
             'influences': [0, 1, 2], 'weights': [0.0] * 6},
            {'mesh': self.mesh, 'skinCluster': self.skin, 'vertices': [99],
             'influences': [0, 1, 2], 'weights': [0.0] * 3},
            {'mesh': self.mesh, 'skinCluster': self.skin, 'vertices': [0],
             'influences': [0, 1, 3], 'weights': [0.0] * 3}]
        for request in requests:
            with self.assertRaises(RuntimeError):
                shared.setWeightsBatch([request])
            self.assertEqual(self.snapshots(), before)
        valid = {'mesh': self.mesh, 'skinCluster': self.skin, 'vertices': [0],
                 'influences': [0, 1, 2], 'weights': [0.5, 0.25, 0.25]}
        with self.assertRaisesRegex(RuntimeError, 'overlapping vertices'):
            shared.setWeightsBatch([valid, valid])
        self.assertEqual(self.snapshots(), before)

    def test_two_consecutive_operations_restore_intermediate_and_original_states(self):
        cmds.flushUndo()
        shared.setWeights(self.mesh, [v for _ in range(9) for v in (0.5, 0.25, 0.25)])
        first = self.snapshots()
        shared.setWeights(self.mesh, [v for _ in range(9) for v in (0.25, 0.5, 0.25)])
        second = self.snapshots()
        cmds.undo()
        self.assertEqual(self.snapshots(), first)
        cmds.undo()
        self.assertEqual(self.snapshots(), self.before)
        cmds.redo()
        self.assertEqual(self.snapshots(), first)
        cmds.redo()
        self.assertEqual(self.snapshots(), second)

    def test_undo_failure_after_mutation_restores_pre_undo_weights(self):
        shared.setWeightsBatch([
            {'mesh': self.mesh, 'weights': [v for _ in range(9) for v in (0.5, 0.25, 0.25)]},
            {'mesh': self.other, 'weights': [v for _ in range(9) for v in (0.5, 0.5)]}])
        before = self.snapshots()
        command_class = next(value for value in gc.get_objects()
                             if isinstance(value, type) and value.__name__ == 'SkinEditClass'
                             and not value.__module__.startswith('SkinningTools.'))
        original = command_class._write
        calls = []
        def fail_after_write(command, operation, weights):
            original(command, operation, weights)
            calls.append(operation)
            if len(calls) == 2:
                raise RuntimeError('injected undo failure')
        errors = []
        callback = om.MCommandMessage.addCommandOutputCallback(lambda *args: errors.append(args[0]))
        try:
            with patch.object(command_class, '_write', fail_after_write):
                cmds.undo()
        finally:
            om.MMessage.removeCallback(callback)
        self.assertTrue(any('injected undo failure' in message for message in errors))
        self.assertEqual(self.snapshots(), before)


if __name__ == '__main__':
    unittest.main()

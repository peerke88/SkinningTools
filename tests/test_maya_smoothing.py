"""M3 mathematical reference and disposable real-host brush/native checks."""
import math
import os
import sys
import time
import unittest

READY = 'maya.standalone' in sys.modules
if READY:
    from maya import cmds
    READY = cmds.about(batch=True)
if READY:
    from maya.api import OpenMaya as om
    from SkinningTools.Maya.plugin.averageWeightPlugin import AverageWghtCtx
    from SkinningTools.Maya.tools import shared
    from tests.maya_fixtures import SceneFixture, snapshot, write_raw, skin_data


def reference(original, neighbors, strength, normalize=False, maximum=0, locks=None):
    """Independent row-oriented reference; ties keep lower physical positions."""
    if strength == 0 or not neighbors:
        return list(original)
    locks = locks or [False] * len(original)
    result = []
    for column, value in enumerate(original):
        average = sum(row[column] for row in neighbors) / len(neighbors)
        result.append(value if locks[column] else value * (1-strength) + average * strength)
    if maximum:
        locked_count = sum(locked and value > 0 for locked, value in zip(locks, result))
        if locked_count > maximum:
            raise ValueError('Locked influences exceed limit')
        order = sorted([i for i in range(len(result)) if not locks[i]],
                       key=lambda i: (-result[i], i))
        for column in order[maximum-locked_count:]:
            result[column] = 0.0
    if normalize:
        budget = 1-sum(value for value, locked in zip(result, locks) if locked)
        total = sum(value for value, locked in zip(result, locks) if not locked)
        if budget < -1e-6 or (not total and 1e-6 < budget < 1 and any(not v for v in locks)):
            raise ValueError('Invalid normalization budget')
        if total:
            for column in range(len(result)):
                if not locks[column]:
                    result[column] *= max(0, budget)/total
    return result


@unittest.skipUnless(READY, 'Use fresh mayapy')
class PythonSmoothingTests(unittest.TestCase):
    def setUp(self):
        self.fixture = SceneFixture()
        self.fixture.__enter__()
        self.addCleanup(self.fixture.__exit__, None, None, None)
        self.mesh, self.skin = self.fixture.create(sparse=True)
        self.rows = [[0.1 + (i % 3)*0.1, 0.2, 0.6-(i % 3)*0.1] for i in range(9)]
        write_raw(self.mesh, self.skin, [w for row in self.rows for w in row])

    def neighbors(self, vertex):
        fn, dag, comp = skin_data(self.mesh, self.skin)
        iterator = om.MItMeshVertex(dag)
        iterator.setIndex(vertex)
        return [self.rows[i] for i in iterator.getConnectedVertices()]

    def assertRowsClose(self, actual, expected):
        self.assertEqual(len(actual), len(expected))
        for left, right in zip(actual, expected):
            self.assertAlmostEqual(left, right, places=12)

    def test_python_math_reference_strength_modes_limits_locks_and_ties(self):
        context = AverageWghtCtx()
        for locks in ([False]*3, [False, True, False]):
            context.locked = locks
            for strength in (0.0, 0.5, 1.0):
                for mode in (0, 1, 2):
                    for maximum in (0, 2, 3):
                        context.normalize = mode
                        context.maintainMaxInfl = bool(maximum)
                        context.maxInfluences = maximum
                        neighbors = [[0.4, 0.2, 0.4], [0.2, 0.2, 0.6]]
                        actual, indices = context.calcWeights(strength, self.rows[0],
                            sum(neighbors, []), [0, 1, 2], 2)
                        expected = reference(self.rows[0], neighbors, strength, mode == 1, maximum, locks)
                        self.assertRowsClose(actual, expected)
                        self.assertEqual(list(indices), [0, 1, 2])
        context.locked = [False]*3
        context.normalize, context.maintainMaxInfl, context.maxInfluences = 0, True, 1
        self.assertEqual(context.calcWeights(1, [0.2]*3, [0.5, 0.5, 0], [2, 5, 8], 1)[0], [0.5, 0, 0])

    def load_python_brush(self):
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Maya', 'plugin', 'averageWeightPlugin.py')
        if not cmds.pluginInfo(path, query=True, loaded=True):
            cmds.loadPlugin(path, quiet=True)
        cmds.paintAverageWghtCtxInitialize(self.mesh)

    def test_python_vertex_zero_raw_original_and_cached_redo(self):
        self.load_python_brush()
        cmds.setAttr(self.skin + '.normalizeWeights', 1)
        before = snapshot(self.mesh, self.skin)
        cmds.flushUndo()
        cmds.paintAverageWghtCtxUpdate(0, 0, 0.5)
        after = snapshot(self.mesh, self.skin)
        self.assertRowsClose(after['weights'][:3], reference(self.rows[0], self.neighbors(0), 0.5, True))
        for unused in range(3):
            cmds.undo()
            self.assertEqual(snapshot(self.mesh, self.skin), before)
            cmds.redo()
            self.assertEqual(snapshot(self.mesh, self.skin), after)

    def test_python_zero_strength_and_isolated_vertex_preserve_exact_rows(self):
        self.load_python_brush()
        before = snapshot(self.mesh, self.skin)
        cmds.paintAverageWghtCtxUpdate(0, 0, 0.0)
        self.assertEqual(snapshot(self.mesh, self.skin), before)
        cmds.undo()
        cmds.redo()
        self.assertEqual(snapshot(self.mesh, self.skin), before)
        isolated = self.fixture.isolated()
        joints = self.fixture.joints[:3]
        skin = cmds.skinCluster(joints, isolated, toSelectedBones=True, normalizeWeights=0)[0]
        write_raw(isolated, skin, [v for unused in range(4) for v in (0.2, 0.3, 0.1)])
        cmds.paintAverageWghtCtxInitialize(isolated)
        original = snapshot(isolated, skin)
        cmds.paintAverageWghtCtxUpdate(0, 3, 1.0)
        self.assertEqual(snapshot(isolated, skin), original)

    def test_python_cached_redo_survives_context_switch(self):
        other, other_skin = self.fixture.create(different=True)
        self.load_python_brush()
        before = snapshot(self.mesh, self.skin)
        other_before = snapshot(other, other_skin)
        cmds.flushUndo()
        cmds.paintAverageWghtCtxUpdate(0, 0, 0.5)
        after = snapshot(self.mesh, self.skin)
        cmds.paintAverageWghtCtxInitialize(other)
        cmds.undo()
        self.assertEqual(snapshot(self.mesh, self.skin), before)
        cmds.redo()
        self.assertEqual(snapshot(self.mesh, self.skin), after)
        self.assertEqual(snapshot(other, other_skin), other_before)

    def test_python_invalid_strength_index_and_lock_budget_are_failure_safe(self):
        self.load_python_brush()
        before = snapshot(self.mesh, self.skin)
        for index, value in ((-1, 0.5), (9, 0.5), (0, -0.1), (0, 1.1), (0, float('nan'))):
            with self.assertRaises(RuntimeError):
                cmds.paintAverageWghtCtxUpdate(0, index, value)
            self.assertEqual(snapshot(self.mesh, self.skin), before)
        for joint in before['influences'][:2]:
            cmds.setAttr(joint + '.liw', True)
        cmds.setAttr(self.skin + '.maintainMaxInfluences', True)
        cmds.setAttr(self.skin + '.maxInfluences', 1)
        before = snapshot(self.mesh, self.skin)
        with self.assertRaises(RuntimeError):
            cmds.paintAverageWghtCtxUpdate(0, 0, 0.5)
        self.assertEqual(snapshot(self.mesh, self.skin), before)


@unittest.skipUnless(READY and os.environ.get('SKINNINGTOOLS_NATIVE_TEST_PLUGIN'),
                     'Native regressions require an explicit isolated build')
class NativeSetterTests(PythonSmoothingTests):
    # Inherit fixture/reference helpers, but not the Python test methods.
    test_python_math_reference_strength_modes_limits_locks_and_ties = None
    test_python_vertex_zero_raw_original_and_cached_redo = None
    test_python_zero_strength_and_isolated_vertex_preserve_exact_rows = None
    test_python_invalid_strength_index_and_lock_budget_are_failure_safe = None
    test_python_cached_redo_survives_context_switch = None

    def setUp(self):
        super(NativeSetterTests, self).setUp()
        self.plugin = os.path.abspath(os.environ['SKINNINGTOOLS_NATIVE_TEST_PLUGIN'])
        if not cmds.pluginInfo(self.plugin, query=True, loaded=True):
            cmds.loadPlugin(self.plugin, quiet=True)

    def test_native_distinct_multiuse_values_sparse_mapping_exact_undo_redo(self):
        values = [v for unused in range(9) for v in (0.125, 0.25, 0.5)]
        for mode in (0, 1, 2):
            cmds.setAttr(self.skin + '.normalizeWeights', mode)
            cmds.setAttr(self.skin + '.maintainMaxInfluences', True)
            cmds.setAttr(self.skin + '.maxInfluences', 1)
            before = snapshot(self.mesh, self.skin)
            cmds.SkinWeights(self.mesh, self.skin, nwt=values)
            after = snapshot(self.mesh, self.skin)
            self.assertEqual(after['weights'], values)
            self.assertEqual(after['settings'], before['settings'])
            self.assertEqual(list(cmds.SkinWeights(self.mesh, self.skin, q=True)), values)
            for unused in range(3):
                cmds.undo()
                self.assertEqual(snapshot(self.mesh, self.skin), before)
                cmds.redo()
                self.assertEqual(snapshot(self.mesh, self.skin), after)
            cmds.undo()

    def test_native_parser_contiguous_distinct_values(self):
        mesh, skin = self.fixture.create()
        values = [value for unused in range(9) for value in (0.125, 0.25, 0.5)]
        cmds.SkinWeights(mesh, skin, nwt=values)
        self.assertEqual(snapshot(mesh, skin)['weights'], values)

    def test_native_setter_invalid_arguments_leave_weights_and_queue_unchanged(self):
        before = snapshot(self.mesh, self.skin)
        cmds.flushUndo()
        for values in ([], [0.1], [0.1]*26, [0.1]*28, [float('nan')]*27,
                       [float('inf')]*27, [-0.1]*27, [1.1]*27):
            with self.assertRaises(RuntimeError):
                cmds.SkinWeights(self.mesh, self.skin, nwt=values)
            self.assertEqual(snapshot(self.mesh, self.skin), before)
            self.assertTrue(cmds.undoInfo(query=True, undoQueueEmpty=True))
        other, other_skin = self.fixture.create(different=True)
        before = snapshot(self.mesh, self.skin)
        with self.assertRaises(RuntimeError):
            cmds.SkinWeights(self.mesh, other_skin, nwt=[0.1]*27)
        self.assertEqual(snapshot(self.mesh, self.skin), before)

    def test_native_setter_locked_influence_and_locked_setting(self):
        joint = snapshot(self.mesh, self.skin)['influences'][1]
        cmds.setAttr(joint + '.liw', True)
        before = snapshot(self.mesh, self.skin)
        cmds.SkinWeights(self.mesh, self.skin, nwt=[0.1]*27)
        after = snapshot(self.mesh, self.skin)
        self.assertEqual(after['weights'][1::3], before['weights'][1::3])
        cmds.undo()
        self.assertEqual(snapshot(self.mesh, self.skin), before)
        cmds.setAttr(self.skin + '.normalizeWeights', 1)
        cmds.setAttr(self.skin + '.normalizeWeights', lock=True)
        before = snapshot(self.mesh, self.skin)
        with self.assertRaises(RuntimeError):
            cmds.SkinWeights(self.mesh, self.skin, nwt=[0.1]*27)
        self.assertEqual(snapshot(self.mesh, self.skin), before)


@unittest.skipUnless(READY and os.environ.get('SKINNINGTOOLS_NATIVE_TEST_PLUGIN'), 'Explicit isolated native build required')
class NativeSmoothingTests(PythonSmoothingTests):
    test_python_math_reference_strength_modes_limits_locks_and_ties = None
    test_python_vertex_zero_raw_original_and_cached_redo = None
    test_python_zero_strength_and_isolated_vertex_preserve_exact_rows = None
    test_python_invalid_strength_index_and_lock_budget_are_failure_safe = None
    test_python_cached_redo_survives_context_switch = None

    def setUp(self):
        super(NativeSmoothingTests, self).setUp()
        plugin = os.path.abspath(os.environ['SKINNINGTOOLS_NATIVE_TEST_PLUGIN'])
        if not cmds.pluginInfo(plugin, query=True, loaded=True):
            cmds.loadPlugin(plugin, quiet=True)
        if 'AverageVtxWeight' not in cmds.pluginInfo(plugin, query=True, command=True):
            self.skipTest('Setter-only duplicate plugin')

    def test_native_two_vertices_match_reference_python_and_per_vertex_limits(self):
        original = snapshot(self.mesh, self.skin)['weights']
        for mode in (0, 1, 2):
            for maximum in (0, 1, 2, 3):
                for strength in (0.0, 0.5, 1.0):
                    shared.setWeightsBatch([{'mesh': self.mesh, 'weights': original, 'normalize': False}])
                    cmds.setAttr(self.skin + '.normalizeWeights', mode)
                    cmds.setAttr(self.skin + '.maintainMaxInfluences', bool(maximum))
                    cmds.setAttr(self.skin + '.maxInfluences', maximum or 3)
                    before = snapshot(self.mesh, self.skin)
                    expected = list(original)
                    context = AverageWghtCtx()
                    context.normalize, context.maintainMaxInfl, context.maxInfluences = mode, bool(maximum), maximum
                    for vertex in (0, 8):
                        neighbors = self.neighbors(vertex)
                        row = reference(self.rows[vertex], neighbors, strength, mode == 1, maximum)
                        python, unused = context.calcWeights(strength, self.rows[vertex], sum(neighbors, []), [0, 1, 2], len(neighbors))
                        self.assertRowsClose(row, python)
                        expected[vertex*3:vertex*3+3] = row
                    cmds.AverageVtxWeight([self.mesh+'.vtx[8]', self.mesh+'.vtx[0]'], sc=self.skin, wt=strength)
                    after = snapshot(self.mesh, self.skin)
                    self.assertRowsClose(after['weights'], expected)
                    self.assertEqual(after['settings'], before['settings'])
                    for unused in range(3):
                        cmds.undo()
                        self.assertEqual(snapshot(self.mesh, self.skin), before)
                        cmds.redo()
                        self.assertEqual(snapshot(self.mesh, self.skin), after)

    def test_native_locks_preserved_explicit_normalization_and_isolated_vertex(self):
        joint = snapshot(self.mesh, self.skin)['influences'][1]
        cmds.setAttr(joint + '.liw', True)
        cmds.setAttr(self.skin + '.normalizeWeights', 1)
        before = snapshot(self.mesh, self.skin)
        cmds.AverageVtxWeight(self.mesh+'.vtx[0:1]', sc=self.skin, wt=0.5, n=False)
        after = snapshot(self.mesh, self.skin)
        self.assertEqual(after['weights'][1::3], before['weights'][1::3])
        self.assertRowsClose(after['weights'][:3], reference(self.rows[0], self.neighbors(0), 0.5, False, locks=[False, True, False]))
        cmds.undo()
        self.assertEqual(snapshot(self.mesh, self.skin), before)
        isolated = self.fixture.isolated()
        skin = cmds.skinCluster(self.fixture.joints[:3], isolated, toSelectedBones=True, normalizeWeights=0)[0]
        write_raw(isolated, skin, [v for unused in range(4) for v in (0.2, 0.3, 0.1)])
        before = snapshot(isolated, skin)
        cmds.AverageVtxWeight(isolated+'.vtx[3]', sc=skin, wt=1.0)
        self.assertEqual(snapshot(isolated, skin), before)

    def test_native_invalid_strength_components_cluster_and_lock_budget(self):
        other, other_skin = self.fixture.create(different=True)
        before = snapshot(self.mesh, self.skin)
        cmds.flushUndo()
        for strength in (-0.1, 1.1, float('nan'), float('inf')):
            with self.assertRaises(RuntimeError):
                cmds.AverageVtxWeight(self.mesh+'.vtx[0]', sc=self.skin, wt=strength)
            self.assertEqual(snapshot(self.mesh, self.skin), before)
        for target, skin in ((self.mesh+'.e[0]', self.skin),
                             (self.mesh+'.vtx[0]', other_skin),
                             ([self.mesh+'.vtx[0]', other+'.vtx[0]'], self.skin)):
            with self.assertRaises(RuntimeError):
                cmds.AverageVtxWeight(target, sc=skin, wt=0.5)
            self.assertEqual(snapshot(self.mesh, self.skin), before)
        self.assertTrue(cmds.undoInfo(query=True, undoQueueEmpty=True))
        for joint in before['influences'][:2]:
            cmds.setAttr(joint+'.liw', True)
        cmds.setAttr(self.skin+'.maintainMaxInfluences', True)
        cmds.setAttr(self.skin+'.maxInfluences', 1)
        before = snapshot(self.mesh, self.skin)
        with self.assertRaises(RuntimeError):
            cmds.AverageVtxWeight(self.mesh+'.vtx[0]', sc=self.skin, wt=0.5)
        self.assertEqual(snapshot(self.mesh, self.skin), before)

    def test_native_object_and_default_selection_resolve_all_vertices(self):
        before = snapshot(self.mesh, self.skin)
        expected = sum([reference(row, self.neighbors(i), 0.5) for i, row in enumerate(self.rows)], [])
        cmds.AverageVtxWeight(self.mesh, sc=self.skin, wt=0.5, n=False)
        self.assertRowsClose(snapshot(self.mesh, self.skin)['weights'], expected)
        cmds.undo()
        self.assertEqual(snapshot(self.mesh, self.skin), before)
        cmds.select(self.mesh, replace=True)
        cmds.AverageVtxWeight(sc=self.skin, wt=0.5, n=False)
        self.assertRowsClose(snapshot(self.mesh, self.skin)['weights'], expected)

    def test_native_consecutive_edits_restore_intermediate_and_original(self):
        before = snapshot(self.mesh, self.skin)
        cmds.flushUndo()
        cmds.AverageVtxWeight(self.mesh+'.vtx[0]', sc=self.skin, wt=0.5)
        first = snapshot(self.mesh, self.skin)
        cmds.AverageVtxWeight(self.mesh+'.vtx[8]', sc=self.skin, wt=0.5)
        second = snapshot(self.mesh, self.skin)
        cmds.undo()
        self.assertEqual(snapshot(self.mesh, self.skin), first)
        cmds.undo()
        self.assertEqual(snapshot(self.mesh, self.skin), before)
        cmds.redo()
        self.assertEqual(snapshot(self.mesh, self.skin), first)
        cmds.redo()
        self.assertEqual(snapshot(self.mesh, self.skin), second)

    def test_native_bulk_smoothing_timing(self):
        for subdivisions in (2, 10, 32):
            mesh, skin = self.fixture.create(subdivisions=subdivisions)
            count = cmds.polyEvaluate(mesh, vertex=True)
            write_raw(mesh, skin, [v for i in range(count) for v in (i % 3 * 0.1, 0.3, 0.6-i % 3*0.1)])
            start = time.perf_counter()
            cmds.AverageVtxWeight(mesh+'.vtx[*]', sc=skin, wt=0.5, n=False)
            print('Native smoothing: %d vertices, %.6f seconds' % (count, time.perf_counter()-start))

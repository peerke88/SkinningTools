"""Installed baseline binary smoke checks, distinct from source build validation."""
import os
import sys
import unittest

READY = 'maya.standalone' in sys.modules
if READY:
    from maya import cmds
    READY = cmds.about(batch=True)

if READY:
    from tests.maya_fixtures import SceneFixture, snapshot, write_raw


@unittest.skipUnless(READY, 'Use tests/run_maya.py in fresh mayapy')
class NativeBaselineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        version = cmds.about(version=True)
        root = os.path.dirname(os.path.dirname(__file__))
        cls.plugin = os.environ.get('SKINNINGTOOLS_NATIVE_TEST_PLUGIN') or os.path.join(root, 'Maya', 'plugin', 'averageWeightPerryCpp',
                                 'comp', 'Maya' + version, 'plug-ins', 'skinCommands.mll')
        if sys.platform != 'win32' or not os.path.isfile(cls.plugin):
            raise unittest.SkipTest('No matching bundled Windows native plugin: ' + cls.plugin)
        # An installed binary that fails to load is an error, not a hidden skip.
        cmds.loadPlugin(cls.plugin, quiet=True)
        print('Native binary:', cls.plugin)
        print('Registered commands:', cmds.pluginInfo(cls.plugin, query=True, command=True))

    def setUp(self):
        self.fixture = SceneFixture()
        self.fixture.__enter__()
        self.addCleanup(self.fixture.__exit__, None, None, None)
        self.mesh, self.skin = self.fixture.create()

    def test_native_query_matches_api_for_contiguous_influences(self):
        self.assertEqual(list(cmds.SkinWeights(self.mesh, self.skin, query=True)),
                         snapshot(self.mesh, self.skin)['weights'])

    def test_native_average_single_vertex_strength_one_undo_redo(self):
        if 'AverageVtxWeight' not in cmds.pluginInfo(self.plugin, query=True, command=True):
            self.skipTest('This existing native project registers only SkinWeights')
        # Native ParseArgs evaluates Python against Maya's global namespace.
        # Supply the dependency explicitly; source does not import it itself.
        import __main__
        __main__.cmds = cmds
        self.addCleanup(delattr, __main__, 'cmds')
        write_raw(self.mesh, self.skin, [v for _ in range(9) for v in (0.25, 0.75, 0.0)])
        before = snapshot(self.mesh, self.skin)
        cmds.flushUndo()
        cmds.AverageVtxWeight(self.mesh + '.vtx[0]', sc=self.skin, wt=1.0)
        after = snapshot(self.mesh, self.skin)
        self.assertEqual(after['weights'], before['weights'])
        cmds.undo()
        self.assertEqual(snapshot(self.mesh, self.skin), before)
        cmds.redo()
        self.assertEqual(snapshot(self.mesh, self.skin), after)

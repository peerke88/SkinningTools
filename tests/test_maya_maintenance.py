"""M5 real Maya2025/Qt6 import and adapter checks; no network or live scene."""
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

READY = 'maya.standalone' in sys.modules
if READY:
    from maya import cmds
    READY = cmds.about(batch=True)
if READY:
    from SkinningTools.Maya import api, interface, pluginPaths
    from SkinningTools.Maya.tools import shared
    from tests.maya_fixtures import SceneFixture, snapshot


@unittest.skipUnless(READY, 'Use a fresh mayapy process')
class MayaMaintenanceTests(unittest.TestCase):
    def setUp(self):
        self.fixture = SceneFixture()
        self.fixture.__enter__()
        self.addCleanup(self.fixture.__exit__, None, None, None)

    def test_real_host_version_and_native_owner_agreement(self):
        self.assertEqual(api.getMayaVersion(), '2025')
        self.assertEqual(interface.getMayaVersion(), '2025')
        self.assertEqual(api.getPluginSuffix(), interface.getPluginSuffix())
        path = api.getPlugin()
        self.assertEqual(path, interface.pathToPlugin('skinCommands'))
        self.assertIn('averageWeightPerryCpp', path)
        selected = os.environ.get('SKINNINGTOOLS_NATIVE_TEST_PLUGIN') or path
        api.loadPlugin(selected)
        self.assertTrue(cmds.pluginInfo(selected, query=True, loaded=True))
        self.assertEqual(set(cmds.pluginInfo(selected, query=True, command=True)), {'AverageVtxWeight', 'SkinWeights'})

    def test_loaded_native_basename_collision_is_rejected_before_loading(self):
        import shutil
        selected = os.environ.get('SKINNINGTOOLS_NATIVE_TEST_PLUGIN') or api.getPlugin()
        api.loadPlugin(selected)
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(prefix='m5-collision-', dir=root / 'build') as temporary:
            duplicate = Path(temporary) / Path(selected).name
            shutil.copy2(selected, duplicate)
            with self.assertRaisesRegex(RuntimeError, 'already owned'):
                api.loadPlugin(str(duplicate))
            self.assertEqual(set(cmds.pluginInfo(selected, query=True, command=True)), {'AverageVtxWeight', 'SkinWeights'})

    def test_lazy_decorator_missing_plugin_preserves_scene_and_queue(self):
        mesh, skin = self.fixture.create()
        before = snapshot(mesh, skin)
        resolver = Mock(return_value=None)
        operation = Mock()
        decorated = shared.dec_loadPlugin(resolver)(operation)
        resolver.assert_not_called()
        cmds.flushUndo()
        with self.assertRaisesRegex(RuntimeError, 'unavailable'):
            decorated()
        resolver.assert_called_once_with()
        operation.assert_not_called()
        self.assertEqual(snapshot(mesh, skin), before)
        self.assertTrue(cmds.undoInfo(query=True, undoQueueEmpty=True))

    def test_actual_qt_core_wrapper_screen_and_translation_import(self):
        from SkinningTools.UI import qt_util, translator
        from SkinningTools.ThirdParty.google_trans_new import google_translator
        self.assertEqual(qt_util.QT_VERSION, 'pyside6')
        obj = qt_util.QObject()
        pointer = qt_util.shiboken.getCppPointer(obj)[0]
        self.assertIs(qt_util.wrapinstance(pointer, qt_util.QObject), obj)
        self.assertGreater(qt_util.screenGeometry().height(), 0)
        state = SimpleNamespace(combo=SimpleNamespace(currentText=lambda: 'japanese'))
        self.assertEqual(translator.TranslatorDialog.getLangValue(state), 'ja')
        self.assertTrue(callable(google_translator))
        # Maya standalone owns a QGuiApplication, not a widget QApplication.
        # Actual widget construction is tested in a separate system-Python process.

    def test_installer_actual_ui_method_delegates_to_verified_local_transaction(self):
        import packageInstaller
        from tests.test_maintenance import core_tree
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(prefix='m5-ui-', dir=root / 'build') as temporary:
            folder = Path(temporary)
            source, dest = folder / 'release/SkinningTools', folder / 'scripts/SkinningTools'
            core_tree(source, 'new')
            core_tree(dest, 'old')
            (dest / 'UI/settings.ini').write_bytes(b'private settings')
            state = SimpleNamespace(progress=None, oldSettings=SimpleNamespace(isChecked=lambda: True),
                downloadChk=SimpleNamespace(isChecked=lambda: False), cbx=SimpleNamespace(currentIndex=lambda: 0),
                _InstallWindow__skinFile=str(dest), close=Mock())
            with patch.object(packageInstaller, 'CURRENTFOLDER', str(folder / 'release')):
                with patch.object(packageInstaller.utils, 'setProgress'):
                    packageInstaller.InstallWindow.install(state)
            self.assertEqual((dest / '__init__.py').read_text(), 'new')
            self.assertEqual((dest / 'UI/settings.ini').read_bytes(), b'private settings')
            self.assertTrue((source / '__init__.py').exists())
            self.assertEqual(len(list(dest.parent.glob('Backup_SkinningTools-*'))), 1)
            state.close.assert_called_once_with()

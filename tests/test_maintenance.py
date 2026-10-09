"""M5 real filesystem transactions and deterministic packaging in private trees."""
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
import zipfile

from Maya import pluginPaths
import installCore
import packageCreator

ROOT = Path(__file__).resolve().parents[1]


def core_tree(folder, marker):
    folder.mkdir(parents=True)
    for name in installCore.REQUIRED_FILES:
        path = folder / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(marker, encoding='utf-8')
    (folder / 'UI/SkinningToolsUI.py').write_text('__VERSION__ = "5.0.1"\n', encoding='utf-8')


class MaintenanceTests(unittest.TestCase):
    def setUp(self):
        (ROOT / 'build').mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix='m5-tests-', dir=ROOT / 'build')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source, self.dest = self.root / 'source', self.root / 'scripts/SkinningTools'
        core_tree(self.source, 'new')
        core_tree(self.dest, 'old')
        self.original = installCore.inventory(str(self.dest))

    def test_version_uses_api_year_not_launcher_or_update_label(self):
        for api, expected in ((201700, '2017'), (20170000, '2017'), (20220000, '2022'), (20250000, '2025'), (20250200, '2025')):
            self.assertEqual(pluginPaths.mayaVersion(SimpleNamespace(about=lambda **kw: api)), expected)
        with self.assertRaises(ValueError):
            pluginPaths.mayaVersion(SimpleNamespace(about=lambda **kw: 123))

    def test_reloader_skips_unavailable_plugins_without_touching_scene(self):
        from tests.source_loader import definition
        commands = SimpleNamespace(pluginInfo=Mock(), file=Mock())
        function = definition('reloader.py', 'unload', {'cmds': commands,
            'PLUGINS': [None], 'DEFAULT_RELOAD_PACKAGES': [],
            'SkinningToolsUI': SimpleNamespace(closeSkinningToolsMainWindow=Mock()),
            'sys': SimpleNamespace(modules={})})
        function(newScene=False)
        commands.pluginInfo.assert_not_called()
        commands.file.assert_not_called()

    def test_plugin_exact_owner_precedence_casing_and_no_cross_version_fallback(self):
        root = self.root / 'plugins'
        for owner in ('averageWeightPerryCpp', 'skinToolWeightsCpp'):
            target = root / owner / 'comp/maya2025/plug-ins/skinCommands.mll'
            target.parent.mkdir(parents=True)
            target.write_bytes(b'fixture-not-a-plugin')
        brush = root / 'skinToolWeightsCpp/lib/maya2025/release/smooth_brush_maya.mll'
        brush.parent.mkdir(parents=True)
        brush.write_bytes(b'wrong-owner')
        resolved = pluginPaths.resolve('SkinCommands', '2025', 'Windows', str(root))
        self.assertIn('averageWeightPerryCpp', resolved)
        self.assertIsNone(pluginPaths.resolve('skinCommands', '2024', 'Windows', str(root)))
        self.assertIsNone(pluginPaths.resolve('smooth_brush_maya', '2025', 'Windows', str(root)))
        for platform, suffix in (('Linux', '.so'), ('Darwin', '.bundle'), ('Windows', '.mll')):
            self.assertEqual(pluginPaths.pluginSuffix(platform), suffix)
        with self.assertRaises(ValueError):
            pluginPaths.resolve('unowned', '2025', 'Windows', str(root))

    def test_loader_propagates_failure_and_does_not_reload_loaded_file(self):
        path = self.source / '__init__.py'
        commands = SimpleNamespace(pluginInfo=Mock(return_value=False), loadPlugin=Mock(side_effect=RuntimeError('injected load')))
        with self.assertRaisesRegex(RuntimeError, 'injected load'):
            pluginPaths.loadPlugin(str(path), commands)
        commands.pluginInfo.side_effect = lambda unused, **kw: str(path) if kw.get('path') else True
        commands.loadPlugin.reset_mock()
        pluginPaths.loadPlugin(str(path), commands)
        commands.loadPlugin.assert_not_called()
        with self.assertRaisesRegex(RuntimeError, 'unavailable'):
            pluginPaths.loadPlugin(None, commands)

    def test_install_keeps_source_settings_tooltips_and_unique_backup(self):
        (self.dest / 'UI/settings.ini').write_bytes(b'private-settings')
        tips = self.dest / 'Maya/tooltips'
        tips.mkdir()
        (tips / 'old.gif').write_bytes(b'optional-tooltip')
        old = installCore.inventory(str(self.dest))
        source = installCore.inventory(str(self.source))
        backup = installCore.installPackage(str(self.source), str(self.dest))
        self.assertEqual(installCore.inventory(backup), old)
        self.assertEqual(installCore.inventory(str(self.source)), source)
        self.assertEqual((self.dest / 'UI/settings.ini').read_bytes(), b'private-settings')
        self.assertEqual((self.dest / 'Maya/tooltips/old.gif').read_bytes(), b'optional-tooltip')
        second = installCore.installPackage(str(self.source), str(self.dest))
        self.assertNotEqual(backup, second)

    def test_install_missing_or_tampered_replacement_preserves_existing(self):
        expected = installCore.inventory(str(self.source))
        (self.source / installCore.MANIFEST).write_text(json.dumps({'format': 1, 'files': expected}))
        (self.source / 'Maya/api.py').write_text('tampered')
        with self.assertRaisesRegex(ValueError, 'checksum'):
            installCore.installPackage(str(self.source), str(self.dest))
        self.assertEqual(installCore.inventory(str(self.dest)), self.original)
        (self.source / 'Maya/api.py').unlink()
        with self.assertRaisesRegex(ValueError, 'missing'):
            installCore.installPackage(str(self.source), str(self.dest))
        self.assertEqual(installCore.inventory(str(self.dest)), self.original)

    def test_install_copy_or_prepare_failure_keeps_old_bytes(self):
        with patch.object(installCore.shutil, 'copytree', side_effect=OSError('injected copy')):
            with self.assertRaisesRegex(OSError, 'injected copy'):
                installCore.installPackage(str(self.source), str(self.dest))
        with self.assertRaisesRegex(RuntimeError, 'injected prepare'):
            installCore.installPackage(str(self.source), str(self.dest), prepare=Mock(side_effect=RuntimeError('injected prepare')))
        self.assertEqual(installCore.inventory(str(self.dest)), self.original)
        self.assertFalse(list(self.dest.parent.glob('.SkinningTools-stage-*')))
        with patch.object(installCore.shutil, 'copytree', side_effect=OSError('original copy error')):
            with patch.object(installCore.shutil, 'rmtree', side_effect=OSError('cleanup error')):
                with self.assertWarnsRegex(UserWarning, 'Retained staging directory'):
                    with self.assertRaisesRegex(OSError, 'original copy error'):
                        installCore.installPackage(str(self.source), str(self.dest))
        self.assertEqual(installCore.inventory(str(self.dest)), self.original)

    def test_install_promotion_failure_restores_old_bytes(self):
        rename = installCore.os.rename
        def fail_promotion(source, target):
            if '.SkinningTools-stage-' in source:
                raise OSError('injected promotion')
            return rename(source, target)
        with patch.object(installCore.os, 'rename', side_effect=fail_promotion):
            with self.assertRaisesRegex(OSError, 'injected promotion'):
                installCore.installPackage(str(self.source), str(self.dest), keepBackup=False)
        self.assertEqual(installCore.inventory(str(self.dest)), self.original)

    def test_install_verification_failure_restores_old_and_first_install_removes_bad_tree(self):
        inventory = installCore.inventory
        def fail_readback(folder):
            if folder == str(self.dest) and (self.dest / '__init__.py').read_text() == 'new':
                return {'unexpected': 'digest'}
            return inventory(folder)
        with patch.object(installCore, 'inventory', side_effect=fail_readback):
            with self.assertRaisesRegex(ValueError, 'Installed package differs'):
                installCore.installPackage(str(self.source), str(self.dest))
        self.assertEqual(inventory(str(self.dest)), self.original)
        import shutil
        shutil.rmtree(self.dest)
        with patch.object(installCore, 'inventory', side_effect=fail_readback):
            with self.assertRaisesRegex(ValueError, 'Installed package differs'):
                installCore.installPackage(str(self.source), str(self.dest))
        self.assertFalse(self.dest.exists())

    def test_install_rejects_overlap_and_preparation_core_mutation(self):
        with self.assertRaisesRegex(ValueError, 'overlap'):
            installCore.installPackage(str(self.source), str(self.source / 'nested'))
        def tamper(stage):
            (Path(stage) / 'Maya/api.py').write_text('changed')
        with self.assertRaisesRegex(ValueError, 'Preparation altered'):
            installCore.installPackage(str(self.source), str(self.dest), prepare=tamper)
        self.assertEqual(installCore.inventory(str(self.dest)), self.original)

    def test_install_rollback_failure_reports_recoverable_old_backup(self):
        rename = installCore.os.rename
        def fail_promotion_and_restore(source, target):
            if '.SkinningTools-stage-' in source or 'Backup_SkinningTools-' in source:
                raise OSError('injected rollback failure')
            return rename(source, target)
        with patch.object(installCore.os, 'rename', side_effect=fail_promotion_and_restore):
            with self.assertRaisesRegex(RuntimeError, 'previous tree is at'):
                installCore.installPackage(str(self.source), str(self.dest))
        backups = list(self.dest.parent.glob('Backup_SkinningTools-*'))
        self.assertEqual(len(backups), 1)
        self.assertEqual(installCore.inventory(str(backups[0])), self.original)

    def test_successful_replace_removes_backup_only_after_verification(self):
        backup = installCore.installPackage(str(self.source), str(self.dest), keepBackup=False)
        self.assertIsNone(backup)
        self.assertEqual((self.dest / '__init__.py').read_text(), 'new')
        self.assertFalse(list(self.dest.parent.glob('Backup_SkinningTools-*')))

    def test_packaging_is_identical_preserves_licenses_and_does_not_change_source(self):
        (self.source / 'dragDropInstall.mel').write_text('installer')
        (self.source / 'packageInstaller.py').write_text('__VERSION__ = "5.0.1"\n')
        license_path = self.source / 'ThirdParty/example/LICENSE'
        license_path.parent.mkdir(parents=True)
        license_path.write_bytes(b'original license notice')
        (self.source / 'README.md').write_text('[contract](docs/development/RELEASE_PROCESS.md)')
        contract = self.source / 'docs/development/RELEASE_PROCESS.md'
        contract.parent.mkdir(parents=True)
        contract.write_text('release contract')
        files = list(installCore.REQUIRED_FILES) + ['ThirdParty/example/LICENSE', 'README.md', 'docs/development/RELEASE_PROCESS.md']
        before = installCore.inventory(str(self.source))
        results = [packageCreator.createPackage(self.root / ('release%d.zip' % index), self.source,
                   version='5.0.2', files=files) for index in (1, 2)]
        self.assertEqual(results[0]['sha256'], results[1]['sha256'])
        self.assertEqual(installCore.inventory(str(self.source)), before)
        with zipfile.ZipFile(results[0]['path']) as archive:
            self.assertEqual(archive.read('SkinningTools/ThirdParty/example/LICENSE'), b'original license notice')
            self.assertIn(b'5.0.2', archive.read('packageInstaller.py'))
            self.assertEqual(archive.read('SkinningTools/RELEASE_PROCESS.md'), b'release contract')
            self.assertIn(b'(RELEASE_PROCESS.md)', archive.read('SkinningTools/README.md'))
            extracted = self.root / 'extracted'
            archive.extractall(extracted)
        installCore.validatePackage(str(extracted / 'SkinningTools'))
        with self.assertRaisesRegex(ValueError, 'overwrite'):
            packageCreator.createPackage(results[0]['path'], self.source, files=files)

    def test_release_selection_excludes_personal_data_and_includes_primary_and_notices(self):
        names = ['UI/settings.ini', 'scene.mb', 'Maya/test.skinWeights', 'Maya/plugin/averageWeightPerryCpp/comp/Maya2025/plug-ins/skinCommands.mll',
                 'ThirdParty/qcachegrind/LICENSE.LGPL', 'Maya/plugin/build/private.py', 'UI/icons/logo.png', 'tests/private.json']
        with patch.object(packageCreator.subprocess, 'check_output', return_value=('\0'.join(names)+'\0').encode('utf-8')):
            selected = packageCreator.releaseFiles(self.source)
        self.assertEqual(selected, sorted([names[3], names[4], names[6]]))

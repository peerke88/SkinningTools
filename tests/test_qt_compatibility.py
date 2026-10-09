"""Real Qt widgets outside Maya; source-defined combobox avoids Maya dependencies."""
import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class QtCompatibilityTests(unittest.TestCase):
    def check_binding(self, binding):
        if importlib.util.find_spec(binding) is None:
            self.skipTest('%s is unavailable; no runtime claim' % binding)
        code = '''
import os, sys
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
import importlib.util
spec = importlib.util.spec_from_file_location('m5_qt_util', ROOT / 'UI/qt_util.py')
qt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qt)
import ast
assert qt.QT_VERSION == EXPECTED
app = qt.QApplication([])
widget = qt.QWidget()
assert qt.wrapinstance(qt.shiboken.getCppPointer(widget)[0], qt.QWidget) is widget
assert qt.screenGeometry().height() > 0
tree = ast.parse((ROOT / 'UI/translator.py').read_text(encoding='utf-8'))
node = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'SearchableComboBox')
scope = dict(qt.__dict__)
exec(compile(ast.Module(body=[node], type_ignores=[]), str(ROOT / 'UI/translator.py'), 'exec'), scope)
Combo = scope['SearchableComboBox']
combo = Combo()
combo.addItem('fixture')
combo._sync()
assert combo.currentText() == 'fixture'
widget.close()
combo.close()
print('REAL_QT_WIDGETS', qt.QT_VERSION, 'passed')
'''
        # qt_util prefers PySide6; isolate PySide2 explicitly when both are installed.
        if binding == 'PySide2':
            code = "import sys\nsys.modules['PySide6'] = None\nsys.modules['PySide'] = None\n" + code
        code = 'from pathlib import Path\nROOT = Path(%r)\nEXPECTED = %r\n' % (str(ROOT), binding.lower()) + code
        result = subprocess.run([sys.executable, '-c', code], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('REAL_QT_WIDGETS', result.stdout)

    def test_pyside6_real_widget_wrapper_screen_and_combobox(self):
        self.check_binding('PySide6')

    def test_pyside2_real_widget_wrapper_screen_and_combobox(self):
        self.check_binding('PySide2')

"""Run only as: mayapy tests/run_maya.py, never inside interactive Maya."""
import os
import sys
import time
import unittest


def main():
    if 'maya.cmds' in sys.modules or 'maya.standalone' in sys.modules:
        raise RuntimeError('Run this file in a fresh mayapy process')
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, root)
    sys.path.insert(0, os.path.dirname(root))
    import maya.standalone
    maya.standalone.initialize(name='python')
    try:
        from maya import cmds
        if not cmds.about(batch=True):
            raise RuntimeError('Interactive Maya is forbidden')
        print('Host: Maya %s; Python %s' % (cmds.about(version=True), sys.version))
        start = time.perf_counter()
        suite = unittest.defaultTestLoader.discover(os.path.join(root, 'tests'), pattern='test_maya_*.py', top_level_dir=root)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        print('Elapsed test seconds: %.3f' % (time.perf_counter() - start))
        return 0 if result.wasSuccessful() else 1
    finally:
        maya.standalone.uninitialize()


if __name__ == '__main__':
    sys.exit(main())

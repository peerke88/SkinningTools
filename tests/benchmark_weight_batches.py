"""Warm command-only comparison; run in a fresh mayapy process with --plugin."""
import argparse
import json
import os
import statistics
import sys
import time


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--plugin', required=True)
    args = parser.parse_args()
    if 'maya.standalone' in sys.modules or 'maya.cmds' in sys.modules:
        raise RuntimeError('Use a fresh mayapy process')
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, root)
    sys.path.insert(0, os.path.dirname(root))
    import maya.standalone
    maya.standalone.initialize(name='python')
    try:
        from maya import cmds
        from tests.maya_fixtures import SceneFixture, snapshot
        if not cmds.about(batch=True):
            raise RuntimeError('Interactive Maya is forbidden')
        cmds.loadPlugin(os.path.abspath(args.plugin), quiet=True)
        with SceneFixture() as fixture:
            for subdivisions in (2, 10, 32):
                mesh, skin = fixture.create(subdivisions=subdivisions)
                count = cmds.polyEvaluate(mesh, vertex=True)
                weights = [v for unused in range(count) for v in (0.25, 0.25, 0.5)]
                payload = json.dumps([{'mesh': mesh, 'skinCluster': skin, 'vertices': list(range(count)),
                                       'influences': [0, 1, 2], 'weights': weights}])
                cmds.SkinEditor(mesh, skin, bt=payload)
                times = []
                for unused in range(11):
                    cmds.flushUndo()
                    start = time.perf_counter()
                    cmds.SkinEditor(mesh, skin, bt=payload)
                    times.append(time.perf_counter()-start)
                assert snapshot(mesh, skin)['weights'] == weights
                print('COMMAND_ONLY %d vertices median %.6f min %.6f max %.6f seconds' %
                      (count, statistics.median(times), min(times), max(times)))
    finally:
        maya.standalone.uninitialize()


if __name__ == '__main__':
    main()

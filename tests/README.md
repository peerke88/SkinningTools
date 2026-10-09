# Reliability characterization and regressions

Run from the repository root:

```powershell
python -m unittest discover -s tests -t . -v
& 'C:\Program Files\Autodesk\Maya2025\bin\mayapy.exe' tests/run_maya.py
python tests/inventory.py
```

The first command runs host-independent source-definition tests. Maya tests are
explicit skips here. The second initializes a fresh standalone process and runs
real Maya, PySide6 model, Python plugin and bundled native binary tests. Do not
execute the runner from Maya's Script Editor. Fixture helpers refuse interactive
Maya. No runner creates, opens or saves a scene file or invokes the reloader or
installer. Tests make temporary namespaces and delete only nodes created during
each fixture, including generated skin history and poses. Failures still execute
cleanup. Undo queue flushing is restricted to the disposable batch process.

Source-definition tests compile the original selected function body with explicit
fake collaborators. They do not validate full imports, UI event wiring, Maya
types or native binaries. Tests for D001/D002/D008/D009/D011/D012 now assert
desired M1 behavior. Tests for untouched defects deliberately assert observed
baseline behavior, including erroneous results. Passing suites do not certify
all defects as corrected. Original M0 expectations/evidence remain in the M0
commit and TEST_RESULTS.txt. D018 is an explicit bind-pose characterization.

Snapshots include weights, ordered influence names, physical and logical indices,
locks, normalization/max-influence settings, selection and associated bind poses.
Fixtures cover multiple meshes/different influence sets, sparse indices after
removal/addition, locks, invalid/missing skinCluster, zero/under/over-normalized
weights, boundary and isolated vertices. Invalid fixture dimensions/NaN/infinity
are rejected before fixture mutation. This safety validation is test code only.

Native tests load the existing matching Windows `averageWeightPerryCpp` binary,
which registers both `SkinWeights` and `AverageVtxWeight`. Missing matching
binaries are skips; load failures are errors. This is not a C++ rebuild or proof
that the binary matches checked-in source. Native smoothing requires `cmds` in
Maya's global Python namespace; the smoke test supplies this explicitly and
removes it afterwards. A run without it logged NameError while returning success.

Bulk timings use 9, 121 and 1089 vertices and three influences. They are smoke
measurements without thresholds, not production performance certification.
See `docs/development/TEST_MATRIX.md` for blocked and deferred cases.

M2 adds desired weight-contract cases in test_maya_weight_integrity.py. D003/D014
now assert corrected writes and exact undo/redo; D015 asserts propagation. There
are 16 Python cases and 33 Maya cases. Import batching is tested with existing
clusters and geometry matching isolated; D019/D020 explicitly characterize the
unchanged remap/sampling errors. File-import tests use a disposable temporary JSON
file, removed on exit. No test fixture data or scene files are delivered to GitHub.
M2_TEST_RESULTS.txt and WEIGHT_WRITE_CONTRACT.md describe evidence and boundaries.

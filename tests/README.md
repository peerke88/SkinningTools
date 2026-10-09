# Baseline characterization

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
types or native binaries. Tests named with defect IDs deliberately assert
**observed baseline behavior**, including erroneous results. Green M0 tests do
not mean those defects are corrected. M1 and later should add desired-behavior
regressions and replace obsolete characterization expectations in the same
reviewable correction, without weakening assertions to hide failures.

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

# M4 architecture recovery — 2026-10-09

Parent: `6ca6e494460d136fe08811064e06f503f8092ee0`. M3 was accepted by the
user's request to continue M4. Work stays on local
`refactor` branch (verified at delivery); no push, PR or publication. M4 is delivered
for acceptance; stop before M5.

## Result and ownership

Deterministic weight calculations can now be imported without Maya or Qt.
The Python brush and batch writer share locked-budget normalization. Table
selected-cell priority and slider uniform/low/high policies remain separate,
named implementations because their existing behavior differs.

| Responsibility | Authoritative implementation | Existing caller/owner |
| --- | --- | --- |
| Validation, normalization, limiting and blending | Maya/tools/weightMath.py | Batch writer and Python brush |
| Table and slider calculation policies | Maya/tools/weightMath.py | UI methods gather inputs and apply results |
| Physical/logical influence layout and Maya resolvers | Maya/tools/weightWrite.py | Shared, ApiWeights, brush and writer |
| Prepare, exact apply, readback and rollback | weightWrite.WeightBatch | SkinEditor/brush MPxCommands own undo |
| Native SkinWeights and exact-write/layout helpers | averageWeightPerryCpp/projects | Both existing native targets |
| Native smoothing | averageWeightPerryCpp/projects/averagevtxweight.cpp | Existing AverageVtxWeight |

SkinEditClass retains its name, flags, methods and signatures through inheritance;
the plugin adapter handles parsing and undo/redo. The Python brush no longer imports
or constructs another plugin command class as a writer. Shared helpers and
ApiWeights consume canonical mapping, preserving physical weight-array positions
and logical bind-matrix plug indices.

The duplicate native project's three source/header files include the authoritative
averageWeightPerryCpp files. Both projects and registrations remain. This makes
skinToolWeightsCpp/projects depend on its sibling source tree; building an isolated
copy of that directory is no longer supported. The full repository contains the
dependency. No new library/build target is introduced; smoothBrushRodCpp is unaffected.

The table groups rows by mesh/influence layout, commits one batch, then publishes
derived UI status. An unused original-weight cache and fragile last-row flushing
are removed; M2 scene snapshots still own exact undo/redo. Unused native private
arrays and redundant registration rethrows are removed. Slider Qt/util imports
become explicit; its py23 wildcard remains for Python 2 builtin compatibility.

Maya skinPercent/copySkinWeights and the independent native brush remain legitimate
mutation owners. Slider writes retain skinPercent normalization/max-setting
semantics. Arbitrary binding/influence operations are not whole-scene transactions.
Equivalent implementations are consolidated without imposing one policy on every
different Maya operation.

## Changed files

Production: new Maya/tools/weightMath.py and weightWrite.py; existing
Maya/plugin/SkinEditPlugin.py and averageWeightPlugin.py; Maya/tools/shared.py and
apiWeights.py; UI/weightEditor/weightEditor.py and
UI/ControlSlider/vertexinfluenceeditor.py; averageWeightPerryCpp/projects
averagevtxweight.h and skinweights.h; skinToolWeightsCpp/projects skinweights.cpp,
skinweights.h and utils.hpp; matching primary Maya2025 skinCommands.mll.

Tests: new test_weight_math.py, test_maya_architecture.py,
compare_weight_policies.py and benchmark_weight_batches.py; existing
test_characterization.py, inventory.py and README.md. Development documentation:
new M4 report, four evidence files and inventory; existing architecture, changelog,
defect ledger, test matrix and weight-write contract. No installer/loader is edited.

## Correctness evidence

- 23 Python tests pass: 75 ordinary discovered cases, 52 explicit Maya skips.
  Seven new tests import the actual pure module, including a fresh-process
  dependency check, offset row normalization, locks, zero fallback and limits.
- 52 Maya2025/Python3.11/PySide6 tests pass against delivered primary bytes.
  Four new architecture cases exercise actual UI methods with controlled metadata
  and real writes, sparse mappings, interleaved meshes, one undo entry, final zero
  rows and callback cleanup. They do not exercise interactive Qt event wiring.
- Both native projects compile with the existing M3 configuration; four setter
  cases pass against the separately built duplicate target.
- Read-only accepted-M3 source comparison gives exact equality in 864 slider and
  256 table policy cases. This is not exhaustive input coverage.
- Original M3 callback code reproduces a stuck guard for one slider. Original M3
  table code with the new zero-row fixture submits an unfinished earlier request
  with empty influence/weight buffers and fails validation. M4 desired tests pass.
  D022/D023 record these incidental control-flow corrections.

Evidence: M4_TEST_RESULTS.txt, M4_POLICY_RESULTS.txt, M4_BASELINE_RESULTS.txt,
M4_PERFORMANCE_RESULTS.txt and M4_CALL_SITES.json. The new inventory retains the
known Python3 translator parse failure; historical CALL_SITES.json is unchanged.

## Performance

Fresh-process benchmark: M3 SkinEditor source versus M4, same host/meshes/prebuilt
JSON request, one warmup and eleven command calls. Medians in seconds:

| Vertices | M3 | M4 |
| --- | --- | --- |
| 9 | .000316 | .000324 |
| 121 | .000937 | .001103 |
| 1089 | .006458 | .006751 |

The largest case is about 4.5% slower, with overlapping observed ranges. The first
extraction added about 22%; normalizing private flat rows in place and avoiding
redundant numeric type checks on SDK MDoubleArray snapshots reduced that cost.
Finite/range checks remain; generic inputs still receive type validation.
Shared mapping/dispatch overhead remains, with less than .2 ms absolute difference
for smaller cases. The benchmark excludes wrapper queries and JSON preparation.
Delivered smoke: shared 1089-vertex get/set .008324 s, native smoothing .010176 s.
These observations do not certify production-scale performance or memory use.

## Build and delivery

Reuse M3_BUILD.md's Maya2025/MSVC v143 configuration:

```powershell
cmake --build build/m3-average-fixed --config Release
cmake --build build/m3-setter-fixed --config Release
```

Only averageWeightPerryCpp/comp/Maya2025/plug-ins/skinCommands.mll is updated.
It is an exact copy of the tested output, and the final suite loads those bytes.
SHA256: `A0214887ED527B65520E7E496D5ED9910D6099599A4E8B0BC6D080AD4A9E82F9`.
Previous bytes are recoverable from the parent commit. The separate ignored output
build/m3-setter-fixed/Release/smooth_brush_maya.mll has SHA256
`F2196312E267238F743DE5D75F61768D9FB54EF4160FF6D675A19D7EC65D20CE`.
Its target name does not identify the separate smoothBrushRodCpp engine. No other
host/platform binary is replaced.

## Limits and acceptance

Minimum Python/Maya versions and public APIs are intentionally retained. Maya2022/
PySide2 and Python2 runtime verification are unavailable. Interactive workflows,
Linux/macOS, other ABI binaries, NURBS/lattice setters, native post-mutation fault
injection and production memory/scale remain unvalidated. Standalone checks run
actual callbacks/methods, not full interactive workflows. D017-D020 and
loader/build/version/installer work remain for M5 or later scope.
Automated M4 evidence passes within these host boundaries; user acceptance is pending.

# M0 verification matrix

Date: 2026-10-09, Asia/Tokyo. Tests use unittest; all changes are characterization
infrastructure, fixtures and documentation. Exact commands are in tests/README.md.

## Executed results

| Suite | Runtime | Result | Interpretation |
| --- | --- | --- | --- |
| Host-independent definitions | System Python 3.13.14 | 12 passing cases | Executes selected unchanged source bodies with explicit fake collaborators |
| Host tests | Maya 2025 / Python 3.11.4 / PySide6 | Final counts in CHANGELOG.md and TEST_RESULTS.txt | Real API, Qt model, Python plugin and native binary; disposable standalone process |
| Complete shared import | Maya 2025 standalone | Passed | Includes package/UI import chain; not UI construction |
| Source call inventory | Python 3.13.14 | Generated CALL_SITES.json | Reports translator Python 2 syntax and CMake helper escape warning |

The ordinary Python discovery reports host tests as explicit skips; the standalone
runner executes them. These are baseline characterizations: some deliberately
assert broken behavior. No corrected-defect acceptance is claimed.

| Coverage | Evidence | Still needed |
| --- | --- | --- |
| D001 | Real decorated call returns None; undecorated call raises NameError; isolated source case | Correct valid/missing/multi mesh bind-pose behavior in M1 |
| D002 | Source paste mutates memory, registers no rows; locked cell preserved | Actual Qt paste events, one/many cells/vertices/meshes and undo/redo |
| D003 | Real typed API write changes weights with empty undo queue | Unified writer, exact failure rollback, multi mesh/consecutive edit undo |
| D004 | Real removed+added sparse mapping accepts physical shared indices | Other writers, lock/settings behavior; reject unsupported logical substitution |
| D005 | Source formula at strengths 0/.5/1, normalization masking, zero neighbors | Maya callback, boundary/sparse max influence cases, desired math comparison |
| D006 | Source redo ignores vertex zero and zero strength, calls positive case | Maya paint command exact redo/undo |
| D007 | Source parsing index evidence in both copies | Native setter many flags/invalid inputs in isolated processes; source rebuild |
| D008 | Both source checks accept .5 total, reject 1.5, accept 1 | Qt status and corrected absolute tolerance in M1 |
| D009 | Real selection of A.vtx[0], B.vtx[7] returns both IDs for either mesh | Shape/transform names, mixed object/components and corrected UI rows |
| D010 | Source flattened limiting and normalization evidence | Distinct distributions across multiple vertices, enabled max-influence setting |
| D011 | Real PySide6 dataChanged emits invalid indices, memory changed | Correct signal indices/roles under PySide6 and PySide2 and view refresh |
| D012 | Source platform function executions disagree on Linux | Real Linux/macOS plugin resolution, primary loader ownership |
| D013 | Installer deletion precedes replacement move in source | Fault-injected filesystem installation staging/rollback; never run live installer |
| D014 | Real list input raises constructor TypeError; scene snapshot unchanged | Explicitly approve correction scope; list/array parity after fix |
| Existing SkinEditor | Two vertices, three undo/redo cycles, exact snapshots, unrelated second mesh | Locked weights, unnormalized originals, all normalization modes, atomic multi mesh |
| Native binary | Matching 2025 binary loads; query matches API; constant-weight vertex-0 smoothing and undo/redo | Nonconstant numerical reference, malformed flags, source/binary equivalence |
| Fixture safety | Batch guard, namespace cleanup after injected exception, original nodes/selection preserved | Fixtures are forbidden in interactive scenes |
| Fixture inputs | NaN/infinity/dimension failures before writes; zero/.5/1.5 totals; locks and sparse map capture | Does not establish production input validation |
| Mesh topology | Boundary triangle and isolated vertex, multiple/different influence meshes | Brush integration and representative production topology |

## Failures investigated rather than concealed

1. First integration run: D003/D004 raised MDoubleArray constructor TypeError
   for list inputs. Classification: **Product defect**, new D014. Keep explicit
   failure-before-write test. Pass MDoubleArray on the valid public array branch
   to test undo/index contracts separately; no production change.
2. First integration run: D011 expected TypeError, but no exception occurred.
   Classification: **Test defect** (incorrect assumption). The corrected test
   connects to the actual signal and asserts delivered QModelIndex validity.
   Invalid indices are reproduced; the defect is not hidden.
3. Native smoke run without global cmds: NameError logged by native Python
   evaluations despite a successful command return. Classification: **Product
   defect / runtime dependency**, D016. Later numerical smoke explicitly seeds
   that dependency; this does not certify error propagation.
4. Initial inventory generation could not parse translator.py. Classification:
   **Product compatibility defect**, D017; generator abort was a **Test tooling
   defect**. Inventory now records parse failures explicitly instead of dropping
   the file silently. CMake helper invalid escape is a warning, not an executed
   build failure.
5. Original D004 claim for shared.py: **Unverified hypothesis contradicted in
   the tested case**. Sparse shared writes passed without any code correction.

## Unavailable and deferred checks

- Environment limitation: Maya 2022 and PySide2 unavailable, so secondary-host
  integration and real Qt5 interaction cannot run. Real Linux/macOS are absent.
- Deferred scope: interactive Maya 2025 UI/brush events and complete window
  workflows; no user scene touched or reset.
- Deferred scope: native compilation. Compiler/CMake/SDK files are present,
  but CMake project/source ambiguity and ABI/build reproducibility require M3/M5
  investigation. Available binary execution is not rebuilt-source validation.
- Deferred scope: D007 unsafe argument cases, D010 multi-vertex native numerical
  limits, installer fault injection, production failure rollback, atomic writes,
  all lock/normalization modes and full-scene history equivalence.
- Large-mesh/production performance and memory not measured. Bulk smoke timings
  are reported in TEST_RESULTS.txt; no optimization or pass threshold imposed.

Every finding's expected behavior and reproduction plan is in DEFECT_LEDGER.md.
M1 corrections need desired-behavior regressions, not merely these baseline checks.

## M2 evidence update

Historical tables above remain M0 evidence. M2 executes 16 Python and 33 Maya
cases; see M2_TEST_RESULTS.txt and M2_REPORT.md. D003 and D014 now assert corrected
behavior, D015 preserves exceptions, and sparse physical mapping is retained.
Exact command batch rollback, locked weights, normalization modes 0/1/2, raw
arrays and single-entry multi-mesh undo are tested. Full importer geometry matching
is isolated in its write-boundary test; D019/D020 separately assert remaining
remapping/sampling defects. Arbitrary full-scene transactions, production memory
and scale, native rebuilds, interactive UI and Maya 2022 remain unvalidated.

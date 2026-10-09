# M2 weight integrity and command ownership

2026-10-09, Asia/Tokyo. User accepted M1 and requested continuation. Parent:
`bd19472ce1b3521fbe5c9edba4a60d6ab50dd029`. Work and commit stay local on
`codex/skinningtools-reliability`; nothing is pushed or published to GitHub.

## Result

D003 is corrected at the shared/full-mesh/table weight-write boundary by extending
the existing SkinEditor command. Multi-mesh paste and staged importer weight writes
now use one command, exact original/committed snapshots and failure rollback.
D004's original corruption hypothesis remains unreproduced; physical indices are
retained, made explicit and tested with sparse logical mappings and locked values.
Reordered vertex and influence inputs map to the intended rows/columns.

D014's unsupported list constructor disappears as a necessary consequence of
routing lists and MDoubleArray through the same boundary. D015 propagation is
necessary for failed writes to reach callers: dec_undo closes chunks then re-raises.
These supporting corrections were explained during M2; unrelated algorithms,
native binaries and package hierarchy were not changed.

Five production files changed: Maya/plugin/SkinEditPlugin.py, Maya/tools/shared.py,
Maya/api.py, Maya/tools/weightsManager.py and UI/weightEditor/weightEditor.py.
Public signatures and legacy command flags remain; batching and normalization flags
are additive. See WEIGHT_WRITE_CONTRACT.md for validation, lock behavior, index
spaces, settings control, routes and atomicity limits.

## Validation

16 host-independent cases pass. Ordinary discovery explicitly skips 33 host cases;
all 33 pass in a fresh Maya 2025/Python 3.11.4/PySide6 standalone process. These
include existing native smoke cases, not native rebuilds. M2_TEST_RESULTS.txt
contains final output. Passing characterizations for unchanged defects are not
claims that those defects are fixed. No live user scene is opened or saved.

M2 tests exercise exact repeated/consecutive undo/redo, raw unnormalized originals,
two meshes/different influence counts, partial/reordered components, stale caller
originals, sparse mapping/locks, zero rows, normalization modes 0/1/2, setting
restoration, list/array parity, cluster mismatch, duplicate/out-of-range indices,
NaN/infinity/range/dimension failures and injected failures after real mutations.
The failed second write restores both meshes and creates no undo entry. Failed
undo restores pre-undo weights and emits the expected error. Real table paste now
undoes both meshes once. Existing-cluster import weight batching is tested with
geometry matching explicitly isolated; its invalid second payload leaves both
meshes unchanged. This does not certify the complete import/remapping workflow.

The initial desired M2 regressions failed before production changes. Implementation
investigation found non-DAG getDagPath raises TypeError in this host and mode-1
normalization alters writes despite the API flag; both were resolved. Test harness
assumptions about plugin module registration and cmds.undo exception propagation
were corrected using the registered command class and Maya error callbacks.

Importer investigation initially suspected missing exported metadata. A direct
check contradicted that hypothesis: the fixture exports nine positions. The actual
confirmed additional defects are D019 (closest-point list coordinates used as dict
keys) and D020 (inclusive random upper bound beyond the final vertex). Both remain
unchanged with explicit reproductions, rather than silently broadening M2.

## Costs and remaining checks

The 1,089-vertex, three-influence smoke write measures approximately 8-9 ms in
typical M2 runs, versus about 1.8 ms in M1, roughly five times slower. One run was
18 ms, showing uncontrolled host variation. Validation, snapshots, JSON transport
and exact readback add overhead. Writes remain bulk API operations per geometry,
without per-vertex Maya command calls. No performance threshold or production-scale
certification is claimed; memory usage was not measured.

Maya 2022/PySide2, interactive editor/brush events, real Linux/macOS, large production
meshes and native builds remain unavailable or deferred. Max-influence pruning is
owned by caller algorithms, not this exact snapshot writer. Atomicity does not cover
importer binding creation or arbitrary tool scene changes. Persistent failure of
the rollback API is reported explicitly but cannot guarantee recovery. Existing
native and brush paths remain for M3; D018 bind-pose behavior remains unchanged.

M2 is delivered for acceptance. Stop here before implementing M3.

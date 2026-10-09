# Development change ledger

## M0 — 2026-10-09 — accepted 2026-10-09

Baseline: `2d712f9dd844112d7457324b85e6c351e60f66b1`.
Branch: `codex/skinningtools-reliability`. Local M0 commit:
`4d6d3f026dc5025a734274691cf2649d534a4391`.
No GitHub push, PR, merge or publication. Production files and binaries unchanged.

Added:

- docs/development/BASELINE.md — authoritative baseline and environment contract.
- docs/development/ARCHITECTURE.md and CALL_SITES.json — manual execution map plus
  generated source call locations, arguments and parse-failure records.
- docs/development/DEFECT_LEDGER.md — D001-D013 verification and additional M0
  findings D014-D017; none marked Fixed or Accepted.
- docs/development/TEST_MATRIX.md and TEST_RESULTS.txt — evidence levels,
  investigation history, executed results and limitations.
- tests/__init__.py, source_loader.py, test_characterization.py — standard-library
  harness with 12 host-independent baseline cases.
- tests/maya_fixtures.py, run_maya.py, test_maya_integration.py,
  test_maya_native.py — batch-only fixture lifecycle and real-host tests.
- tests/inventory.py and README.md — inventory regeneration and safety/run notes.

Validation: 12 host-independent tests pass; 16 Maya 2025 cases pass (14 API/Qt/
Python-plugin/fixture/performance cases and 2 bundled-native cases). Ordinary
Python discovery skips those 16 host cases explicitly. Full command outputs are
saved in TEST_RESULTS.txt. Product defects remain present and deliberately
characterized. First-run failures were classified and preserved in the matrix.

Risks: Maya 2022/PySide2, interactive event workflows, native build provenance,
failure atomicity, locks/normalization, unsafe native arguments, installer rollback
and release compatibility require later milestones. User acceptance is required
before M1. Keep proposed M1 targets D001/D002/D008/D009/D011/D012; seek explicit
scope acceptance for D014, and reconsider original D004 assumptions for M2.

## M1 — 2026-10-09 — accepted by continuation 2026-10-09

Parent: `4d6d3f026dc5025a734274691cf2649d534a4391`. Same working branch.
The user accepted M0 and requested continuation. No GitHub push, PR or merge.

D001 retains resolved clusters and refuses missing clusters before comparison.
D002 registers paste rows/columns and skips unavailable targets. D008 checks
absolute normalization error. D009 scopes selection to its owning mesh/shape.
D011 emits actual model indices. D012 resolves the Linux suffix as .so.

Production changes: Maya/interface.py, Maya/tools/apiWeights.py,
Maya/tools/skinCluster.py, UI/weightEditor/weightEditor.py and
UI/weightEditor/weightsTableModel.py. Tests/test_characterization.py and
tests/test_maya_integration.py include desired-behavior regressions for corrected
targets and retain untouched defect characterizations. Public signatures, native
plugins, weight algorithms and undo implementation unchanged. Original production
CRLF/EOF conventions preserved; check whitespace with Git cr-at-eol enabled.

Validation: 16 host-independent cases and 18 Maya 2025/PySide6 cases pass,
including two-mesh paste with locked weights and exact undo/redo. Full evidence:
M1_TEST_RESULTS.txt. Scope, test investigations and limitations: M1_REPORT.md.

New D018: existing checkBasePose misclassifies an untouched bind in Maya 2025.
It remains unchanged and explicitly characterized. D014 also remains unchanged.
Neither additional correction scope nor M2-M5 implementation was included.
Maya 2022/PySide2 and complete interactive workflows remain unvalidated.
Stop for user acceptance before M2.

## M2 — 2026-10-09 — accepted by continuation 2026-10-09

Parent: `bd19472ce1b3521fbe5c9edba4a60d6ab50dd029`. Same working branch.
User accepted M1 and requested continuation. No GitHub push, PR or publication.

D003 now uses the existing SkinEditor owner for shared/full-mesh/table writes,
with exact snapshots, one multi-mesh undo entry and verified failure rollback.
D004 retains physical indices and explicit mapping/component identity. D014 list
support and D015 exception propagation are necessary incidental M2 corrections.

Five production files changed: Maya/api.py, Maya/plugin/SkinEditPlugin.py,
Maya/tools/shared.py, Maya/tools/weightsManager.py, UI/weightEditor/weightEditor.py.
Existing APIs/flags retained; batch helper/flags and normalization flag added.
Tests update corrected expectations and add tests/test_maya_weight_integrity.py.
Documentation: M2_REPORT.md, WEIGHT_WRITE_CONTRACT.md, M2_TEST_RESULTS.txt and
updates to the defect ledger, architecture, matrix and test README.

Validation: 16 Python cases and 33 Maya 2025 cases pass. Bulk 1,089-vertex writes
are approximately five times slower than M1 in uncontrolled smoke measurements;
production memory/scale unmeasured. Exact writer does not enforce max influences.
D019 closest-coordinate remapping and D020 out-of-range random sampling are
reproduced and unchanged. Full importer binding/remap transaction unvalidated.
Maya 2022/PySide2, interactive workflows and native builds remain deferred.
Stop for acceptance before M3.

## M3 — 2026-10-09 — accepted by continuation to M4

Parent: `effbb7fd2ad49f249411dc40238f002486abc03d`. User accepted M2 and
requested continuation. Same local branch; no GitHub push, PR or publication.

D005/D006 correct Python brush interpolation, zero/isolated policy and cached
undo/redo. D010 corrects native per-vertex limiting/normalization. D007 parsers
are hardened in both native copies; valid-call corruption was not reproduced,
while missing invalid-input failure was reproduced. D016 settings queries now
use native plugs; D021 default-selection fallback is fixed during argument audit.
Native physical indices, locks, status propagation and exact writes are validated.

Production: averageWeightPlugin.py; averageWeightPerryCpp/projects
averagevtxweight.cpp/.h, skinweights.cpp/.h, utils.hpp; skinToolWeightsCpp/projects
skinweights.cpp/.h, utils.hpp; primary Maya2025 averageWeightPerryCpp skinCommands.mll.
Only that bundled binary is replaced. Duplicate setter build remains under ignored
build/; no plugin removed or unrelated smoothBrushRodCpp engine changed.

Validation: 16 Python tests; 48 Maya2025 tests against delivered primary binary;
four setter cases against the independently rebuilt duplicate. Separate invalid
native cases execute in fresh processes. Evidence: M3_TEST_RESULTS.txt,
M3_BASELINE_RESULTS.txt, M3_REPORT.md and M3_BUILD.md. New mathematical reference
and host regressions: tests/test_maya_smoothing.py. M2 class-selection injection
harness corrected to distinguish registered/imported command classes.

1,089-vertex native smoothing costs about 10-11 ms versus approximately 15 ms in
the original-source smoke (incorrect math and cmds errors; not a certified speedup).
Memory/production scale, interactive events, Maya2022/PySide2, other ABI/platform
binaries and native post-mutation fault injection remain unvalidated.
Stop for acceptance before M4.

## M4 — 2026-10-09 — accepted by continuation to M5

Parent: `6ca6e494460d136fe08811064e06f503f8092ee0`. User accepted M3 and
requested M4. Local branch only; no GitHub push, PR or publication.

Extract weightMath deterministic policies and weightWrite canonical Maya
layout/exact batch machinery. SkinEditor and Python brush own undo and share the
writer. Table/slider methods delegate math; table groups interleaved rows into
one batch. D022 callback cleanup and D023 final-zero-row flushing are corrected.
Public APIs and distinct solver policies remain. Native duplicate sources include
the primary implementation; both projects compile and remain. Remove confirmed
unused caches/private fields, redundant rethrows and slider Qt/util wildcards.

Validation: 23 Python tests, 52 Maya2025 tests using delivered primary bytes,
four duplicate setter tests, 864 exact slider and 256 table policy comparisons.
Final command-only 1089-vertex median is about 4.5% above M3 with overlapping ranges.
Only the matching primary Maya2025 binary is updated. M4_REPORT.md and associated
results record evidence/limits. D017-D020, interactive and secondary hosts remain
deferred. Stop for acceptance before M5.

## M5 — 2026-10-09 — local delivery, awaiting acceptance

Parent: dc8068eb7aa00982a94646a4c08a5f38915df9dc. User accepted M4 by continuing.
Local refactor branch; no GitHub push, PR, merge, publication or live installation.

D013 staged installer recovery, D017 Python3 translation imports, D024 canonical
plugin/version resolution, D025 deterministic packaging and D026 native build
ownership are corrected. Existing API entry points, legacy dependencies/binaries
and minimum runtime claims remain. Qt wrappers/screen query and missing-plugin
reloader handling are updated; the independent SBR engine is preserved.

Validation: 38 ordinary Python/filesystem/Qt6 cases pass; 58 skips identify 57 Maya
cases and one unavailable PySide2 case. All 57 Maya2025 cases pass; four separate
native setter cases pass. Actual release ZIPs match byte-for-byte, runtime manifests
validate, existing dedicated notices and primary bytes match, private installation
and extracted release Maya sparse-write/exact-undo smoke pass. Full dependency,
compatibility and remaining-license/interactive limits are recorded in M5_REPORT.md,
RELEASE_PROCESS.md and THIRD_PARTY.md. Stop after M5 for acceptance.

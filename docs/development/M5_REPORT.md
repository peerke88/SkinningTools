# M5 compatibility, packaging and maintenance — 2026-10-09

Parent: dc8068eb7aa00982a94646a4c08a5f38915df9dc. M4 was accepted by the
user's continuation. Work remains on the verified local refactor branch. No
GitHub push, PR, merge, publication, download or live installation was performed.
M5 is delivered for acceptance; the requested milestone sequence stops here.

## Changes and concrete responsibilities

- Maya/pluginPaths.py owns API-year detection, suffixes, exact known-owner/native
  paths and checked loading. API/interface/shared/brush adapters delegate. Loading
  is lazy, missing/failed loads propagate, and a loaded basename belonging to a
  different file is rejected. No cross-year ABI fallback is introduced.
- installCore.py owns source validation, manifest hashes, same-volume private
  staging, settings/tooltips copying, unique backup, promotion/readback and rollback.
  InstallWindow retains its public options/functions and delegates the transaction.
  The source package is preserved. Optional downloads affect staging only and accept
  GIF leaf members; no remote download was executed.
- packageCreator.py runs explicitly, using tracked allowlisted source bytes,
  deterministic ZIP metadata/order and a canonical SHA256 manifest. It includes the
  primary native plugin, preserved dependencies/notices and release documentation.
  Importing it no longer rewrites versions or deletes output. Explicit version
  stamping/debug changes affect packaged copies only; 7z is no longer required.
- The two setter builds share primary FindMaya, require an explicit SDK year,
  select C++17 for modern SDK years and retain C++11 for older years. The duplicate
  retains its CMake target name but outputs skinCommands into a setter comp layout;
  explicit install prefixes are respected. No install target or SBR rebuild ran.
- Python3 translator print/quote/dict-view failures are corrected with Python2
  fallback retained. Qt wrapper backend pairing and the Qt6 tooltip screen query
  are corrected. Unavailable plugin paths are skipped by the reloader's unload
  loop; the live reloader/new-scene action was not executed.

No weight algorithm, public Maya command flag/name, minimum Maya/Python runtime
claim or legacy asset is removed. Build/package tooling uses its separately
documented Python3.9+ contract. README/source/package documentation now describe
verified hosts, release reproducibility, native ownership and installer recovery.

## Verification

38 ordinary Python/filesystem/Qt6 cases pass: 96 discovered, 58 explicit skips
(57 Maya-only and one unavailable PySide2 case). All 57 Maya2025/Python3.11/PySide6
cases pass against delivered primary bytes; four independent duplicate setter
cases pass in another process. Both native targets configure and compile.

M5 adds 14 pure/filesystem cases, two Qt binding cases and five Maya maintenance
cases. Filesystem injections cover missing/tampered source, copy/preparation errors,
core mutation, promotion/readback errors, persistent rollback failure, original
exception preservation during staging cleanup failure, backup/overwrite, unique
backups, settings/tooltips and source preservation. Real installer UI method routing
executes with controlled checkbox/progress metadata in a disposable Maya process.

The original M4 overwrite installer body deletes a private old tree before a
missing replacement raises FileNotFoundError: D013 is reproduced, not merely inferred.
The original API version body returns C: for a relocated launcher despite API20250000.
Source inventory now has zero Python3 parse failures after D017 repair.

Qt6 core/wrapper/screen APIs and actual translation imports/lookup run inside Maya.
Actual Qt6 widgets/wrapping/screen and a source-defined translator combobox run in
a separate system-Python QApplication. PySide2 explicitly skips. The first QWidget
attempt inside Maya aborted because standalone owns QGuiApplication; that incomplete
run is not counted as passing. Initial system-test isolation/class extraction and
native override mismatches were test defects, corrected without weakening product
assertions. Failure evidence is retained in M5_ATTEMPTS.txt.

Two actual final release ZIPs are byte-identical. Runtime manifests validate; both
existing dedicated notices and primary binary bytes match source. Package README
links resolve. A private first installation verifies every runtime file. A fresh
Maya process imports the extracted release, verifies release debug mode/native
ownership and performs a sparse weight write with exact undo/redo. Artifacts remain
under ignored build/m5-verified-delivery; no user data/scenes are packaged.

M5_TEST_RESULTS.txt, M5_BUILD_RESULTS.txt, M5_BASELINE_RESULTS.txt,
M5_RELEASE_RESULTS.txt and M5_CALL_SITES.json record final evidence. Release ZIP
identity is recorded in M5_RELEASE_RESULTS.txt rather than treated as a signed
authenticity statement. Fixed-input reproducibility is scoped to the same
Python/zlib and input newline bytes.

## Native provenance and timing

Delivered primary Maya2025 skinCommands.mll SHA256:
`179FD8FDD69993A3D7B23ABD9DE046D4CD68E7651C4B11AB7E10AD189074F08B`.
It exactly matches build/m5-average/projects/Release/skinCommands.mll. The separate
build/m5-setter/Release/skinCommands.mll SHA256 is
`EFDF8C6FFAF83271088FE37B80AFDECAB7DD93A0A26E133BDD5DE2A4F37FAE91`
and stays ignored. Previous primary bytes are recoverable from the M4 parent.
Other host/platform/brush binaries are unchanged.

Delivered smoke runs: shared 1089-vertex get/set .009271-.009388 s; native smoothing .010567-.012313 s.
M4 observed .008324/.010176 s. These single-run comparisons include loader metadata
checks and are uncontrolled; no certified performance equivalence/speedup or
production memory/scale claim is made. Weight policies themselves are unchanged.

## Changed files

New runtime helpers: Maya/pluginPaths.py, installCore.py. Existing production:
Maya/api.py, interface.py, tools/shared.py; UI/qt_util.py, SkinningToolsUI.py,
translator.py, tabs/skinBrushes.py; bundled google_trans_new quote import;
packageCreator.py, packageInstaller.py, reloader.py; both setter root/project CMake
files and primary FindMaya; matching primary Maya2025 binary. Tests: maintenance,
Qt binding and Maya maintenance modules plus characterization adapter collaborators.
Documentation: README, release/dependency contracts, M5 report/evidence/inventory
and architecture/change/defect/test ledgers. No unrelated asset was removed.

## Remaining risks and acceptance boundary

Runtime Maya2022/PySide2/Python2, legacy/other OS ABI builds, interactive Maya UI/
MEL drag-drop, real network services and concurrent/active-DLL installation are
unverified. Recovery handles caught failures, not power loss between directory
renames; unique old backups remain recoverable. A persistent rollback filesystem
failure reports the old backup path rather than claiming automatic restoration.

The dependency/license audit preserves all existing dedicated/embedded notices
and records missing referenced full texts/uncertain grants. These require upstream
or owner review before external distribution; M5 makes no legal clearance claim.
Bundled Requests imports removed cgi under system Python3.13; no dependency upgrade
or Maya2027 support expansion is attempted. D018-D020 remain known, characterized
scene/importer defects outside this milestone. The independent SBR build/painting
engine remains unvalidated and intact.

Available automated maintenance evidence passes. Secondary-host/interactive release
certification and missing-license review remain outstanding; user acceptance is pending.

# M0 baseline characterization

Recorded 2026-10-09 (Asia/Tokyo). Historical M0 snapshot; accepted 2026-10-09.
See M1_REPORT.md for subsequent work. At M0, no production
code changes, supported-version changes, plugin removal, installer execution,
network publication or GitHub push is authorized by this milestone.

## Authoritative repository state

- Repository: `peerke88/SkinningTools`; origin URL is
  `https://github.com/peerke88/SkinningTools.git` (inspected locally only).
- Initial branch: `master`; clean tracked working tree.
- Baseline / master commit: `2d712f9dd844112d7457324b85e6c351e60f66b1`.
- Delivery branch: `codex/skinningtools-reliability`.
- No repository or ancestor AGENTS.md was found in the inspected paths.
- All M0 deliverables are under `tests/` and `docs/development/`. The local M0
  commit is `4d6d3f026dc5025a734274691cf2649d534a4391`.
  No remote branch or pull request is created. The user explicitly prohibited
  committing data to GitHub; all commits and evidence remain local.

## Runtime contract actually observed

| Capability | Discovery / execution evidence | Limit |
| --- | --- | --- |
| Maya 2025 | `C:\Program Files\Autodesk\Maya2025\bin\mayapy.exe`; standalone initialized, complete shared-module imports succeeded, host reports 2025 | Batch integration; interactive workflows not certified |
| Maya 2022 | No installation in Autodesk directory and no mayapy on PATH | PySide2 / secondary-host tests unavailable |
| Maya 2027 | `C:\Program Files\Autodesk\Maya2027\bin\mayapy.exe`; interpreter reports Python 3.13.9 | Discovered only; outside requested primary/secondary host validation |
| Maya Python | Maya 2025 reports 3.11.4 (MSC 1934, AMD64) | Not Python 2.7 verification |
| System Python | `C:\Users\Perry\scoop\apps\python313\current\python.exe`, 3.13.14 | No Maya module or pytest; stdlib unittest used |
| Qt | PySide6 found in system Python and Maya 2025; real QAbstractTableModel signals tested in Maya | No interactive widget/brush event tests; PySide2 not found |
| Compiler | Visual Studio 18 Community; MSVC tool folders 14.44.35207 and 14.51.36231; direct cl 19.44.35228 x64 probe ran | No native rebuild or ABI validation; cl not on PATH |
| CMake | 4.4.3 available on PATH | Existing CMake minimums/old policies not build-tested |
| Maya SDK files | Maya 2025 `include/maya/MFnSkinCluster.h` and `lib/OpenMaya.lib` exist; devkit folder contains a moved-devkit notice | Full build toolchain not certified |
| Native binary | Existing `averageWeightPerryCpp/comp/Maya2025/plug-ins/skinCommands.mll` loaded; registers SkinWeights and AverageVtxWeight | Binary/source correspondence unknown |

README claims Maya 2017+, Python 2.7 (3.7). Source retains `py23.py`, old OpenMaya,
PySide and PyQt4 branches alongside API 2.0 and PySide6. These claims have not been
removed or narrowed. `UI/qt_util.py` tries PySide6, PySide, PySide2, then PyQt4;
the bindings and their API differences must be tested separately. Native binaries
are distributed for several versions/platforms; their presence proves neither
loadability nor compatibility. Existing CMake projects set C++11, not C++17.
New M0 test tooling uses Python 3.9+ AST APIs; this changes no production minimum.

Runtime dependencies include Maya cmds/mel, API 1.0 and 2.0, a Qt binding and
matching shiboken, matching native binaries, plus bundled KDTree, profiling,
requests/translation components. Sphinx dependencies are documentation tooling.
The test suite uses no numpy/scipy, asynchronous operations or additional packages.

## Baseline findings

Real Maya checks reproduced D001, D003, D009, D011 and new D014. Host-independent
execution of unchanged source definitions reproduced D002, D005, D006, D008 and
D012 with explicitly fake host collaborators. These are separate evidence levels.
D004 did **not** reproduce in the shared writer: physical indices 0..N-1 correctly
address influences even when logical plug indices have gaps after removal/addition.
Changing this writer to logical indices solely from the original audit would risk
introducing a defect. Python smoothing and native writers use different mapping
paths and remain review targets.

The existing SkinEditor command restored exact weights through three undo/redo
cycles for two vertices and left a second mesh unchanged. This is a viable candidate
for M2 investigation, not proof of atomic multi-mesh writes, lock preservation,
failed operations or exact restoration under forced normalization.

Additional observations: `dec_undo` catches errors instead of propagating them;
native AverageVtxWeight evaluates unqualified `cmds` in Maya's global Python
namespace and logged NameError while returning success when it was absent;
UI/translator.py has Python 2 print syntax despite lazy call sites in the settings
and main window. None of these paths were corrected in M0.

## Measurement limits

Detailed results and failure classification are in TEST_MATRIX.md and
DEFECT_LEDGER.md. All baseline tests deliberately preserve current behavior;
passing tests do not certify the product as correct. Bulk read/write timings cover
9, 121 and 1089 vertices with three influences, one run each, without thresholds.
Memory use was not measured. Large production meshes, interactive brushes, Qt
selection/paste events, Maya 2022, Linux/macOS, packaging, rollback and native
build reproducibility remain unvalidated.

## Acceptance boundary

M0 provides inventory, fixture infrastructure, executed baseline coverage and a
verification plan for every registered finding. M1-M5 are not implemented.
Require user acceptance before M1. Recommended M1 remains D001, D002, D008, D009,
D011 and D012 with targeted desired-behavior regression tests. D014 warrants
explicit scope approval before adding it to that milestone. Reassess D004 in M2
using the actual API's physical-index contract and the individual callers.

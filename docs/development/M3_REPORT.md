# M3 smoothing and native reliability

2026-10-09, Asia/Tokyo. User accepted M2 by continuation. Parent local commit:
`effbb7fd2ad49f249411dc40238f002486abc03d`. Work stays on
`codex/skinningtools-reliability`; no GitHub push, PR or publication.

## Result and scope

D005 now interpolates each influence as original*(1-strength) plus neighbor
average*strength. Strength zero and isolated vertices preserve the exact original
row, including an unnormalized row; they do not prune or normalize it. D006 redo
uses the cached committed snapshot, including vertex zero and zero strength, and
remains correct after the global Python brush context switches to another mesh.

Python brush writes reuse M2 SkinEditClass preparation/application inside the
existing brush MPxCommand, retaining the five-element setWeights return format.
The brush command owns its undo entry. No new plugin or scene command is introduced.
Physical influence positions replace logical plug indices at array consumers.

Both existing native SkinWeights sources now parse each multi-use argument at
index zero with status checks, validate dimensions/finite bounded values and mesh
ownership before writes, preserve locks, propagate failures and retain original
and committed arrays. D007's suspected valid-call index failure was **not reproduced**
by the contiguous original-source build test; it is not claimed as a reproduced
corruption fix. The original build did accept an empty setter payload without
raising, which the corrected command rejects. See M3_BASELINE_RESULTS.txt.

D010 limiting and normalization now happen independently for every selected
vertex. Ties retain lower physical positions. Locked nonzero influences consume
the limit budget; an impossible locked count or normalization budget is rejected
before writing. Sparse influences, locks and modes 0/1/2 are tested. Native
AverageVtxWeight reads settings through Maya plugs, eliminating D016's implicit
global cmds dependency and pointer-to-bool conversion. No Python calls occur in
the native smoothing loop. The advertised default-selection input is now resolved
explicitly; object input still edits the entire mesh. Multiple meshes and wrong
component types are rejected instead of dropping entries silently.

Native writes apply exact arrays with normalization/max-maintenance temporarily
disabled and settings restored. They validate ordered influence/logical mappings
and vertex counts on undo/redo, verify readback and attempt rollback on failed
writes. Helpers in both existing utils.hpp files are identical. Duplicated command
implementations remain until architecture/build ownership is addressed; no plugin
was removed. Native API failure after a real partial write is not fault-injected
in this milestone; persistent rollback API failure remains a reported limitation.

## Builds and delivery

The existing averageWeightPerryCpp CMake project built against the Maya 2025 SDK.
The original source was built separately before editing. Corrected sources in both
native projects build with CMake 4.4.3, VS 18 generator, v143 MSVC 19.44.35228,
Windows SDK 10.0.26100.0 and the installed Maya 2025 headers/libraries. Original
comparison build used the default MSVC 19.51 toolset. These are local host builds,
not certification of every Autodesk-supported compiler/platform combination.

Only averageWeightPerryCpp/comp/Maya2025/plug-ins/skinCommands.mll is replaced with
the tested corrected binary. Its SHA256 is
`4D9914AC4B6962C03AEC98BAAA3F3B3012C7FC9A29F51024E7B6204B81B368B0`.
The previous bundled SHA256 was
`B9482853BB4E4D17A27E6CF6D0A1D7E8967282CFDB7C18396BFC11BB045080D9`;
it is recoverable from the parent commit and a local ignored build backup.

The skinToolWeightsCpp root CMake target is misleadingly named smooth_brush_maya
but registers only SkinWeights. Its corrected build was tested separately and
kept under ignored build/. It does not replace the separate smoothBrushRodCpp
engine or any existing lib/smooth_brush binary. Other Maya/platform binaries remain
unchanged and retain their previous behavior until rebuilt and validated.
M3_BUILD.md records exact commands and artifact provenance.

## Evidence and limits

Final evidence: 16 Python tests pass, 48 Maya 2025 tests pass using the delivered
primary binary, and four setter regressions pass against the independent duplicate
build. Invalid native setter/brush cases execute in separate fresh Maya processes
with failure/unchanged-scene assertions. Original-source numerical/invalid-input
failures and valid-parser non-reproduction are retained separately. No live user
scene is opened or saved. Interactive paint events remain unexecuted; production
callback commands are exercised directly in standalone.

The numerical matrix compares Python, C++ and an independent row reference to
1e-12 across strengths 0/.5/1, modes 0/1/2, disabled/enabled limits and multiple
vertices. Checks include locks, sparse indices, zero strength, isolated vertices,
nonconstant weights, reordered input, object/default selection, invalid values and
dimensions, cluster mismatch, settings restoration, repeated/consecutive undo/redo
and context changes. The M2 failure injection tests initially patched the imported
helper rather than Maya's registered class after M3 introduced a second class
identity; the harness now selects the registered class and both regressions pass.

Native smoothing smoke measurements for 1,089 vertices are approximately 10-11 ms
in corrected runs versus about 15 ms in the original-source run. The original run
also emitted missing-cmds errors and computes incorrect limited/normalized results,
so this is an uncontrolled cost observation, not an equivalent-result benchmark
or certified speedup. Shared bulk writes remain around 8-9 ms, consistent with M2.
Selected-row snapshots and bulk writes are retained; neighbor queries remain per
vertex through C++, without per-vertex Python calls. Memory usage was not measured.

Maya 2022/PySide2, Linux/macOS, other ABI versions, NURBS/lattice setter branches,
interactive UI strokes, native fault injection and production-scale performance
remain unvalidated. D017-D020 remain unchanged. M3 is delivered for acceptance;
stop before M4.

# M1 deterministic corrections

2026-10-09, Asia/Tokyo. User accepted M0 and requested continuation. This local
milestone addresses only D001, D002, D008, D009, D011 and D012. Nothing is sent to
GitHub. Parent commit is `4d6d3f026dc5025a734274691cf2649d534a4391`; delivery
commit is reported to the user and available with `git log -1` after commit.

## Result and implementation scope

The comparison function now retains each mesh's resolved skinCluster and returns
False for missing clusters before comparing influences or calling the pose helper.
Existing bind-pose confirmation remains. Paste now registers every modified row
and column, so the existing normalization/SkinEditor path commits the data to its
own mesh. Locked cells, headers, absent influence columns and unavailable target
columns are skipped; empty destination/copy data returns without mutation.

Both normalization status checks use absolute rounded deviation greater than
1e-6, detecting under/over totals symmetrically while accepting the tolerance
boundary. Selection is filtered against full owning transform/shape names before
vertex conversion, preventing indices from another mesh entering a row. The Qt
model emits real QModelIndex values, preserving tuple and QModelIndex input.
Linux plugin suffix in interface now agrees with api (.so).

Five production files changed, with public signatures and the existing weight
normalization/undo implementation preserved. No native binary/build, packaging,
installer, supported-version policy or architecture hierarchy changed.

## Validation and evidence

Before production edits, the new Python regression expectations failed with
4 assertion failures and 3 errors, reproducing the targeted baseline issues.
D011 had already been reproduced by a real Qt slot in M0.

Final execution: 16 Python cases pass; ordinary discovery skips 18 host cases;
all 18 execute and pass in separate Maya 2025/Python 3.11.4/PySide6 standalone.
M1_TEST_RESULTS.txt contains final command output. No live user scene opened,
reset or saved. M0 TEST_RESULTS.txt remains unchanged as historical evidence.

- D001: source tests validate cluster resolution, missing clusters and Yes/No
  out-of-pose decisions; real Maya compares single/multiple meshes, unifies
  influence sets and refuses missing clusters without changing captured weights.
- D002: source tests cover single-cell/rectangle registration, locks, headers,
  absent influences and empty destinations. Real Qt indices feed the production
  paste and normalization methods with real API/plugin writes to two meshes and
  multiple vertices. Captured locked influence stays unchanged; untouched vertex
  weights remain unchanged; two undo calls restore both exact snapshots and two
  redo calls restore committed snapshots. Existing per-mesh undo entries retained.
- D008: executes both production source conditions at totals 0/.5/1/1.5 and
  positive/negative tolerance boundaries. Full UI color painting unexecuted.
- D009: real Maya checks separate vertex IDs, shape/transform aliases, component
  ranges, mixed object/component selection and empty selection.
- D011: real PySide6 model slot checks valid indices, correct row/column/model,
  both accepted input forms. The initial second-cell test had an invalid index
  because the fixture exposed only one display column; corrected the fixture,
  not the production column-count implementation.
- D012: resolver executions agree for Windows/Darwin/Linux; actual Linux binary
  loading is unexecuted on this Windows host.

## Remaining findings and limits

New D018 is reproduced: the existing checkBasePose helper returns False for an
untouched bind whose dagPose query returns None. The helper is unchanged because
it is outside the accepted six corrections. Real comparison integration supplies
the confirmation answer explicitly using a patched dialog; source tests separately
exercise pose decisions. These tests do not certify bind-pose correctness or
interactive dialog behavior. Investigate D018 before relying on automatic pose
decisions, with explicit approval for its correction scope.

D003 direct API writes, D005/D006 smoothing and D014 list-input failures remain
characterized, not fixed. M2 still needs failure atomicity, reliable undo contracts,
all lock/normalization modes and other-writer index audits. D004 was not reproduced
in the shared physical-index path. Maya 2022/PySide2, complete interactive Qt events,
native source rebuilding, malformed native arguments and real Linux/macOS remain
unvalidated. No production performance certification is claimed.

Stop after this local milestone for acceptance before M2.

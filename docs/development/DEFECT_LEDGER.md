# Defect verification ledger

Historical M0 evidence is retained; M1 status updates identify corrected targets.
Status is not acceptance. Runtime evidence
is explicitly distinguished from isolated Python execution and source inspection.
D001-D013 retain the supplied register; D014-D018 are additional observations,
not authorized milestone expansion. All remain unchecked until accepted.

- [ ] D001

    Category: Product defect

    Severity: Critical

    Source location: Maya/tools/skinCluster.py:39 forceCompareInfluences

    Observed behavior: Resolved cluster is discarded; undefined skinClusterName raises NameError; dec_undo suppresses it and returns None.

    Expected behavior: Resolve each mesh cluster and validate its bind pose before comparing/mutating influences.

    Reproduction: Use disposable valid/missing clusters, multiple meshes and both in/out-of-pose settings; assert result, unchanged unrelated poses and propagated failure.

    Root cause: Missing assignment before checkBasePose.

    Test coverage: Isolated source and real Maya 2025 call; bind pose acceptance scenarios deferred to M1.

    Implementation status: Fixed in M1. Retains resolved cluster names; missing cluster returns False before comparison. Pose/confirmation branches tested with explicit source collaborators; real Maya cluster comparison and missing input pass. D018 remains separate.

    Verification status: Tested in M1; awaiting acceptance. Historical observed behavior above is M0 evidence.

- [ ] D002

    Category: Product defect

    Severity: Critical

    Source location: UI/weightEditor/weightEditor.py:317 pasteCells

    Observed behavior: Values change in memory, but rowsToUpdate stays empty and cellDict has no new row.

    Expected behavior: Paste commits the intended cells to each corresponding skinCluster with locks and undo/redo preserved.

    Reproduction: Single/multiple cells and vertices, multiple meshes, locked influence; compare before/after scene weights then exact undo/redo.

    Root cause: cellDict starts empty; row registration only occurs if the row is already in cellDict; missing initialization branch.

    Test coverage: Two source-method cases (ordinary and locked cell); Qt/Maya complete paste workflow still unverified.

    Implementation status: Fixed in M1. Registers changed rows/columns; skips empty/header/missing-influence/unavailable column targets. Source single/rectangle checks and real two-mesh paste/locks/exact undo-redo pass.

    Verification status: Tested in M1; awaiting acceptance. Historical observed behavior above is M0 evidence.

- [ ] D003

    Category: Product defect

    Severity: Critical

    Source location: Maya/tools/shared.py:824 setWeights and its callers

    Observed behavior: MDoubleArray input mutates real weights after flushUndo while undo queue stays empty.

    Expected behavior: All committed weights support exact original/committed restoration with failure-safe writes.

    Reproduction: Single/multiple vertices and meshes, consecutive/repeated undo/redo, inject a failure between meshes; snapshot weights/settings/locks/indices before and after.

    Root cause: Direct MFnSkinCluster mutation lacks MPxCommand-owned undo entry; dec_undo cannot supply one.

    Test coverage: Real direct-write test; existing SkinEditor two-vertex exact repeated undo/redo characterization.

    Implementation status: Unchanged; M0 characterization only.

    Verification status: Reproduced. Real Maya 2025; no M2 redesign implemented.

- [ ] D004

    Category: Unverified hypothesis

    Severity: Critical

    Source location: Maya/tools/shared.py:779 _getSetData

    Observed behavior: Sequential array values are physical indices. Sparse logical indices after removed/added influences did not corrupt the tested shared write.

    Expected behavior: Translate the appropriate index space for each API/plug consumer; never interchange logical plug and physical array indices.

    Reproduction: Compare physical order, logical map and influence names for contiguous/sparse/removed/added/locked cases; audit other writers separately.

    Root cause: Original hypothesis conflates index spaces; no shared-writer root cause established.

    Test coverage: Real sparse shared-write test passed with distinct per-influence weights; lock fixture captured only.

    Implementation status: Unchanged; M0 characterization only.

    Verification status: Unverified. Not reproduced for shared.py in Maya 2025. Do not replace physical indices with logical indices on audit evidence alone.

- [ ] D005

    Category: Product defect

    Severity: High

    Source location: Maya/plugin/averageWeightPlugin.py:47 AverageWghtCtx.calcWeights

    Observed behavior: With two influences/two neighbors and normalization off, strength zero produces half the original weights. Empty neighbor array produces zeros.

    Expected behavior: original*(1-strength)+average_neighbors*strength, explicit zero-neighbor policy, valid normalization and per-vertex limits.

    Reproduction: Strength 0/1/.5; boundary/isolated vertices; enable/disable normalization/max influence limiting and sparse influences; compare reference and Maya output.

    Root cause: Original contribution divided by flattened neighbor-weight length rather than component count; normalized output can mask scaling.

    Test coverage: Source execution endpoints/intermediate/normalization/empty neighbors; real callback deferred.

    Implementation status: Unchanged; M0 characterization only.

    Verification status: Reproduced. Python algorithm executed; full Maya brush not validated.

- [ ] D006

    Category: Product defect

    Severity: High

    Source location: Maya/plugin/averageWeightPlugin.py:158 AverageWghtCtxUpdate.redoIt

    Observed behavior: Redo skips valid vertex zero and zero-strength edits.

    Expected behavior: Vertex zero behaves like every valid vertex; redo reapplies exactly committed state.

    Reproduction: Paint vertex 0 and positive vertex at strength 0/.5/1, undo then redo; assert callback and exact weights.

    Root cause: Falsy checks on self.index and self.value reject legitimate zero values.

    Test coverage: Source redo method: two rejected cases and positive control.

    Implementation status: Unchanged; M0 characterization only.

    Verification status: Reproduced. Python definition executed; complete paint command deferred.

- [ ] D007

    Category: Unverified hypothesis

    Severity: High

    Source location: Maya/plugin/skinToolWeightsCpp/projects/skinweights.cpp:81; averageWeightPerryCpp/projects/skinweights.cpp:122

    Observed behavior: Both sources get the ith multi-use flag argument list then call arg.asDouble(i); flag syntax supplies one double per use.

    Expected behavior: Parse every weight argument from its own list at the correct index; reject malformed/missing inputs before mutation.

    Reproduction: In a separate batch process per unsafe case, set a distinctive flattened array with several flag uses; compare all values, bad argument failure, unchanged scene and undo/redo. Repeat both native sources/builds.

    Root cause: Source suggests intra-list index should be zero; no rebuilt or setter runtime confirmation yet.

    Test coverage: Native binary load/query/basic AverageVtxWeight smoke only; parser finding source-inspected.

    Implementation status: Unchanged; M0 characterization only.

    Verification status: Unverified. Source evidence only; native setter not run and binaries not rebuilt.

- [ ] D008

    Category: Product defect

    Severity: High

    Source location: UI/weightEditor/weightEditor.py:648 and :885 normalization status checks

    Observed behavior: Both conditions accept under-normalized .5 totals while flagging over-normalized 1.5 totals.

    Expected behavior: Detect absolute total deviation greater than 1e-6 in both directions.

    Reproduction: Rows totaling 0/.5/1/1.5 and values within/at/outside tolerance; check initial load and post-edit UI flags.

    Root cause: Comparison uses signed sum-minus-one rather than absolute difference.

    Test coverage: Both actual source AST condition expressions executed for .5/1/1.5.

    Implementation status: Fixed in M1. Both checks flag absolute deviation greater than 1e-6, tested at zero/under/over totals and tolerance boundaries.

    Verification status: Tested in M1; awaiting acceptance. Historical observed behavior above is M0 evidence.

- [ ] D009

    Category: Product defect

    Severity: High

    Source location: Maya/tools/apiWeights.py:54 selectedVertIds; editor getSkinWeights call site :615

    Observed behavior: Selection A.vtx[0], B.vtx[7] returns [0,7] for either requested node.

    Expected behavior: Component identity includes mesh and vertex; each requested mesh receives only its own IDs.

    Reproduction: Select different indices across two meshes, overlapping IDs, transform/shape/full-path aliases, ranges and object selections; verify editor rows per mesh.

    Root cause: node argument ignored; global vertices converted to bare integer IDs.

    Test coverage: Source isolation and real Maya two-mesh selection test.

    Implementation status: Fixed in M1. Filters selection using canonical owning transform/shape before index extraction. Real Maya aliases, ranges, mixed object/components and empty selection pass.

    Verification status: Tested in M1; awaiting acceptance. Historical observed behavior above is M0 evidence.

- [ ] D010

    Category: Unverified hypothesis

    Severity: High

    Source location: Maya/plugin/averageWeightPerryCpp/projects/averagevtxweight.cpp:233-282

    Observed behavior: Source selects top mMaxinf values across flattened mNewValues; normalization also sums flattened result.

    Expected behavior: Limit and normalize independently for every vertex.

    Reproduction: Give two or more vertices disjoint strongest influences, enable max limits 1/2, vary normalization, inspect each vertex sum/count; compare with reference and undo/redo.

    Root cause: Source limit loop sits after vertex result accumulation and uses whole array length; runtime enabled-limit behavior unconfirmed.

    Test coverage: Source inspection; constant single-vertex native smoke does not verify this.

    Implementation status: Unchanged; M0 characterization only.

    Verification status: Unverified. Native per-vertex numerical reproduction and binary/source correspondence deferred.

- [ ] D011

    Category: Product defect

    Severity: Medium

    Source location: UI/weightEditor/weightsTableModel.py:229 setData

    Observed behavior: Maya 2025 PySide6 accepts tuple arguments but emits two invalid QModelIndex instances; stored value changes.

    Expected behavior: Emit valid top-left/bottom-right model indices for edited cell with appropriate roles.

    Reproduction: Connect a real dataChanged slot, edit via QModelIndex and tuple inputs, assert row/column/model/validity and view update under each Qt binding.

    Root cause: Tuple has no model/index identity; signal conversion yields default invalid indexes.

    Test coverage: Real PySide6 model emission with slot; initial TypeError assumption corrected.

    Implementation status: Fixed in M1. Emits self.index(row,col); real PySide6 verifies both input forms and valid model/row/column identity.

    Verification status: Tested in M1; awaiting acceptance. Historical observed behavior above is M0 evidence.

- [ ] D012

    Category: Product defect

    Severity: Medium

    Source location: Maya/interface.py:569 getPluginSuffix; Maya/api.py:113

    Observed behavior: interface returns .bundle for Linux while api returns .so.

    Expected behavior: Resolve correct platform suffix and deterministic matching plugin identity.

    Reproduction: Execute each resolver for Windows/macOS/Linux; real host plugin paths and version match, multiple candidate files, unavailable plugin errors.

    Root cause: Duplicated suffix functions disagree on Linux; interface uses first directory-walk match.

    Test coverage: Source functions executed with platform collaborators, agreement on Windows/macOS.

    Implementation status: Fixed in M1. Interface Linux suffix corrected to .so; both functions agree under Windows/macOS/Linux simulated platforms. Real Linux loading unavailable.

    Verification status: Tested in M1; awaiting acceptance. Historical observed behavior above is M0 evidence.

- [ ] D013

    Category: Unverified hypothesis

    Severity: High

    Source location: packageInstaller.py:172 install overwrite branch

    Observed behavior: Source rmtree removes existing installation before later replacement move/validation; backup branch is optional.

    Expected behavior: Install a verified replacement with recoverable old installation on any failure.

    Reproduction: Use temporary installation trees only; inject invalid archive/missing files/download/extract/move failure; assert old tree survives or is restored byte-for-byte.

    Root cause: No staging/verification/rollback transaction established in inspected overwrite path.

    Test coverage: Source inspection only; live installer explicitly not executed.

    Implementation status: Unchanged; M0 characterization only.

    Verification status: Unverified. Installer failure not reproduced; M5 target.

- [ ] D014

    Category: Product defect

    Severity: High

    Source location: Maya/tools/shared.py:835 setWeights list input

    Observed behavior: Python list input raises TypeError: MDoubleArray: No matching constructor found; original scene snapshot unchanged.

    Expected behavior: Documented list and MDoubleArray input forms both work after validation.

    Reproduction: Same valid dimensions/values using list/array; invalid dimension/nonfinite arrays rejected before mutation; compare outputs and undo after later corrections.

    Root cause: OpenMaya.MDoubleArray(len(weightData)) has no matching Maya 2025 constructor; typed array branch works.

    Test coverage: Real list-input exception and unchanged full snapshot test.

    Implementation status: Unchanged; M0 characterization only.

    Verification status: Reproduced. New M0 discovery only; seek explicit approval to add correction scope.

- [ ] D015

    Category: Product defect

    Severity: High

    Source location: Maya/tools/shared.py:27 dec_undo

    Observed behavior: Errors are swallowed; chunks close but callers receive None and lose exception propagation.

    Expected behavior: Close chunks in finally while preserving original unrecoverable exceptions and applying explicit rollback policy.

    Reproduction: Injected ValueError with debug on/off, failed Maya operation after first mutation; assert same exception and chunk closure, then scene integrity.

    Root cause: Broad except logs only when debug is enabled and does not re-raise.

    Test coverage: Isolated decorator injection and real D001 decorated call.

    Implementation status: Unchanged; M0 characterization only.

    Verification status: Reproduced. New M0 observation; relevant to M2, no correction.

- [ ] D016

    Category: Product defect / implicit runtime dependency

    Severity: High

    Source location: Maya/plugin/averageWeightPerryCpp/projects/averagevtxweight.cpp:77-94

    Observed behavior: Without cmds in Maya global namespace, native evaluations logged NameError but command returned success in first smoke run.

    Expected behavior: Explicitly access settings and propagate unsuccessful evaluations/API errors.

    Reproduction: Fresh standalone without global cmds, capture command error/status and scene snapshot; repeat with explicit dependency and max/normalization settings.

    Root cause: Unqualified Python cmds string evaluations, ignored status, and casting result1.asChar() pointer to bool are source concerns.

    Test coverage: Actual 2025 bundled binary emitted NameError in unseeded smoke; seeded constant numerical smoke passes.

    Implementation status: Unchanged; M0 characterization only.

    Verification status: Reproduced. Binary dependency reproduced; pointer-cast behavior/source equivalence still unverified. No added implementation scope.

- [ ] D017

    Category: Product compatibility defect

    Severity: Medium

    Source location: UI/translator.py:142; UI/SkinningToolsUI.py:272; UI/dialogs/settingsDialog.py:61

    Observed behavior: Python 3 AST parsing fails at print inText, self.getLangValue(); settings/main-window translation actions lazily import the module.

    Expected behavior: Keep approved legacy support while enabling translation import in supported Python hosts.

    Reproduction: Import translation module in disposable host, trigger lazy translation UI path; verify syntax and dependencies for intended legacy and primary environments.

    Root cause: Python 2 print syntax remains in reachable optional source.

    Test coverage: Inventory parse_failures explicitly records Python 3 SyntaxError; no interactive translation run.

    Implementation status: Unchanged; M0 characterization only.

    Verification status: Confirmed. Source syntax confirmed; UI path runtime unverified; out of current correction scope.
- [ ] D018

    Category: Product defect, newly discovered during M1.

    Severity: High.

    Source location: Maya/tools/skinCluster.py:16 checkBasePose.

    Observed behavior: Fresh Maya 2025 untouched bind returns None from
    cmds.dagPose(pose, query=True, atPose=True), but helper returns False and
    comparison can prompt for an out-of-pose confirmation.

    Expected behavior: Distinguish at-pose and out-of-pose bindings correctly.

    Reproduction: Create a disposable mesh/joint binding, query its pose/helper;
    repeat after moving a joint, multiple poses, missing pose and fallback.

    Root cause: Existing helper treats non-None dagPose result as at-pose;
    broader pose/fallback semantics require separate review.

    Test coverage: Real Maya test_D018_bind_pose_helper_misclassifies_untouched_bind;
    fresh-process diagnostic returned POSE ['bindPose1'] None False.

    Implementation status: Unchanged; outside the six accepted M1 corrections.

    Verification status: Reproduced; no complete bind-pose correctness claim.

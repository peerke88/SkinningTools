# M2 weight-write contract

The owner is the existing `Maya/plugin/SkinEditPlugin.py` SkinEditor MPxCommand.
`shared.setWeights(inMesh, weightData)` retains its signature and delegates to
the additive `shared.setWeightsBatch(requests)`. No plugin was added or removed.

## Requests and routing

| Caller | Route | Normalization |
| --- | --- | --- |
| Existing shared.setWeights callers | One full-mesh batch request | True |
| Table edits and multi-mesh paste | One batch of explicit component requests | True |
| WeightsManager.importData | Stage every mesh's weights, then one batch | True |
| api.setSkinWeights without influenceIndices | One full-mesh batch, validates supplied cluster | False |
| Legacy cmds.SkinEditor | Existing mesh/skin positional arguments and vid/jid/nw/ow flags | True unless n=False |

A full-mesh request contains `mesh`, flat `weights`, optional `skinCluster` and
optional boolean `normalize`. The wrapper resolves all vertices and influences.
An explicit request additionally requires `skinCluster`, `vertices` and
`influences`. An empty wrapper batch is a no-op. The command's additive
`bt/batchWeights` flag accepts the JSON list; `n/normalize` controls legacy flags.

Weight rows follow the supplied vertex order and columns follow the supplied
influence order. Influence indices are **physical positions** in
MFnSkinCluster.influenceObjects(), never sparse logical matrix plug indices.
The command captures ordered influence names and logical indices to detect
mapping changes, while passing all physical positions to API setWeights.
Vertices are sorted into the Maya component order and input rows remapped.
Component identity includes skinCluster, geometry object and vertex ID.

All requests are prepared before the first mutation. The command rejects wrong
mesh/skin ownership, duplicate or out-of-range indices, overlapping requests,
wrong dimensions, nonfinite values and values outside [0,1]. Existing per-value
weights must also be finite in [0,1]; under/over-normalized totals are permitted.
Caller ow/originalWeights remains accepted with a dimension check, but actual
scene weights own undo. The full selected rows are captured, including columns
outside the requested subset. Unselected vertices remain untouched.

## Locks, normalization and settings

Locked influence values are retained from the original scene. Requested changes
to them are ignored. With normalize=True, unlocked values scale into the remaining
1-minus-locked-total budget. A locked total above 1+1e-6 is rejected. A zero unlocked
total with a partial locked budget is rejected; an entirely zero row without
locked contributions stays zero. With normalize=False, merged values are retained
without scaling. Influence lock attributes are never changed.

For each exact bulk write, normalizeWeights is temporarily set to zero and
maintainMaxInfluences to False through API plugs, then restored in finally.
This is required because Maya 2025 normalization mode 1 can change an array even
when API normalize=False. Locked or connected settings requiring temporary
control are rejected before any write. Max-influence pruning remains the caller's
algorithm; the exact writer deliberately does not prune snapshots. Restoration
of original/committed arrays must not depend on later normalization calculations.

## Undo, redo and failure

A successful batch creates one undoable MPxCommand. Undo restores exact original
arrays; redo restores exact committed arrays. Before every application, including
undo/redo, vertex counts, influence signatures, dimensions, values and controllable
settings are checked. Readback must equal the intended array exactly.

If any write fails, all attempted writes, including the partially changed failing
mesh, are restored in reverse order to pre-application snapshots and verified.
The original exception propagates. If the underlying API also fails persistently
during rollback, an explicit rollback error is emitted; no unconditional recovery
claim is made for that situation. Maya reports undoIt failures through its error
channel rather than necessarily raising from cmds.undo. Tests capture that channel.

dec_undo closes chunks in finally and now propagates exceptions. It groups recorded
commands; it does not make arbitrary scene changes transactional.

## Boundary limits

Atomicity covers one prepared weight batch. Skin binding creation, remapping,
influence edits, arbitrary decorated tool workflows and successive separate batches
are not whole-scene transactions. The importer test isolates geometry matching and
uses existing clusters; D019/D020 remain defects in closest-search paths.
Existing skinPercent, copySkinWeights, Python brush and native command paths remain
in the baseline architecture and require their scheduled milestones. No claim is
made that every production workflow already uses this owner.

Python/Maya minimum versions and public signatures are unchanged. Runtime evidence
is Maya 2025/Python 3.11/PySide6 only; secondary-host and interactive compatibility
are unvalidated. Full-array capture, JSON preparation and readback add time/memory
cost; production-scale capacity requires separate measurement.

## M3 owner update

The Python brush now reuses SkinEditClass validation and exact application inside
its existing callback MPxCommand; the callback owns its cached before/after arrays.
Native SkinWeights and AverageVtxWeight use corresponding checked native helpers,
with the same physical-index/exact-restoration/settings-control rules. Algorithms
remain separate until M4; brush/native smoothing now enforce limits per row.
Only the Maya2025 primary bundled native binary is rebuilt. Earlier boundary
limits for arbitrary whole-scene changes and persistent rollback failures remain.

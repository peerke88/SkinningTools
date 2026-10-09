# Existing architecture and execution inventory

This describes the baseline, not a new package hierarchy. `CALL_SITES.json` is a
generated inventory of calls to weight writes/queries, attribute changes,
skinCluster operations, plugin loads and undo functions across first-party Maya
and UI Python files. Each record includes enclosing scope, line and arguments.
Query-only calls are retained to distinguish them from mutations. AST parse
failures are explicit. Calls dispatched indirectly, through MEL strings or C++
require the manual inventory below; the JSON is not a claim of complete dynamic
reachability. Generate it with `python tests/inventory.py`.

## Entry points and workflow routing

| Entry / action | Existing route | Write boundary |
| --- | --- | --- |
| Release launch | README -> UI/SkinningToolsUI.showUI; root tool() -> same | Main UI initializes tabs, editor and selection state |
| Development reload | reloader.unload; defaults newScene=True | Can force a new scene and unload plugins; not used by tests |
| Main vertex/bone buttons | UI/tabs/vertAndBoneFunction.py signals -> Maya/interface.py | Interface interprets ordered selection, dispatches tools |
| Copy mesh skin | interface.copySkin -> skinCluster.transferSkinning/transferClosestSkinning -> execCopySourceTarget | copySkinWeights and shared.setWeights |
| Copy/swap vertex | interface.copyVtx/switchVtx -> Copy2MultVertex/switchVertexWeight | cmds.skinPercent |
| Average / unify shells | interface.avgVtx/unifyShells/setHardShellWeight -> AvarageVertex/hardSkinSelectionShells or vertexWeight | skinPercent; Python normalization/calculation in tools |
| Influence operations | interface.moveBones/removeJoint/addNewJoint -> joints.BoneMove/BoneSwitch/removeJoints/addCleanJoint | shared.setWeights, skinPercent, skinCluster edit/add/remove, scene attributes |
| Max influences | interface.setMaxInfl/getMaxInfl -> skinCluster.setMaxJointInfluences/getVertOverMaxInfluence | skinPercent prune and queries |
| Table editor | SkinningToolsUI.__componentEditSetup loads SkinEditPlugin; WeightEditorWindow.getSkinWeights -> ApiWeights.getData/selectedVertIds | Editing/copy/paste -> tryNormalizeWeights -> cmds.SkinEditor |
| Slider editor | UI/ControlSlider/vertexinfluenceeditor -> Maya/api.skinPercent alias | cmds.skinPercent directly from widget |
| Marking menu | UI/markingMenu -> interface.doSkinPercent -> skinCluster.doSkinPercent | relative/absolute skinPercent writes |
| File weight manager | UI/tabs/weightsUI -> WeightsManager.gatherData/importData using ApiWeights and remap dialogs | shared.setWeights after mapping; not transactional |
| Hold/fetch and toolbar | UI/tabs/mayaToolsHeader -> interface.skinWeight/vertexWeight and holdFetch | shared.setWeights or cmds scene commands |
| Initial weights | UI/tabs/initialWeightUI -> initialWeight.setInitialWeights | buildSkinCluster then shared.setWeights |
| Soft selection | UI/tabs/softSelectUI -> softSelectWeight.setSkinWeights | cmds.skinPercent per vertex, influence addition |
| Vertex matcher | UI/tabs/vertexWeightMatcher | cmds.SkinWeights query/write or cmds.copySkinWeights |
| Python smooth paint | interface.paintSmoothBrush/smooth -> averageWeightPlugin paint callbacks | paintAverageWghtCtxInitialize/Update -> AverageWghtCtx.setWeights |
| Native neighbor smoothing | skinCluster.neighbourAverage; Maya/SmoothBrush/globalskinsmooth.GlobalSkinSmooth callback | cmds.AverageVtxWeight |
| Smooth/relax brush | UI/tabs/skinBrushes builds artUserPaintCtx command strings | SBR_brush and SBR_cache_manager, smoothBrushRodCpp |
| Install | dragDropInstall.mel -> packageInstaller | download/extract/move/delete installation; not exercised |
| Package generation | packageCreator.py top-level execution | rewrites version/date and recreates package directory; never import for testing |

## Mutation and undo boundaries

| Path | Current behavior | Undo ownership / risk |
| --- | --- | --- |
| shared._getSetData/getWeights/setWeights | Full mesh component and physical influence array; API 2.0 bulk write | No command-owned snapshot/undo entry. Tested; Python list branch fails in Maya 2025 |
| skinCluster.py callers | execCopySourceTarget:254, freezeSkinnedMesh:758 -> shared; other operations skinPercent/copySkinWeights | Many dec_undo wrappers group cmds but cannot add API writes to undo |
| joints.BoneMove:379 | shared bulk write before further scene/influence operations | dec_undo grouping does not make API weights undoable |
| weightsManager.importData:197 | mapped bulk weights -> shared | No reliable atomic all-mesh rollback established |
| initialWeight.setInitialWeights:186 | skin creation plus shared weights | Scene creation and weight mutation can have different undo ownership |
| interface.skinWeight.setSkinWeights:718 | saved full weights -> shared | Same direct-write concern |
| Python SkinEditPlugin | MPxCommand stores caller-provided original/new arrays; physical joint IDs from editor | Undo/redo writes normalize=True. Tested only contiguous two-vertex case; caller originals trusted |
| averageWeightPlugin | MPxCommand snapshots one component's weights; calcWeights then API write | redo recomputes; zero index/value rejected. Influence IDs derived from logical indices; sparse/max-limit cases need validation |
| Native SkinWeights (two copies) | Multi-use newWeights flag, bulk get/set, original weights captured by API | Command undo; duplicate source parsing issue, unchecked return paths. Not rebuilt |
| Native AverageVtxWeight | Cache component results; neighbors gathered per vertex | Command undo; limiting/normalization applied to flattened cached result in source |
| Native SBR_brush | toolbox_maya/data/maya_skin_weights.cpp:273 calls MFnSkinCluster.setWeights | cmd_swe_brush.cpp redoIt/undoIt owns snapshots; mayaCheck around API write. Runtime brush not tested |
| cmds.skinPercent | tools skinCluster/joints/softSelectWeight, interface.vertexWeight, UI slider, Maya/api setter | Maya built-in undo; normalization/lock settings vary |
| cmds.copySkinWeights / skinCluster edits | transferSkinning, matcher, influence add/remove, binding | Maya built-in undo; whole operation transaction not established |

The generated inventory also includes bind matrices, influence locks, cluster
attributes, mesh history and other setAttr calls. Weight reads include API getWeights,
skinPercent query mode and weightList attribute queries. There is no discovered
first-party Python direct assignment to weightList.weights via setAttr; matrix
weightIn values in shared are transform blending, not skinCluster weights.

`shared.dec_undo` opens a chunk, catches exceptions (debug warning only), and
closes in finally. It suppresses recoverable and unrecoverable exceptions alike.
`Maya/api.startUndo/endUndo` exposes separate manual boundaries. A chunk alone
does not supply exact rollback or atomic multi-mesh behavior. Partial changes are
not automatically reverted when a later step fails.

## Active, conditional and legacy implementations

- Active source call sites exist for shared bulk writes, SkinEditor, SkinWeights,
  skinPercent, AverageVtxWeight, Python paint commands and SBR native commands.
  A call site is evidence of intended use, not proof each UI route runs successfully.
- Main SkinningToolsUI imports the skinBrushes tab only when debug is enabled;
  other brush launch paths also exist. These are conditional, not removable.
- averageWeightPerryCpp registers both AverageVtxWeight and SkinWeights;
  skinToolWeightsCpp/projects registers only SkinWeights. Duplicate SkinWeights
  implementations persist and may collide if both binaries are loaded. Maya/api
  still computes a skinToolWeightsCpp path; there is no matching 2025 binary in
  that comp tree, while averageWeightPerryCpp has one. Its intended 2025 binary
  ownership should be established before consolidation.
- skinToolWeightsCpp top-level CMake calls the project smooth_brush_maya and has
  smooth-brush binaries, while projects/ holds SkinWeights source. This divergence
  requires build provenance investigation before regenerating binaries.
- smoothBrushRodCpp is a substantial independent brush engine with Eigen and
  toolbox libraries. Duplicated smooth_brush binaries also occur under
  skinToolWeightsCpp/lib. Preserve both until loader/build ownership is reviewed.
- API 1.0 imports, PySide/PyQt4 branches, py23 helpers and old-version binaries
  indicate legacy compatibility. No removal is justified by M0 evidence.
- UI/translator.py is Python 2 syntax and lazily imported by translation actions;
  it is not proven unused. JSON reports its Python 3 parse failure.

## Coupling and duplication

Maya/tools/shared imports Qt/UI utils and profiling helpers. ApiWeights imports
interface and UI utilities. UI table and slider widgets own normalization and
weight writes; tools and plugins each implement blending/normalization too.
UI/utils.remapClosestPoints combines geometric mapping and weights. Influence
mapping varies: physical editor columns/shared write arrays, logical plug indices
in joint utilities and smoothing plugins. Maya/api and interface duplicate version,
suffix and loader resolution; Linux suffix disagreement is tested. interface scans
directories and returns the first match rather than an explicit plugin identity.

The target responsibility split can start with these existing modules. Investigate
reusing SkinEditor for M2 before introducing any command/plugin. M4 can extract
deterministic weight math after contracts and regression coverage are established;
no such restructuring is done in M0.

## M2 routing update

The tables and CALL_SITES.json above preserve the M0 baseline. Current shared,
full-mesh API, table and staged importer weight writes route through the existing
SkinEditor command. See WEIGHT_WRITE_CONTRACT.md for the current ownership map
and exact atomicity boundaries. Native/brush/skinPercent paths remain separate.

## M3 routing/build update

Python brush callback MPxCommands reuse M2 SkinEditClass preparation/application
and own exact cached undo/redo. Native AverageVtxWeight remains a native owner,
using checked plugs, physical indices, per-row math and exact write helpers.
Both native SkinWeights copies are patched; helpers intentionally remain duplicated
pending M4. Maya2025 averageWeightPerryCpp bundled binary is rebuilt and validated.
skinToolWeightsCpp root target registers only SkinWeights despite being named
smooth_brush_maya; it was built/tested separately without overwriting any brush
engine binary. See M3_BUILD.md and M3_REPORT.md for provenance and deferred hosts.

## M4 current ownership

Earlier sections retain historical observations. Current Python calculations
live in Maya/tools/weightMath.py, importable without Maya/Qt. Batch/brush share
normalization; blending/limits, table priority and slider solvers each have a named
implementation. Distinct policies remain distinct; UI classes gather inputs and
apply results.

Maya/tools/weightWrite.py owns influenceMapping (DAG, physical position, logical
plug), geometry resolvers and WeightBatch preparation/exact application/rollback.
Shared, ApiWeights and Python brush consume its layout. SkinEditClass inherits
the writer and owns command undo; paint callbacks use WeightBatch directly and
own their cached undo/redo. Table edits submit one grouped batch and discard an
unused original-weight cache.

skinToolWeightsCpp/projects includes authoritative native setter/helpers from
averageWeightPerryCpp/projects. Both builds/registrations remain; smoothBrushRodCpp
stays separate. Maya built-in writes retain their own ownership and semantics.
Loader/build naming is M5 work. M4_REPORT.md records current ownership and limits;
M4_CALL_SITES.json is the updated inventory.

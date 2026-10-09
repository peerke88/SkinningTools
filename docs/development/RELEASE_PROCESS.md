# Local release, install and compatibility contract — M5

## Runtime evidence and retained support

README's historical Maya2017+/Python2.7 support claim is retained, not expanded
into a certification of every version. The tool is Maya-only; its root package
imports UI/Maya eagerly. Supported-feature availability also requires matching
native binaries. No older binary, dependency or legacy Qt branch is removed.

| Environment | Evidence | Boundary |
| --- | --- | --- |
| Maya2025 / Python3.11.4 / PySide6 / Windows x64 | Full disposable Maya suite, core Qt APIs/imports, native builds and commands | Interactive Maya window/strokes/MEL drag-drop not executed |
| System Python3.13.14 / PySide6 | Pure/filesystem/package tests and real Qt6 widget/wrapper/screen/combobox check in a separate process | Qt module loaded directly and translator combobox compiled from source; full Maya package is not imported |
| Maya2022 / PySide2 | Source branches retained; real Qt2 test explicitly skips because binding/host absent | Not runtime validated |
| Maya2017-2020 / Python2 / PySide / PyQt4 | Existing branches/binaries retained; new runtime helpers use Python2-compatible syntax | No runtime certification; builds retain C++11 policy for older SDK years |
| Linux/macOS | Exact suffix/year/casing resolution tested with directory fixtures | No ABI/native/UI execution |
| Maya2027 / Python3.13 | Installation previously discovered, outside requested host pair | Bundled Requests imports removed stdlib cgi; no matching 2027 plugins; not certified |

Maya standalone owns a QGuiApplication, so QWidget construction aborted a private
test process. Widget checks therefore run in separate system Python with a real
QApplication. Core/screen/import checks still run inside Maya. No user scene or
installed script directory is modified by the test harness.

## Native discovery and builds

Maya/pluginPaths.py is authoritative: API year is the validated four-digit prefix
of apiVersion (shorter legacy and modern encodings),
independent of launcher path/update text. Suffixes are Windows .mll, Darwin .bundle
and Linux .so. Native discovery only inspects known owners at the exact host year:

- skinCommands: averageWeightPerryCpp/comp/MayaYEAR/plug-ins first, then the
  legacy skinToolWeightsCpp/comp/MayaYEAR/plug-ins setter where available.
- smooth_brush_maya: smoothBrushRodCpp/lib/mayaYEAR/release only. Same-named
  files in skinToolWeightsCpp/lib have uncertain provenance and are preserved
  but are not fallback brush owners.

Folder/file casing is matched consistently; ambiguous matches fail. Missing files
do not trigger a cross-year fallback. Decorators resolve lazily and propagate load
failure before the operation. If another file already owns the same basename,
loading fails explicitly rather than silently using a different binary.

The two setter projects now share the primary FindMaya module. Specify the target
year explicitly; it is not guessed from the launcher. C++17 is selected for SDK
years 2022+, C++11 for older years; CMAKE_CXX_STANDARD remains overridable and is
required. The duplicate keeps its historical CMake target name but outputs
skinCommands, with explicit source files and a comp/MayaYEAR/plug-ins install
destination. An explicit CMAKE_INSTALL_PREFIX is respected. Do not install the
duplicate over the primary: it registers only SkinWeights, whereas the primary
also registers AverageVtxWeight. No install target is needed for validation.

Verified local Windows recipe (Maya2025 SDK, CMake4.4.3, VS18 generator, MSVC v143):

```powershell
cmake -S Maya/plugin/averageWeightPerryCpp -B build/m5-average -G 'Visual Studio 18 2026' -A x64 -T v143 '-DMAYA_VERSION=2025' '-DCMAKE_POLICY_VERSION_MINIMUM=3.5'
cmake --build build/m5-average --config Release
cmake -S Maya/plugin/skinToolWeightsCpp -B build/m5-setter -G 'Visual Studio 18 2026' -A x64 -T v143 '-DMAYA_VERSION=2025' '-DCMAKE_POLICY_VERSION_MINIMUM=3.5'
cmake --build build/m5-setter --config Release
```

Outputs: build/m5-average/projects/Release/skinCommands.mll and
build/m5-setter/Release/skinCommands.mll. Test them in separate processes.
Only the validated primary Maya2025 binary is copied into the runtime tree;
other ABI/platform binaries stay unchanged. smoothBrushRodCpp's source/build
configuration is retained; its C++11/FindMaya/build provenance remains a separate
engine audit boundary, and no replacement brush binary is generated here.

## Reproducible package

Use Python3.9+ for release tooling (independent of Maya runtime minimum), Git and
the standard library. Importing packageCreator is read-only; run its CLI explicitly:

```powershell
python -X utf8 packageCreator.py --output package/SkinningTools.zip
```

Build from a reviewed checkout with intended files tracked/staged and a clean
production tree. The builder reads tracked working-tree bytes through an explicit
runtime/asset allowlist. It excludes tests, build/cache directories, local settings,
scene/weight-data files and untracked content. Include new runtime files in Git
before building. It includes the primary native plugin, all retained runtime/native
source assets and existing license notices; no subprocess 7z dependency remains.
Maya/tooltips GIFs travel inside the main ZIP, avoiding a separate release download.

Archive paths/order, timestamps and permissions are fixed. Version is read from
the UI source; --version X.Y.Z stamps only packaged UI/installer copies. Debug is
disabled only in packaged utils.py. Source files are never rewritten or moved.
The builder refuses to overwrite an existing archive. Same input bytes on the same
Python/zlib toolchain give byte-identical ZIPs; different Git newline conversions
or compressors are not claimed to give identical bytes.

SkinningTools/package-manifest.json records SHA256 for every runtime package file,
its format and version. It detects accidental corruption; it is not a signed trust
or authenticity guarantee. THIRD_PARTY.md records notice/license gaps. Review these
before external distribution; this milestone performs no publication or upload.

## Installation and recovery

Extract the ZIP and drag dragDropInstall.mel into Maya as before. Restart Maya after
installation; this does not hot-reload loaded Python modules/native DLLs. The
existing installer options/functions remain. Its install method delegates to
installCore.installPackage:

1. Validate required files and a release manifest when present. Raw developer trees
   without a manifest use source/staged byte comparison instead.
2. Copy into a unique staging directory alongside the destination, verify hashes,
   copy selected old settings/tooltips, and download optional tooltip content there.
3. Verify core files were not changed during optional preparation, rename the old
   installation to a unique backup, and promote the staged replacement on the same
   volume. Verify installed bytes before deleting any requested overwrite backup.
4. On failure, remove the new promoted tree if necessary and restore the old one.
   A persistent filesystem failure during rollback reports the surviving old backup
   path. A successful backup-mode install always retains its unique backup.

Source packages/settings/tooltips are copied, never consumed. Optional download
failure warns and installation may continue with preserved old tooltips. Archive
extraction accepts GIF leaf names only. Downloads were mocked/not contacted in tests.
The source/destination must not overlap, and package links are rejected.

Recovery covers caught operation failures, not a machine crash/power loss between
renames. In that case, recover the unique Backup_SkinningTools-* sibling manually.
Concurrent installers/active Maya DLL locks are not certified; filesystem errors
propagate. No live installation or user scene is exercised in validation.

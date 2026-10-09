# M3 local build and verification recipe

Run from C:/dev/SkinningTools in PowerShell. Builds remain under ignored build/.
No install target is invoked. The existing projects retain their C++11 policy and
minimum Maya/Python support; no global compiler/environment settings are changed.

```powershell
cmake -S Maya/plugin/averageWeightPerryCpp -B build/m3-average-fixed -G 'Visual Studio 18 2026' -A x64 -T v143 '-DMAYA_VERSION=2025' '-DCMAKE_POLICY_VERSION_MINIMUM=3.5'
cmake --build build/m3-average-fixed --config Release
cmake -S Maya/plugin/skinToolWeightsCpp -B build/m3-setter-fixed -G 'Visual Studio 18 2026' -A x64 -T v143 '-DMAYA_VERSION=2025' '-DCMAKE_POLICY_VERSION_MINIMUM=3.5'
cmake --build build/m3-setter-fixed --config Release
python -m unittest discover -s tests -t . -v
$env:SKINNINGTOOLS_NATIVE_TEST_PLUGIN = 'C:\dev\SkinningTools\Maya\plugin\averageWeightPerryCpp\comp\Maya2025\plug-ins\skinCommands.mll'
& 'C:\Program Files\Autodesk\Maya2025\bin\mayapy.exe' tests/run_maya.py
$env:SKINNINGTOOLS_NATIVE_TEST_PLUGIN = 'C:\dev\SkinningTools\build\m3-setter-fixed\Release\smooth_brush_maya.mll'
$env:SKINNINGTOOLS_MAYA_TEST_NAME = 'tests.test_maya_smoothing.NativeSetterTests'
& 'C:\Program Files\Autodesk\Maya2025\bin\mayapy.exe' tests/run_maya.py
Remove-Item Env:SKINNINGTOOLS_NATIVE_TEST_PLUGIN
Remove-Item Env:SKINNINGTOOLS_MAYA_TEST_NAME
```

Primary output: build/m3-average-fixed/projects/Release/skinCommands.mll.
It registers AverageVtxWeight and SkinWeights. Delivered Maya2025 binary is an
exact byte copy; see M3_REPORT.md for SHA256. Duplicate setter output:
build/m3-setter-fixed/Release/smooth_brush_maya.mll, SHA256
`65A16742CCA5359C6EB0D53E4E33F4B5D81A4F9ED514E2A4A1DB7A3AD0F07850`.
It registers only SkinWeights, despite the target's name. Load the two plugins in
different processes because both register SkinWeights. Neither is the independent
smoothBrushRodCpp engine. CMake project naming/loader consolidation remains M4/M5.

The isolated baseline build used the original parent sources before editing,
build/m3-average-baseline-vs18, the same Maya SDK and default MSVC 19.51. Its runtime
evidence is in M3_BASELINE_RESULTS.txt. Initial configuration mistakes (unavailable
VS17 generator and unquoted PowerShell decimal CMake argument) were corrected to
the available generator and quoted cache values. Compilation repairs included
explicit MDagPath/helper includes and respecting the C++ API's mutable array
signatures. No host compiler limitation is concealed as a skipped correctness test.

tests/run_maya.py accepts an optional SKINNINGTOOLS_MAYA_TEST_NAME to run one case
in its own process. M3 invalid-argument final runs use this to isolate native cases.
SKINNINGTOOLS_NATIVE_TEST_PLUGIN explicitly selects the binary being validated;
without it, new native regression classes skip rather than certifying an arbitrary
old-host binary. The existing smoke classes continue to use the matching bundled
binary by default. Python brush regressions still run in standalone without the
native override. All fixtures retain the batch guard and private cleanup rules.

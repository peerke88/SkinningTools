# Development change ledger

## M0 — 2026-10-09 — local delivery, awaiting acceptance

Baseline: `2d712f9dd844112d7457324b85e6c351e60f66b1`.
Branch: `codex/skinningtools-reliability`. Commit: use
`git log -1 --format=%H codex/skinningtools-reliability` for the local delivery hash.
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

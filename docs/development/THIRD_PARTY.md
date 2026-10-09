# Bundled dependency and notice audit — M5

This is an inventory of repository evidence, not a legal clearance or an assurance
about remote service availability. No dependency is upgraded, removed or downloaded.
The release allowlist retains ThirdParty files, native source/header trees and their
existing notices. This document is included as SkinningTools/THIRD_PARTY.md.

| Component | Local evidence | Runtime/maintenance observation |
| --- | --- | --- |
| KDTree | ThirdParty/kdtree.py, Matej Drame, version 1r11.1.2010; README says MIT | Active nearest-neighbor helper; standalone full MIT notice not found |
| pyprof2calltree | ThirdParty/pyprof2calltree.py contains full MIT-style grant and authors | Active shared profiler import; notice preserved in source |
| QCacheGrind/Qt/Graphviz | ThirdParty/qcachegrind/readme.txt, README.original, COPYING.txt and LICENSE.LGPL | Windows 32-bit QCacheGrind 0.7.4; COPYING describes GPLv2, Qt LGPLv2.1 and Graphviz EPLv1.0; binaries/notices retained, external executable not run |
| Requests | ThirdParty/requests/__init__.py declares 2.7.0, Apache 2.0 and refers to LICENSE | Active download/translation import; standalone referenced LICENSE file absent; cgi import fails under system Python3.13, imports in Maya2025/Python3.11 |
| urllib3 | Bundled under Requests; __init__.py declares 1.10.4 / MIT | Used by translation/downloads; standalone full MIT notice not found |
| chardet | Bundled under Requests; __init__.py declares 2.3.0 / LGPL2.1-or-later and carries notice | Source retained; standalone LGPL text under this subtree not found |
| six | requests/packages/urllib3/packages/six.py has full MIT-style notice | Embedded compatibility support; source notice retained |
| google_trans_new | Source headers declare LuShan / 1.1.9 | Python3 quote import repaired with Python2 fallback; remote translation service not exercised; standalone license not found |
| Control sliders | UI/ControlSlider/__init__.py carries GPL3-or-later notice and author attribution | Active UI components, retained with source notices |
| Eigen | smoothBrushRodCpp/externals/include/Eigen/src/Core/util/Macros.h declares 3.3.3 and MPL2.0 notice | Native brush headers, retained; per-file notices may differ; full MPL text not found |
| Native toolbox/brush and tool modules | Per-file authors/notices and package __init__.py files | Native source retained, no ownership-based removal justified |

Only two dedicated license/copying files are tracked: qcachegrind/COPYING.txt and
qcachegrind/LICENSE.LGPL. The package selection preserves both byte-for-byte, plus
embedded source notices. Missing referenced full texts and uncertain grants need
upstream/owner review before an external release; no new license grant is inferred.
In particular, README labels alone do not establish the terms of each bundled file.

No remote downloads, translation requests or certificate/service checks were made
in this audit. Old versions and source import compatibility are recorded as observed
maintenance constraints, not evidence of a particular unverified security defect.

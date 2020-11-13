QCacheGrind binary for Windows 32bit
====================================

8-May-2013:

This is a precompiled build of QCacheGrind 0.7.4 - the Qt-only version of KCacheGrind.
(http://kcachegrind.sourceforge.net/html/Home.html)

The latest Windows binaries for KCacheGrind are not readily available, so I decided to build my own copy and make this available.
The source code is distributed under the GPLv2 licence and can be found in the kcachegrind project page in Sourceforge. This software is dynamically linked to Qt 5, and the source for these libraries can be found in the link below.

Please go to the KCacheGrind site for more information on using the tool.


Deploying and running
---------------------

Extract the qcachegrind folder to any location.
Run qcachegrind.exe

You may need to install the MS Visual C++ 2010 Redistributable Package (x86). If qcachegrind does not start, this may be the issue.
Download and install this package from http://www.microsoft.com/en-us/download/details.aspx?id=5555

This build should run on:
Windows 7 x86, x64
Windows XP SP3 (not confirmed)
Windows Vista SP2 (not confirmed)


Build notes
-----------

KCachegrind 0.7.4 (05-Apr-2013)
dot - Graphviz 2.30.1 (15-Mar-2013)
Qt 5.02 (10-Apr-2013)

This was compiled in Qt 5 + MSVC2010 on 08-May-2013 
Bundled with the executable are the required QT libraries and the dot tool from the Graphviz windows distribution (http://www.graphviz.org/)

This has been tested in Windows 7 SP1 for x86 and x64. Please post feedback on other platforms.


Licences
--------

kcachegrind: GPLv2 (http://kcachegrind.sourceforge.net/html/License.html)
Qt: LGPL 2.1 (http://qt-project.org/doc/qt-5.0/qtdoc/lgpl.html)
dot: EPL (http://www.graphviz.org/License.php)


Source links
------------

qcachegrind 
http://kcachegrind.sourceforge.net/html/Home.html

dot.exe 
http://www.graphviz.org/

Qt 
http://qt.digia.com/

MSVC2010 Redistribution Package (x86)
http://www.microsoft.com/en-us/download/details.aspx?id=5555
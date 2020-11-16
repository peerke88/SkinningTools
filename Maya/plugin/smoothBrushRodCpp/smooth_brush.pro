###############################################################################
#warning("Please use cmake instead of the .pro to compile")
# This file should not be processed by qmake, it is solely used as a
# convenient way to work with qt creator IDE.
# Build is handle exclusively with CMake please go to the CMakeLists.txt file
# to change build configuration
###############################################################################
TARGET = smooth_brush_maya

include(./smooth_brush.pri)

win32:DEFINES += "_WIN32="
win32:INCLUDEPATH += "C:\Program Files\Autodesk\Maya2019\include"
DEFINES += "OPENMAYA_EXPORT="
DEFINES += "OPENMAYAUI_EXPORT="
DEFINES += "OPENMAYARENDER_EXPORT="
DEFINES += "OPENMAYAANIM_EXPORT="
DEFINES += "FND_EXPORT="
DEFINES += "MAYA_API_VERSION=2018000"

# Modules
SOURCES     += $${SMOOTH_BRUSH_FILES}
INCLUDEPATH += $${SMOOTH_BRUSH_INCLUDEPATH}



DEFINES += "TBX_MAYA_ENABLE_USING_NAMESPACE_TBX_MAYA"
DEFINES += "TBX_MESH_ENABLE_USING_NAMESPACE_TBX_MESH"
DEFINES += "TBX_ENABLE_USING_NAMESPACE_TBX"

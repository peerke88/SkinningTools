# Maya finder module
# This module searches for maya libraries and header files so we could use MAYA API classes.
# This module has been tested in Windows 7/10, OS X Sierra, Linux Cent OS successfully

#Output variables

# MAYA_LIBRARY_DIR - a path to "{Maya installation folder}/lib"
# MAYA_INCLUDE_DIR - a path to header files in devkit folder
# MAYA_LIBRARIES - individually defined libraries

find_package(OpenGL REQUIRED)

set(CMAKE_POSITION_INDEPENDENT_CODE ON)

set(MAYA_VERSION 2015 CACHE STRING "Maya Version") #can be overriden in a terminal by typing: -DMAYA_VERSION = 2016
set(MAYA_INSTALL_PATH_SUFFIX "")
set(MAYA_LIB_DIR_NAME "lib")
set(MAYA_INCLUDE_DIR_NAME "include")
set(MAYA_COMPILE_DEFINITIONS "REQUIRE_IOSTREAM; _BOOL")
set(MAYA_TARGET_TYPE LIBRARY)

# Platform specific values
if (WIN32)

	#Maya Windows
    set(MAYA_INSTALL_PATH "C:/Program Files/Autodesk") #maya install folder
    set(MAYA_PLUGIN_EXTENSION ".mll") #plugin extension
    set(OPENMAYA OpenMaya.lib)
    #Compiler
	set(MAYA_COMPILE_DEFINITIONS "${MAYA_COMPILE_DEFINITIONS};NT_PLUGIN;_MBCS;_AFXDLL") #preprocessor definitions
	set(MAYA_TARGET_TYPE RUNTIME)

elseif(APPLE)

    # Apple Maya
    set(MAYA_INSTALL_PATH /Applications/Autodesk)
    set(MAYA_LIB_DIR_NAME "Maya.app/Contents/MacOS")
    set(MAYA_PLUGIN_EXTENSION ".bundle")
    set(OPENMAYA libOpenMaya.dylib)
    #Compiler
	set(MAYA_COMPILE_DEFINITIONS "${MAYA_COMPILE_DEFINITIONS};OSMac_;_DARWIN;MAC_PLUGIN;OSMac_MachO;OSMacOSX_;CC_GNU_;_LANGUAGE_C_PLUS_PLUS")
    
else()

	# Maya Linux
    set(MAYA_INSTALL_PATH /usr/autodesk)
    set(MAYA_PLUGIN_EXTENSION ".so")
    set(OPENMAYA libOpenMaya.so)
    if(MAYA_VERSION LESS 2016)
        SET(MAYA_INSTALL_PATH_SUFFIX -x64)
    endif()
    #compiler
    set(MAYA_COMPILE_DEFINITIONS "${MAYA_COMPILE_DEFINITIONS};LINUX;_LINUX;LINUX_64") 
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fPIC")  #compiler flags += -fPIC
    
endif()

#Maya install path
set(MAYA_INSTALL_PATH ${MAYA_INSTALL_PATH} CACHE STRING "Maya installation path")
set(MAYA_LOCATION ${MAYA_INSTALL_PATH}/maya${MAYA_VERSION}${MAYA_INSTALL_PATH_SUFFIX}) 
message("[Log] Maya installation location: ${MAYA_LOCATION}")

#Find headers in SDK folder and return a dirrectory
find_path(  MAYA_INCLUDE_DIR    maya/MFn.h
            PATHS               ${MAYA_LOCATION} 
            PATH_SUFFIXES       "${MAYA_INCLUDE_DIR_NAME}/"
            DOC                 "Maya Include Path"
)
message("[Log] Maya include location:  ${MAYA_INCLUDE_DIR}")


#Find libs in maya installation folder and return a dirrectory
find_path(  MAYA_LIBRARY_DIR    ${OPENMAYA}
            PATHS               ${MAYA_LOCATION}
            PATH_SUFFIXES       "${MAYA_LIB_DIR_NAME}/"
            DOC                 "Maya Library Path"
)
message("[Log] Maya libs location: ${MAYA_LIBRARY_DIR}")

#Find maya individual libs
foreach(MAYA_LIB OpenMaya OpenMayaAnim OpenMayaFX OpenMayaRender OpenMayaUI Foundation)
	find_library(MAYA_${MAYA_LIB}_LIBRARY NAMES ${MAYA_LIB} PATHS ${MAYA_LIBRARY_DIR} NO_DEFAULT_PATH)
	set(MAYA_LIBRARIES ${MAYA_LIBRARIES} ${MAYA_${MAYA_LIB}_LIBRARY}) #append a lib to MAYA_LIBRARIES list
endforeach()

set(MAYA_LIBRARIES ${MAYA_LIBRARIES} ${OPENGL_LIBRARIES})

#Specifies "Clang" compiler specific flags for APPLE OS
#-std=c++0x    - tells a compiler to use C++ 11 standard
#-stdlib=libstdc++   - tells "Clang" to use a standard C++ library that comes with GCC
if (APPLE AND ${CMAKE_CXX_COMPILER_ID} MATCHES "Clang") 
    set(MAYA_CXX_FLAGS "-std=c++0x -stdlib=libstdc++ ")
endif()

#show error if MAYA_INCLUDE_DIR, MAYA_LIBRARY_DIR and MAYA_LIBRARIES are not defined
include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(Maya DEFAULT_MSG MAYA_INCLUDE_DIR MAYA_LIBRARY_DIR MAYA_LIBRARIES )

#Set compiler options for each passed it project (_target)
function(MAYA_PLUGIN _target)

    #platform specific preprocessor options
    if (WIN32)
        set_target_properties(${_target} PROPERTIES
            LINK_FLAGS "/export:initializePlugin /export:uninitializePlugin"
            COMPILE_FLAGS "/MD"
        )
    endif()

    #common options
    set_target_properties(${_target} PROPERTIES
        COMPILE_DEFINITIONS "${MAYA_COMPILE_DEFINITIONS}"
        PREFIX ""
        SUFFIX ${MAYA_PLUGIN_EXTENSION}
    )


endfunction()



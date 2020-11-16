cmake_minimum_required(VERSION 3.1)
project(smooth_brush_maya)


add_definitions( -DTBX_MAYA_ENABLE_USING_NAMESPACE_TBX_MAYA )
add_definitions( -DTBX_MESH_ENABLE_USING_NAMESPACE_TBX_MESH )
add_definitions( -DTBX_ENABLE_USING_NAMESPACE_TBX )
  
#-------------------------------------------------------------------------------
# setup third party libs (Eigen)

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/externals/include)

#-------------------------------------------------------------------------------
# Setup Maya version

if(NOT DEFINED MAYA_VERSION)
    message("MAYA_VERSION not defined, set to default value")
    set(MAYA_VERSION 2020)
endif()

#-------------------------------------------------------------------------------
# find various third party libs

find_package(OpenGL REQUIRED)

# Add path to our custom FindXXX.cmake routines (to load third party libs)
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${CMAKE_CURRENT_SOURCE_DIR})

#-------------------------------------------------------------------------------
# Configure project's libraries

if (CMAKE_BUILD_TYPE STREQUAL "Debug")
    set(build_dir  "build/debug")
    set(lib_dir    "lib/debug"  )
    set(build_type "debug"      )
endif()

if (CMAKE_BUILD_TYPE STREQUAL "Release")
    set(build_dir  "build/release")
    set(lib_dir    "lib/release"  )
    set(build_type "release"      )
endif()

#-------------------------------------------------------------------------------

include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}/src
)

set(SRC_ROOT ${CMAKE_CURRENT_SOURCE_DIR}/src)
# List of cpu sources
file(GLOB_RECURSE host_sources ${SRC_ROOT}/*.cpp )
# List of headers
file(GLOB_RECURSE host_headers ${SRC_ROOT}/*.hpp ${SRC_ROOT}/*.h ${SRC_ROOT}/*.inl )

#-------------------------------------------------------------------------------
# FLAGS
#-------------------------------------------------------------------------------

if(DEFINED CMAKE_COMPILER_IS_GNUCC)
    # Enable C++11
    SET( CMAKE_CXX_FLAGS  "${CMAKE_CXX_FLAGS} -std=c++0x" )
endif()

# Anything other than -D or /D is not passed along to nvcc.
# works for any compiler
if(MSVC)
    ADD_DEFINITIONS(-DNOMINMAX)
    ADD_DEFINITIONS(/D _CRT_SECURE_NO_WARNINGS)
    #ADD_DEFINITIONS(/arch:SSE3)
    #ADD_DEFINITIONS(/arch:MMX)
    ADD_DEFINITIONS(/FS)

    ADD_DEFINITIONS(
        -D_USRDLL
        -DNT_PLUGIN
        -D_SECURE_SCL=0
        -D_SECURE_SCL_THROWS=0
        -D_SECURE_SCL_DEPRECATE=0
        -D_CRT_SECURE_NO_DEPRECATE
        -DREQUIRE_IOSTREAM
        -DAW_NEW_IOSTREAMS
        -DBits64_
    )
elseif(MINGW)
    set(MISC_LINK_FLAGS -static-libgcc -static-libstdc++)
else()
    set(CMAKE_CXX_FLAGS -Wall)
endif(MSVC)

# END FLAGS --------------------------------------------------------------------

#-------------------------------------------------------------------------------
# Build static libraries
#-------------------------------------------------------------------------------

# Set the name of our final ".mll" plugin file
set(MAYA_PLUGIN_BIN_NAME "${PROJECT_NAME}")
set(PROJECT_NAME "${PROJECT_NAME}${MAYA_VERSION}")


if(build_type STREQUAL "debug")
    set(PROJECT_NAME "${PROJECT_NAME}_debug")
    set(MAYA_PLUGIN_BIN_NAME "${MAYA_PLUGIN_BIN_NAME}_debug")
endif()


#-------------
# setup Maya

find_package(MAYA REQUIRED)
include_directories(${MAYA_INCLUDE_DIRS})
link_directories(${MAYA_LIBRARY_DIR})
# -------------

ADD_LIBRARY(${PROJECT_NAME} SHARED ${host_sources} ${host_headers})

# set output directory and name of our plugin file:
set_target_properties( ${PROJECT_NAME}
    PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/lib/maya${MAYA_VERSION}/${build_type}"
    RUNTIME_OUTPUT_NAME ${MAYA_PLUGIN_BIN_NAME}
)

TARGET_LINK_LIBRARIES(${PROJECT_NAME}
    ${MAYA_LIBRARIES}        
    ${MISC_LINK_FLAGS}    
    ${OPENGL_LIBRARIES}
)

MAYA_PLUGIN(${PROJECT_NAME})

#END BUILD LIBRARIES -----------------------------------------------------------


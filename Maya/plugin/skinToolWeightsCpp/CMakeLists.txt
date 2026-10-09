cmake_minimum_required(VERSION 3.6) 

project(smooth_brush_maya)

# this is required by osx, might be deprecated in the future
set(CMAKE_MACOSX_RPATH 1)
if(NOT DEFINED MAYA_VERSION)
    message(FATAL_ERROR "Specify -DMAYA_VERSION=<year> for the target SDK/ABI")
endif()
set(_SKINNINGTOOLS_STANDARD 11)
if(MAYA_VERSION GREATER_EQUAL 2022)
    set(_SKINNINGTOOLS_STANDARD 17)
endif()
set(CMAKE_CXX_STANDARD ${_SKINNINGTOOLS_STANDARD} CACHE STRING "C++ standard for the selected Maya SDK")
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE TRUE)

if(POLICY CMP0072)
    # force the application to take new gl functions instead of legacy
    cmake_policy(SET CMP0072 NEW)
endif()

set(CMAKE_SUPPRESS_REGENERATION true)

if(CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)
    set(CMAKE_INSTALL_PREFIX "${CMAKE_CURRENT_SOURCE_DIR}/comp/Maya${MAYA_VERSION}" CACHE PATH "Setter package destination" FORCE)
endif()

set(CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/../averageWeightPerryCpp/modules" ${CMAKE_MODULE_PATH})

# setup third party libs (Eigen)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/externals/include)

#-------------------------------------------------------------------------------
set(SOURCE_FILES projects/main.cpp projects/skinweights.cpp projects/skinweights.h projects/utils.hpp)

add_definitions( -DTBX_MAYA_ENABLE_USING_NAMESPACE_TBX_MAYA )
add_definitions( -DTBX_MESH_ENABLE_USING_NAMESPACE_TBX_MESH )
add_definitions( -DTBX_ENABLE_USING_NAMESPACE_TBX )

find_package(Maya REQUIRED)
include_directories(${MAYA_INCLUDE_DIR})
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/src)

link_directories(${MAYA_LIBRARY_DIR})

add_library(${PROJECT_NAME} SHARED ${SOURCE_FILES})
target_link_libraries(${PROJECT_NAME} ${MAYA_LIBRARIES})

MAYA_PLUGIN(${PROJECT_NAME})
# Keep the historical target name; its artifact owns SkinWeights, not SBR_brush.
set_target_properties(${PROJECT_NAME} PROPERTIES OUTPUT_NAME skinCommands)

#-------------------------------------------------------------------------------

set(build_type "release" )
if (CMAKE_BUILD_TYPE STREQUAL "Debug")
    set(build_type "debug" )
endif()

if (CMAKE_BUILD_TYPE STREQUAL "Release")       
    set(build_type "release" )
endif()

install(TARGETS ${PROJECT_NAME} ${MAYA_TARGET_TYPE} DESTINATION plug-ins)
#-------------------------------------------------------------------------------


add_definitions(-D_BOOL -DREQUIRE_IOSTREAM -DMAYA_VERSION=${MAYA_VERSION} )


if (APPLE)
   add_definitions(-DOSMac_ -DMAC_PLUGIN)
endif()
